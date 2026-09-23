from __future__ import annotations

import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch
from urllib.request import urlopen

from src.cockpit.desktop_launcher import (
    CockpitLaunchError,
    choose_freshness_ref,
    is_repo_root,
    launch_edge_app,
    generate_projection_for_launch,
    _ref_exists,
    _subprocess_creationflags,
    resolve_repo_root,
    run_cockpit,
    start_loopback_server,
)


def make_repo(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
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

    def test_windows_creationflags_suppress_child_console(self) -> None:
        with (
            patch("src.cockpit.desktop_launcher.os.name", "nt"),
            patch.object(
                subprocess,
                "CREATE_NO_WINDOW",
                0x08000000,
                create=True,
            ),
        ):
            self.assertEqual(_subprocess_creationflags(), 0x08000000)

    def test_ref_probe_passes_creationflags_to_git(self) -> None:
        completed = Mock(returncode=0)
        with (
            patch(
                "src.cockpit.desktop_launcher._subprocess_creationflags",
                return_value=0x08000000,
            ),
            patch(
                "src.cockpit.desktop_launcher.subprocess.run",
                return_value=completed,
            ) as run,
        ):
            self.assertTrue(_ref_exists(Path("C:/repo"), "main"))

        self.assertEqual(run.call_args.kwargs["creationflags"], 0x08000000)

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

    def test_launch_generation_materializes_semantic_address_temporal_and_distinction_projections(self) -> None:
        repo = Path("C:/synthetic/repo")
        semantic_model = {"repository_state": {"source_commit": "a" * 40}}
        with (
            patch(
                "src.cockpit.generate_projection.generate_projection",
                return_value=semantic_model,
            ) as semantic,
            patch(
                "src.cockpit.repository_address_fabric.generate_repository_address_fabric",
                return_value={"source_commit": "a" * 40},
            ) as fabric,
            patch(
                "src.cockpit.repository_temporal_lineage.generate_repository_temporal_lineage",
                return_value={"source_commit": "a" * 40},
            ) as temporal,
            patch(
                "src.cockpit.typed_distinction_registry.generate_typed_distinction_registry_projection",
                return_value={"counts": {"admitted_bounded": 1}},
            ) as distinctions,
        ):
            result = generate_projection_for_launch(
                repo,
                source_ref="HEAD",
                freshness_ref="origin/main",
            )

        self.assertEqual(result, semantic_model)
        self.assertEqual(
            semantic.call_args.kwargs["output"],
            repo / "generated" / "cockpit_projection.json",
        )
        self.assertEqual(
            fabric.call_args.kwargs["output"],
            repo / "generated" / "repository_address_fabric.json",
        )
        self.assertEqual(fabric.call_args.kwargs["source_ref"], "HEAD")
        self.assertEqual(
            temporal.call_args.kwargs["output"],
            repo / "generated" / "repository_temporal_lineage.json",
        )
        self.assertEqual(temporal.call_args.kwargs["source_ref"], "HEAD")
        self.assertEqual(
            distinctions.call_args.kwargs["output"],
            repo / "generated" / "typed_distinction_registry_v0.json",
        )
        self.assertEqual(
            distinctions.call_args.kwargs["temporal_lineage"],
            {"source_commit": "a" * 40},
        )

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
