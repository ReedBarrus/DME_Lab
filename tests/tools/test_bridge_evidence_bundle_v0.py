from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "bridge_evidence_bundle_v0.py"


def load_module():
    spec = importlib.util.spec_from_file_location("bridge_evidence_bundle_v0", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_label_regex_accepts_bounded_ids():
    m = load_module()
    assert m.LABEL_RE.fullmatch("CELL_002_RUN_A")
    assert m.LABEL_RE.fullmatch("BUNDLE-001")


def test_label_regex_rejects_path_like_labels():
    m = load_module()
    assert not m.LABEL_RE.fullmatch("../EVIDENCE")
    assert not m.LABEL_RE.fullmatch("has spaces")


def test_parse_object_rejects_non_full_text_mode():
    m = load_module()
    item = {
        "label": "EVIDENCE_A",
        "source_ref": "a" * 40,
        "path": "bridge/prompts/example.md",
        "sha256": "b" * 64,
        "mode": "semantic_search",
    }
    try:
        m.parse_object(item, kind="evidence", allowed_prefixes=("bridge/prompts/",))
    except ValueError as e:
        assert "full_text" in str(e)
    else:
        raise AssertionError("expected non-full-text mode rejection")


def test_validate_repo_path_rejects_traversal():
    m = load_module()
    try:
        m.validate_repo_path("bridge/prompts/../secret.txt", ("bridge/prompts/",))
    except ValueError:
        pass
    else:
        raise AssertionError("expected path traversal rejection")
