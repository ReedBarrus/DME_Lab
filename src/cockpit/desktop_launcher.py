from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
from typing import Sequence
import webbrowser


OBSERVER_RELATIVE_PATH = Path("src/cockpit/observer/index.html")
PROJECTION_RELATIVE_PATH = Path("generated/cockpit_projection.json")
CONFIG_FILENAME = "cockpit.json"
APP_NAME = "DME Cockpit"


class CockpitLaunchError(RuntimeError):
    """Raised when the desktop Cockpit cannot establish a safe launch basis."""


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        logging.getLogger(__name__).debug(format, *args)


def config_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / "DME_Lab"
        return Path.home() / "AppData" / "Roaming" / "DME_Lab"
    base = os.environ.get("XDG_CONFIG_HOME")
    if base:
        return Path(base) / "dme_lab"
    return Path.home() / ".config" / "dme_lab"


def config_path() -> Path:
    return config_dir() / CONFIG_FILENAME


def _normalize_path(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def is_repo_root(path: str | Path) -> bool:
    root = _normalize_path(path)
    return (
        (root / ".git").exists()
        and (root / OBSERVER_RELATIVE_PATH).is_file()
        and (root / "src" / "cockpit" / "generate_projection.py").is_file()
    )


def _ancestor_candidates(start: Path) -> list[Path]:
    resolved = start.resolve()
    if resolved.is_file():
        resolved = resolved.parent
    return [resolved, *resolved.parents]


def _load_saved_repo(path: Path | None = None) -> Path | None:
    target = path or config_path()
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    value = payload.get("repo")
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = _normalize_path(value)
    return candidate if is_repo_root(candidate) else None


def _save_repo(repo_root: Path, path: Path | None = None) -> None:
    target = path or config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(
        json.dumps({"repo": str(repo_root)}, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(target)


def _pick_repo_directory() -> Path | None:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        selected = filedialog.askdirectory(
            title="Select the DME_Lab repository",
            mustexist=True,
        )
    finally:
        root.destroy()
    return _normalize_path(selected) if selected else None


def resolve_repo_root(
    explicit: str | Path | None = None,
    *,
    allow_picker: bool = True,
    saved_config_path: Path | None = None,
) -> Path:
    if explicit is not None:
        candidate = _normalize_path(explicit)
        if not is_repo_root(candidate):
            raise CockpitLaunchError(
                f"not a DME_Lab repository root: {candidate}"
            )
        _save_repo(candidate, saved_config_path)
        return candidate

    env_value = os.environ.get("DME_LAB_REPO")
    if env_value:
        candidate = _normalize_path(env_value)
        if is_repo_root(candidate):
            _save_repo(candidate, saved_config_path)
            return candidate

    saved = _load_saved_repo(saved_config_path)
    if saved is not None:
        return saved

    seen: set[Path] = set()
    starts = [Path.cwd()]
    starts.append(Path(sys.executable))
    starts.append(Path(__file__))

    for start in starts:
        for candidate in _ancestor_candidates(start):
            if candidate in seen:
                continue
            seen.add(candidate)
            if is_repo_root(candidate):
                _save_repo(candidate, saved_config_path)
                return candidate

    if allow_picker:
        selected = _pick_repo_directory()
        if selected is not None:
            if not is_repo_root(selected):
                raise CockpitLaunchError(
                    f"selected directory is not a DME_Lab repository root: {selected}"
                )
            _save_repo(selected, saved_config_path)
            return selected

    raise CockpitLaunchError(
        "could not locate DME_Lab; pass --repo, set DME_LAB_REPO, "
        "or select the repository on first launch"
    )


def _ref_exists(repo_root: Path, ref: str) -> bool:
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "rev-parse",
            "--verify",
            f"{ref}^{{commit}}",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.returncode == 0


def choose_freshness_ref(
    repo_root: Path,
    requested: str | None,
) -> str | None:
    if requested and requested != "auto":
        return requested
    for candidate in ("origin/main", "main"):
        if _ref_exists(repo_root, candidate):
            return candidate
    return None


def generate_projection_for_launch(
    repo_root: Path,
    *,
    source_ref: str,
    freshness_ref: str | None,
) -> dict[str, object]:
    from src.cockpit.generate_projection import generate_projection

    return generate_projection(
        repo=repo_root,
        source_ref=source_ref,
        freshness_ref=freshness_ref,
        output=repo_root / PROJECTION_RELATIVE_PATH,
    )


def start_loopback_server(
    repo_root: Path,
    *,
    port: int = 0,
) -> tuple[ThreadingHTTPServer, threading.Thread, str]:
    handler = partial(_QuietHandler, directory=str(repo_root))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(
        target=server.serve_forever,
        name="dme-cockpit-http",
        daemon=True,
    )
    thread.start()
    actual_port = int(server.server_address[1])
    url = f"http://127.0.0.1:{actual_port}/src/cockpit/observer/"
    return server, thread, url


def find_edge() -> Path | None:
    discovered = shutil.which("msedge")
    if discovered:
        return Path(discovered)

    candidates: list[Path] = []
    for env_name in ("PROGRAMFILES(X86)", "PROGRAMFILES", "LOCALAPPDATA"):
        base = os.environ.get(env_name)
        if not base:
            continue
        candidates.append(
            Path(base) / "Microsoft" / "Edge" / "Application" / "msedge.exe"
        )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def launch_edge_app(url: str, *, profile_dir: Path | None = None) -> subprocess.Popen[bytes]:
    edge = find_edge()
    if edge is None:
        raise CockpitLaunchError("Microsoft Edge executable was not found")

    profile = profile_dir or (config_dir() / "edge-profile")
    profile.mkdir(parents=True, exist_ok=True)
    return subprocess.Popen(
        [
            str(edge),
            f"--app={url}",
            f"--user-data-dir={profile}",
            "--no-first-run",
            "--no-default-browser-check",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _show_error(message: str) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox
    except Exception:
        print(f"{APP_NAME}: {message}", file=sys.stderr)
        return

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        messagebox.showerror(APP_NAME, message)
    finally:
        root.destroy()


def run_cockpit(
    *,
    repo: str | Path | None,
    source_ref: str,
    freshness_ref: str | None,
    port: int,
    open_mode: str,
    allow_picker: bool = True,
) -> int:
    repo_root = resolve_repo_root(repo, allow_picker=allow_picker)
    freshness = choose_freshness_ref(repo_root, freshness_ref)

    # Projection generation happens before a server exists. The generator itself
    # deletes stale output on failure, so a failed launch cannot silently fall
    # back to an older projection.
    generate_projection_for_launch(
        repo_root,
        source_ref=source_ref,
        freshness_ref=freshness,
    )

    server, thread, url = start_loopback_server(repo_root, port=port)
    try:
        if open_mode == "edge-app":
            process = launch_edge_app(url)
            process.wait()
            return 0

        if open_mode == "browser":
            if not webbrowser.open(url, new=1):
                raise CockpitLaunchError(f"browser launch failed; open {url}")
            try:
                while thread.is_alive():
                    thread.join(timeout=1.0)
            except KeyboardInterrupt:
                return 0
            return 0

        if open_mode == "none":
            print(url)
            try:
                while thread.is_alive():
                    thread.join(timeout=1.0)
            except KeyboardInterrupt:
                return 0
            return 0

        raise CockpitLaunchError(f"unknown open mode: {open_mode}")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5.0)


def _default_open_mode() -> str:
    return "edge-app" if os.name == "nt" else "browser"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate and launch the read-only DME Cockpit from an exact committed source."
    )
    parser.add_argument("--repo", default=None, help="DME_Lab repository root")
    parser.add_argument(
        "--source-ref",
        default="HEAD",
        help="committed source ref to project; default: HEAD",
    )
    parser.add_argument(
        "--freshness-ref",
        default="auto",
        help=(
            "locally available comparison ref; 'auto' prefers origin/main then main; "
            "no network fetch is performed"
        ),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="loopback port; 0 chooses an available ephemeral port",
    )
    parser.add_argument(
        "--open-mode",
        choices=("edge-app", "browser", "none"),
        default=_default_open_mode(),
        help="window mode; Windows defaults to Edge app mode",
    )
    parser.add_argument(
        "--no-picker",
        action="store_true",
        help="fail instead of opening a first-run repository chooser",
    )
    args = parser.parse_args(argv)

    try:
        return run_cockpit(
            repo=args.repo,
            source_ref=args.source_ref,
            freshness_ref=args.freshness_ref,
            port=args.port,
            open_mode=args.open_mode,
            allow_picker=not args.no_picker,
        )
    except Exception as exc:
        _show_error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
