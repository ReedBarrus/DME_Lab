#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_TARGET = "src/home/home_capture_v0/server.py"
TRACE_PATH = Path("traces/admission_port_v0.jsonl")

@dataclass(frozen=True)
class Grant:
    operator: str
    object: str

@dataclass
class Cursor:
    task_id: str = "ADMISSION-PORT-001"
    pressure: str = "establish exact SCHEMA_VERSION"
    pressure_state: str = "OPEN"
    basis: str = "current repository source"
    authority: tuple[Grant, ...] = field(default_factory=lambda: (
        Grant("repo.grep:v1", DEFAULT_TARGET),
        Grant("repo.read_full:v1", DEFAULT_TARGET),
    ))

class AdmissionPort:
    def __init__(self, root: Path, cursor: Cursor | None = None,
                 full_read_limit_bytes: int = 8_000,
                 trace_path: Path = TRACE_PATH):
        self.root = root.resolve()
        self.cursor = cursor or Cursor()
        self.full_read_limit_bytes = full_read_limit_bytes
        self.trace_path = trace_path
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)

    def is_authorized(self, operator: str, obj: str) -> bool:
        return any(g.operator == operator and g.object == obj for g in self.cursor.authority)

    def capability_available(self, operator: str) -> bool:
        return operator in {"repo.grep:v1", "repo.read_full:v1", "repo.list:v1"}

    def resource_state(self, operator: str, obj: str) -> tuple[str, str | None]:
        if operator == "repo.read_full:v1":
            path = self._safe_path(obj)
            if not path.exists():
                return "BLOCKED", "OBJECT_NOT_FOUND"
            if path.stat().st_size > self.full_read_limit_bytes:
                return "BLOCKED", "FULL_READ_EXCEEDS_BUDGET"
        return "AVAILABLE", None

    def handle(self, proposal: dict[str, Any]) -> dict[str, Any]:
        proposal_id = self._id("proposal")
        operator = str(proposal.get("operator", ""))
        obj = str(proposal.get("object", ""))
        args = proposal.get("args") or {}

        self._record({"kind":"PROPOSED_TRANSITION","record_id":proposal_id,
                      "task_id":self.cursor.task_id,"pressure_state":self.cursor.pressure_state,
                      "operator":operator,"object":obj,"args":args})

        if self.cursor.pressure_state == "RESOLVED":
            return self._reject(proposal_id, operator, obj, "PRESSURE_RESOLVED",
                                "Current pressure is already RESOLVED; no further repository action is admitted.")

        if not self.capability_available(operator):
            return self._reject(proposal_id, operator, obj, "CAPABILITY_UNAVAILABLE",
                                "No adapter implements this canonical operator.")

        if not self.is_authorized(operator, obj):
            return self._reject(proposal_id, operator, obj, "MISSING_AUTHORITY",
                                "The proposal is outside the exact current grant.")

        resource_state, resource_reason = self.resource_state(operator, obj)
        if resource_state != "AVAILABLE":
            return self._reject(proposal_id, operator, obj, resource_reason or "RESOURCE_BLOCKED",
                                "The action is authorized and implemented, but current resources block execution.")

        admission_id = self._id("admission")
        self._record({"kind":"ADMISSION_DECISION","record_id":admission_id,
                      "proposal_id":proposal_id,"decision":"ADMIT","operator":operator,
                      "object":obj,"pressure_state":self.cursor.pressure_state})

        result = self._execute(operator, obj, args)
        execution_id = self._id("execution")
        self._record({"kind":"EXECUTED_TRANSITION","record_id":execution_id,
                      "proposal_id":proposal_id,"admission_id":admission_id,
                      "operator":operator,"object":obj,"result":result})

        if operator == "repo.grep:v1" and obj == DEFAULT_TARGET and str(args.get("pattern", "")) == "SCHEMA_VERSION" and result.get("matches"):
            exact = None
            for match in result["matches"]:
                m = re.search(r"\bSCHEMA_VERSION\s*=\s*(\d+)\b", match["text"])
                if m:
                    exact = int(m.group(1)); break
            if exact is not None:
                self.cursor.pressure_state = "RESOLVED"
                pressure_record = {"kind":"PRESSURE_TRANSITION","record_id":self._id("pressure"),
                                   "from":"OPEN","to":"RESOLVED",
                                   "evidence":{"object":obj,"operator":operator,"value":exact}}
                self._record(pressure_record)
                result["pressure_transition"] = pressure_record

        return {"event":"ACTION_EXECUTED","recorded":True,"proposal_id":proposal_id,
                "admission_id":admission_id,"execution_id":execution_id,
                "operator":operator,"object":obj,"pressure_state":self.cursor.pressure_state,
                "result":result}

    def _execute(self, operator: str, obj: str, args: dict[str, Any]) -> dict[str, Any]:
        path = self._safe_path(obj)
        if operator == "repo.grep:v1":
            pattern = str(args.get("pattern", ""))
            if not pattern:
                return {"ok":False,"error":"MISSING_PATTERN"}
            matches = []
            with path.open("r", encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    if pattern in line:
                        matches.append({"line":lineno,"text":line.rstrip("\n")})
            return {"ok":True,"matches":matches}
        if operator == "repo.read_full:v1":
            return {"ok":True,"content":path.read_text(encoding="utf-8")}
        if operator == "repo.list:v1":
            return {"ok":True,"entries":sorted(p.name for p in path.iterdir())}
        return {"ok":False,"error":"NO_ADAPTER"}

    def _reject(self, proposal_id: str, operator: str, obj: str,
                reason: str, explanation: str) -> dict[str, Any]:
        rejection_id = self._id("rejection")
        self._record({"kind":"ADMISSION_DECISION","record_id":rejection_id,
                      "proposal_id":proposal_id,"decision":"REJECT","reason":reason,
                      "operator":operator,"object":obj,"pressure_state":self.cursor.pressure_state,
                      "world_changed":False})
        return {"event":"ACTION_REJECTED","recorded":True,
                "witness_record_id":rejection_id,"reason":reason,
                "explanation":explanation,"operator":operator,"object":obj,
                "pressure_state":self.cursor.pressure_state,"world_changed":False}

    def _record(self, payload: dict[str, Any]) -> None:
        envelope = {"ts_unix_ns":time.time_ns(), **payload}
        canonical = json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode()
        envelope["sha256"] = hashlib.sha256(canonical).hexdigest()
        with self.trace_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(envelope, sort_keys=True) + "\n")

    def _safe_path(self, rel: str) -> Path:
        candidate = (self.root / rel).resolve()
        candidate.relative_to(self.root)
        return candidate

    @staticmethod
    def _id(prefix: str) -> str:
        return f"{prefix}:{uuid.uuid4()}"

def run_demo(port: AdmissionPort) -> None:
    demo = [
        {"operator":"repo.read_full:v1","object":DEFAULT_TARGET,"args":{}},
        {"operator":"repo.list:v1","object":"src/home","args":{}},
        {"operator":"repo.grep:v1","object":DEFAULT_TARGET,"args":{"pattern":"SCHEMA_VERSION"}},
        {"operator":"repo.list:v1","object":"src/home/home_capture_v0","args":{}},
    ]
    for proposal in demo:
        print(json.dumps({"proposal":proposal}, sort_keys=True))
        print(json.dumps(port.handle(proposal), sort_keys=True))

def run_jsonl(port: AdmissionPort) -> None:
    print(json.dumps({"event":"ADMISSION_PORT_READY","task_id":port.cursor.task_id,
                      "pressure":port.cursor.pressure,"pressure_state":port.cursor.pressure_state,
                      "authority":[g.__dict__ for g in port.cursor.authority],
                      "note":"Paste one JSON proposal per line. Authority cannot be changed through this port."}, sort_keys=True), flush=True)
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw: continue
        try:
            result = port.handle(json.loads(raw))
        except Exception as exc:
            result = {"event":"PORT_ERROR","recorded":False,"error":type(exc).__name__,"message":str(exc)}
        print(json.dumps(result, sort_keys=True), flush=True)

def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal deterministic DME admission membrane.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--full-read-limit-bytes", type=int, default=8_000)
    args = parser.parse_args()
    port = AdmissionPort(Path(args.root), full_read_limit_bytes=args.full_read_limit_bytes)
    run_demo(port) if args.demo else run_jsonl(port)

if __name__ == "__main__":
    main()
