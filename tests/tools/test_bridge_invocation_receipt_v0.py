from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "local_lmstudio_bridge_v0.py"


def load_module():
    spec = importlib.util.spec_from_file_location("local_lmstudio_bridge_v0", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_manifest():
    return {
        "request_id": "RECEIPT_SELF_TEST_001",
        "source_ref": "a" * 40,
        "input_path": "bridge/prompts/test.md",
        "input_sha256": "b" * 64,
        "model": "qwen/qwen3-coder-30b",
    }


def test_receipt_is_exclusive_and_fail_closed():
    m = load_module()
    with tempfile.TemporaryDirectory() as td:
        m.RECEIPT_DIR = Path(td)
        manifest = sample_manifest()
        prompt = b"bounded prompt"

        path = m.write_invocation_receipt(
            manifest,
            "c" * 64,
            prompt,
            "bridge/requests/RECEIPT_SELF_TEST_001.json",
        )
        assert path.exists()

        receipt = json.loads(path.read_text(encoding="utf-8"))
        assert receipt["state"] == "AUTHORIZED_INVOCATION_STARTED"
        assert receipt["automatic_replay_allowed"] is False

        try:
            m.write_invocation_receipt(
                manifest,
                "c" * 64,
                prompt,
                "bridge/requests/RECEIPT_SELF_TEST_001.json",
            )
        except RuntimeError as exc:
            assert "automatic replay denied" in str(exc)
        else:
            raise AssertionError("second receipt creation should fail closed")


def test_explicit_clear_reopens_only_receipt_gate():
    m = load_module()
    with tempfile.TemporaryDirectory() as td:
        m.RECEIPT_DIR = Path(td)
        manifest = sample_manifest()
        prompt = b"bounded prompt"

        m.write_invocation_receipt(
            manifest,
            "c" * 64,
            prompt,
            "bridge/requests/RECEIPT_SELF_TEST_001.json",
        )
        assert m.clear_invocation_receipt("RECEIPT_SELF_TEST_001") is True
        assert m.clear_invocation_receipt("RECEIPT_SELF_TEST_001") is False


if __name__ == "__main__":
    test_receipt_is_exclusive_and_fail_closed()
    test_explicit_clear_reopens_only_receipt_gate()
    print("PASS: bridge invocation receipt V0 primitive tests")
