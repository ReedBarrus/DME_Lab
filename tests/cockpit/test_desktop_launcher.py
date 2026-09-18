from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch
from urllib.request import urlopen

from src.cockpit.desktop_launcher import (
    CockpitLaunchError,
    choose_freshness_ref,
    is_repo_root,
    launch_edge_app,
    resolve_repo_root,
    run_cockpit,
    start_loopback_server,
)


def make_repo(root: Path) -> Path:
    (root / ".git").mkdir()
    (root / "src" / "cockpit" / "observer").mkdir(parents=True)
    (root / "src" / "cockpit" / "observer" / "index.html").write_text(
        "<!doctype html><title>cockpit</title>\n",
        encoding="utf-8",
    )
    (root / "src" / "cockpit" / "generate_projection.py").write_text(
        "# fixture\n",
        encoding="utf-8",
    )
    return root


class DesktopCockpitLauncherTest(unittest.TestCase):
    def test_explicit_repo_is_validated_and_persisted(self) -> None:
        with TemporaryDirectory() as temporary:
            root = make_repo(Path(temporary) / "repo")
            config = Path(temporary) / "config" / "cockpit.json"

            resolved = resolve_repo_root(
                root,
                allow_picker=False,
                saved_config_path=config,
            )

            self.assertEqual(resolved, root.resolve())
            self.assertTrue(is_repo_root(root))
            saved = json.loads(config.read_text(encoding="utf-8"))
            self.assertEqual(saved["repo"], str(root.resolve()))

    def test_explicit_non_repo_fails(self) -> None:
        with TemporaryDirectory() as temporary:
            with self.assertRaises(CockpitLaunchError):
                resolve_repo_root(
                    Path(temporary),
                    allow_picker=False,
                    saved_config_path=Path(temporary) / "config.json",
                )

    def test_auto_freshness_prefers_origin_main_then_main(self) -> None:
        repo = Path(".").resolve()
        with patch(
            "src.cockpit.desktop_launcher._ref_exists",
            side_effect=lambda _repo, ref: ref in {"origin/main", "main"},
        ):
            self.assertEqual(choose_freshness_ref(repo, "auto"), "origin/main")

        with patch(
            "src.cockpit.desktop_launcher._ref_exists",
            side_effect=lambda _repo, ref: ref == "main",
        ):
            self.assertEqual(choose_freshness_ref(repo, "auto"), "main")

        with patch(
            "src.cockpit.desktop_launcher._ref_exists",
            return_value=False,
        ):
            self.assertIsNone(choose_freshness_ref(repo, "auto"))

    def test_explicit_freshness_ref_is_not_rewritten(self) -> None:
        with patch("src.cockpit.desktop_launcher._ref_exists") as exists:
            self.assertEqual(
                choose_freshness_ref(Path(".").resolve(), "release/test"),
                "release/test",
            )
            exists.assert_not_called()

    def test_loopback_server_serves_repo_without_external_bind(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "src" / "cockpit" / "observer"
            target.mkdir(parents=True)
            (target / "index.html").write_text("COCKPIT_FIXTURE\n", encoding="utf-8")

            server, thread, url = start_loopback_server(root)
            try:
                self.assertEqual(server.server_address[0], "127.0.0.1")
                with urlopen(url, timeout=2.0) as response:
                    body = response.read().decode("utf-8")
                self.assertIn("COCKPIT_FIXTURE", body)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5.0)

    def test_projection_failure_prevents_server_start(self) -> None:
        fake_repo = Path("/synthetic/repo")
        with (
            patch(
                "src.cockpit.desktop_launcher.resolve_repo_root",
                return_value=fake_repo,
            ),
            patch(
                "src.cockpit.desktop_launcher.choose_freshness_ref",
                return_value="main",
            ),
            patch(
                "src.cockpit.desktop_launcher.generate_projection_for_launch",
                side_effect=RuntimeError("synthetic projection failure"),
            ),
            patch("src.cockpit.desktop_launcher.start_loopback_server") as start_server,
        ):
            with self.assertRaisesRegex(RuntimeError, "synthetic projection failure"):
                run_cockpit(
                    repo=None,
                    source_ref="HEAD",
                    freshness_ref="auto",
                    port=0,
                    open_mode="none",
                    allow_picker=False,
                )
            start_server.assert_not_called()

    def test_edge_app_uses_dedicated_profile_and_app_mode(self) -> None:
        with TemporaryDirectory() as temporary:
            edge = Path(temporary) / "msedge.exe"
            edge.write_bytes(b"")
            profile = Path(temporary) / "profile"
            process = Mock()

            with (
                patch(
                    "src.cockpit.desktop_launcher.find_edge",
                    return_value=edge,
                ),
                patch(
                    "src.cockpit.desktop_launcher.subprocess.Popen",
                    return_value=process,
                ) as popen,
            ):
                returned = launch_edge_app(
                    "http://127.0.0.1:1234/src/cockpit/observer/",
                    profile_dir=profile,
                )

            self.assertIs(returned, process)
            args = popen.call_args.args[0]
            self.assertIn(
                "--app=http://127.0.0.1:1234/src/cockpit/observer/",
                args,
            )
            self.assertIn(f"--user-data-dir={profile}", args)


if __name__ == "__main__":
    unittest.main()
