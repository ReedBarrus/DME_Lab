from pathlib import Path
from admission_port_v0 import AdmissionPort, DEFAULT_TARGET

def make_repo(tmp: Path) -> None:
    p = tmp / DEFAULT_TARGET
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("x = 1\nSCHEMA_VERSION = 7\n" + ("# pad\n" * 100), encoding="utf-8")

def test_missing_authority_is_witnessed_and_world_unchanged(tmp_path: Path):
    make_repo(tmp_path)
    port = AdmissionPort(root=tmp_path, trace_path=tmp_path / "trace.jsonl")
    result = port.handle({"operator":"repo.list:v1","object":"src/home","args":{}})
    assert result["event"] == "ACTION_REJECTED"
    assert result["reason"] == "MISSING_AUTHORITY"
    assert result["recorded"] is True
    assert result["world_changed"] is False

def test_authorized_resource_block_is_not_authority_failure(tmp_path: Path):
    make_repo(tmp_path)
    port = AdmissionPort(root=tmp_path, full_read_limit_bytes=8, trace_path=tmp_path / "trace.jsonl")
    result = port.handle({"operator":"repo.read_full:v1","object":DEFAULT_TARGET,"args":{}})
    assert result["event"] == "ACTION_REJECTED"
    assert result["reason"] == "FULL_READ_EXCEEDS_BUDGET"

def test_grep_resolves_pressure_and_closes_horizon(tmp_path: Path):
    make_repo(tmp_path)
    port = AdmissionPort(root=tmp_path, trace_path=tmp_path / "trace.jsonl")
    result = port.handle({"operator":"repo.grep:v1","object":DEFAULT_TARGET,"args":{"pattern":"SCHEMA_VERSION"}})
    assert result["event"] == "ACTION_EXECUTED"
    assert result["pressure_state"] == "RESOLVED"
    after = port.handle({"operator":"repo.grep:v1","object":DEFAULT_TARGET,"args":{"pattern":"SCHEMA_VERSION"}})
    assert after["event"] == "ACTION_REJECTED"
    assert after["reason"] == "PRESSURE_RESOLVED"
