#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs" / "candidates" / "carrier_swap_v0"

PAYLOAD = BASE / "CS001_PAYLOAD_v0.txt"
K1 = BASE / "CS001_CELL_K1_v0.txt"
K2 = BASE / "CS001_CELL_K2_v0.txt"

EXPECTED = {
    "payload_sha256": "b9dcb579c2ffe18c4b7cbee029ef2f31e057485c084bf865f90d4466fce73338",
    "payload_bytes": 126,
    "k1_sha256": "3b561986aaa29d92c883dcc7bda037d7e06059e327a4b087d38f1b1d22edaaf2",
    "k1_bytes": 364,
    "k2_sha256": "e02825759fa9a041b85a5941f9f571752d59fa36bc6ed83846bfdb1ad925051f",
    "k2_bytes": 359,
    "header_sha256": "fe3b2b6e0901fb0149d31ca18a26c177985815ba62bb965f39b63058944a6b08",
    "footer_sha256": "20b1d76a75b27456a8f2493e92d219d2289a6dd47c015149cf27535af84189ef",
}

HEADER = b"You are a bounded relation checker.\nUse only the supplied payload.\n\n"
FOOTER = (
    b"\nTASK:\n"
    b"Determine whether RECORDED_STATUS is warranted by STATE under RULE.\n\n"
    b"Return exactly one line:\n"
    b"RESULT: SUPPORTED\n"
    b"or\n"
    b"RESULT: NOT_SUPPORTED\n"
)
K1_OPEN = b"BEGIN_PAYLOAD\n"
K1_CLOSE = b"END_PAYLOAD\n"
K2_OPEN = b"<payload>\n"
K2_CLOSE = b"</payload>\n"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    payload = PAYLOAD.read_bytes()
    k1 = K1.read_bytes()
    k2 = K2.read_bytes()

    assert len(payload) == EXPECTED["payload_bytes"]
    assert digest(payload) == EXPECTED["payload_sha256"]
    assert len(k1) == EXPECTED["k1_bytes"]
    assert digest(k1) == EXPECTED["k1_sha256"]
    assert len(k2) == EXPECTED["k2_bytes"]
    assert digest(k2) == EXPECTED["k2_sha256"]
    assert digest(HEADER) == EXPECTED["header_sha256"]
    assert digest(FOOTER) == EXPECTED["footer_sha256"]

    expected_k1 = HEADER + K1_OPEN + payload + K1_CLOSE + FOOTER
    expected_k2 = HEADER + K2_OPEN + payload + K2_CLOSE + FOOTER

    assert k1 == expected_k1
    assert k2 == expected_k2
    assert k1.count(payload) == 1
    assert k2.count(payload) == 1

    extracted_k1 = k1[len(HEADER + K1_OPEN): -len(K1_CLOSE + FOOTER)]
    extracted_k2 = k2[len(HEADER + K2_OPEN): -len(K2_CLOSE + FOOTER)]

    assert extracted_k1 == payload
    assert extracted_k2 == payload
    assert extracted_k1 == extracted_k2

    print("CS001_DETERMINISTIC_VALIDATION: PASS")
    print(f"payload_sha256={digest(payload)}")
    print(f"k1_sha256={digest(k1)}")
    print(f"k2_sha256={digest(k2)}")
    print(f"payload_bytes={len(payload)}")
    print(f"k1_bytes={len(k1)}")
    print(f"k2_bytes={len(k2)}")


if __name__ == "__main__":
    main()
