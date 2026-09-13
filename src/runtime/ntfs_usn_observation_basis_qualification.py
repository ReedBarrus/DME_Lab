"""One-shot qualification of the frozen NTFS USN observation basis.

This is an experimental fixture, not a generalized Windows observer.  It
performs the two predeclared same-file overwrite arms and retains enough raw
journal, identity, and endpoint evidence to adjudicate only the frozen
operation-category question.
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
from typing import Any, Iterable


EXPERIMENT_ID = "ntfs_usn_observation_basis_qualification_v0"
DEFAULT_TRACE = Path("traces") / f"{EXPERIMENT_ID}.json"
CONTENT_A = b"A" * 4096
CONTENT_B = b"B" * 4096
SOURCE_INFO_POLICY = "SourceInfo == 0"

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_DELETE = 0x00000004
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x00000080
FSCTL_QUERY_USN_JOURNAL = 0x000900F4
FSCTL_READ_USN_JOURNAL = 0x000900BB
USN_REASON_DATA_OVERWRITE = 0x00000001
USN_REASON_CLOSE = 0x80000000
V2_HEADER = struct.Struct("<IHHQQqqIIIIHH")
READ_USN_JOURNAL_DATA_V1 = struct.Struct("<qIIQQQHH4x")


class QualificationError(RuntimeError):
    """A bounded acquisition or invariant failure."""

    def __init__(self, category: str, operation: str, detail: str):
        super().__init__(f"{category}: {operation}: {detail}")
        self.category = category
        self.operation = operation
        self.detail = detail

    def as_dict(self) -> dict[str, str]:
        return {
            "category": self.category,
            "operation": self.operation,
            "detail": self.detail,
        }


class BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("dwFileAttributes", wintypes.DWORD),
        ("ftCreationTime", wintypes.FILETIME),
        ("ftLastAccessTime", wintypes.FILETIME),
        ("ftLastWriteTime", wintypes.FILETIME),
        ("dwVolumeSerialNumber", wintypes.DWORD),
        ("nFileSizeHigh", wintypes.DWORD),
        ("nFileSizeLow", wintypes.DWORD),
        ("nNumberOfLinks", wintypes.DWORD),
        ("nFileIndexHigh", wintypes.DWORD),
        ("nFileIndexLow", wintypes.DWORD),
    ]


def compose_file_id64(high: int, low: int) -> int:
    """Compose the unsigned V2-compatible 64-bit file identity."""

    return ((high & 0xFFFFFFFF) << 32) | (low & 0xFFFFFFFF)


def _u64(value: int) -> dict[str, str]:
    unsigned = value & 0xFFFFFFFFFFFFFFFF
    return {"decimal": str(unsigned), "hex": f"0x{unsigned:016X}"}


def _i64(value: int) -> dict[str, str]:
    return {"decimal": str(value), "hex_unsigned": f"0x{value & 0xFFFFFFFFFFFFFFFF:016X}"}


def reason_names(reason: int) -> list[str]:
    names: list[str] = []
    if reason & USN_REASON_DATA_OVERWRITE:
        names.append("USN_REASON_DATA_OVERWRITE")
    if reason & USN_REASON_CLOSE:
        names.append("USN_REASON_CLOSE")
    return names


def parse_v2_records(payload: bytes) -> tuple[int, list[dict[str, Any]]]:
    """Parse one FSCTL_READ_USN_JOURNAL output buffer.

    The first eight bytes are the continuation USN.  Every following record
    must be a structurally valid USN_RECORD_V2; other major versions are not
    silently skipped.
    """

    if len(payload) < 8:
        raise QualificationError(
            "invalid", "parse read buffer", f"only {len(payload)} bytes returned"
        )
    continuation = struct.unpack_from("<q", payload, 0)[0]
    records: list[dict[str, Any]] = []
    offset = 8
    while offset < len(payload):
        remaining = len(payload) - offset
        if remaining < V2_HEADER.size:
            raise QualificationError(
                "invalid",
                "parse USN record",
                f"{remaining} trailing bytes cannot contain a V2 header",
            )
        values = V2_HEADER.unpack_from(payload, offset)
        (
            record_length,
            major,
            minor,
            file_reference,
            parent_reference,
            usn,
            timestamp,
            reason,
            source_info,
            security_id,
            file_attributes,
            name_length,
            name_offset,
        ) = values
        if major != 2:
            raise QualificationError(
                "invalid", "parse USN record", f"unsupported major version {major}"
            )
        if record_length < V2_HEADER.size or record_length > remaining:
            raise QualificationError(
                "invalid",
                "parse USN record",
                f"invalid RecordLength {record_length} with {remaining} bytes remaining",
            )
        if name_length % 2 or name_offset < V2_HEADER.size:
            raise QualificationError(
                "invalid", "parse USN record", "invalid UTF-16 filename coordinates"
            )
        if name_offset + name_length > record_length:
            raise QualificationError(
                "invalid", "parse USN record", "filename extends beyond RecordLength"
            )
        raw_name = payload[offset + name_offset : offset + name_offset + name_length]
        try:
            filename = raw_name.decode("utf-16-le")
        except UnicodeDecodeError as exc:
            raise QualificationError(
                "invalid", "parse USN record", f"invalid UTF-16 filename: {exc}"
            ) from exc
        records.append(
            {
                "record_length": record_length,
                "major_version": major,
                "minor_version": minor,
                "file_reference_number": _u64(file_reference),
                "parent_file_reference_number": _u64(parent_reference),
                "usn": _i64(usn),
                "timestamp": str(timestamp),
                "reason": {
                    "decimal": str(reason),
                    "hex": f"0x{reason:08X}",
                    "recognized_names": reason_names(reason),
                },
                "source_info": {
                    "decimal": str(source_info),
                    "hex": f"0x{source_info:08X}",
                },
                "security_id": security_id,
                "file_attributes": {
                    "decimal": str(file_attributes),
                    "hex": f"0x{file_attributes:08X}",
                },
                "file_name": filename,
            }
        )
        offset += record_length
    return continuation, records


def record_acceptance(
    record: dict[str, Any], *, start_usn: int, end_usn: int, file_id64: int
) -> dict[str, Any]:
    usn = int(record["usn"]["decimal"])
    observed_file_id = int(record["file_reference_number"]["decimal"])
    reason = int(record["reason"]["decimal"])
    source_info = int(record["source_info"]["decimal"])
    checks = {
        "major_version_is_2": record["major_version"] == 2,
        "within_frozen_interval": start_usn <= usn < end_usn,
        "file_reference_matches_complete_file_id64": observed_file_id == file_id64,
        "reason_contains_close": bool(reason & USN_REASON_CLOSE),
        "reason_contains_data_overwrite": bool(reason & USN_REASON_DATA_OVERWRITE),
        "source_info_policy_satisfied": source_info == 0,
    }
    return {"accepted": all(checks.values()), "checks": checks}


def adjudicate_cross_arm(aa: str, ab: str) -> dict[str, str]:
    if aa == "QUALIFYING RECORD" and ab == "QUALIFYING RECORD":
        return {
            "basis": "LOCAL BASIS QUALIFIED",
            "operation_vs_content": (
                "DATA_OVERWRITE was observed for both A->A and A->B; the operation-category "
                "witness does not discriminate logical endpoint inequality in this fixture."
            ),
        }
    if aa == "NO QUALIFYING RECORD" and ab == "QUALIFYING RECORD":
        return {
            "basis": "LOCAL BASIS QUALIFIED FOR NARROWER ARM AB REGIME",
            "operation_vs_content": (
                "The qualifying operation-category witness survived only the A->B arm; "
                "the observed asymmetry is retained without assigning a content-value cause."
            ),
        }
    if aa == "QUALIFYING RECORD" and ab == "NO QUALIFYING RECORD":
        return {
            "basis": "BASIS NOT QUALIFIED",
            "operation_vs_content": (
                "The required minimum ARM AB witness was absent despite otherwise valid acquisition."
            ),
        }
    if aa == "NO QUALIFYING RECORD" and ab == "NO QUALIFYING RECORD":
        return {
            "basis": "BASIS NOT QUALIFIED",
            "operation_vs_content": (
                "No qualifying operation-category record was observed; absence is not stasis."
            ),
        }
    if "INVALID" in (aa, ab):
        return {
            "basis": "INVALID",
            "operation_vs_content": "Acquisition or continuity fracture prevents the operation/content comparison.",
        }
    return {
        "basis": "UNRESOLVED",
        "operation_vs_content": "The retained evidence does not warrant the Level-3 operation claim.",
    }


class Win32:
    def __init__(self) -> None:
        if os.name != "nt":
            raise QualificationError("invalid", "platform pre-flight", "Windows is required")
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.shell32 = ctypes.WinDLL("shell32", use_last_error=True)
        self.invalid_handle = ctypes.c_void_p(-1).value
        self._declare_signatures()

    def _declare_signatures(self) -> None:
        k32 = self.kernel32
        k32.CreateFileW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            ctypes.c_void_p,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.HANDLE,
        ]
        k32.CreateFileW.restype = wintypes.HANDLE
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
        k32.CloseHandle.restype = wintypes.BOOL
        k32.DeviceIoControl.argtypes = [
            wintypes.HANDLE,
            wintypes.DWORD,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
            ctypes.c_void_p,
        ]
        k32.DeviceIoControl.restype = wintypes.BOOL
        k32.GetFileInformationByHandle.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(BY_HANDLE_FILE_INFORMATION),
        ]
        k32.GetFileInformationByHandle.restype = wintypes.BOOL
        k32.WriteFile.argtypes = [
            wintypes.HANDLE,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
            ctypes.c_void_p,
        ]
        k32.WriteFile.restype = wintypes.BOOL
        k32.ReadFile.argtypes = [
            wintypes.HANDLE,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
            ctypes.c_void_p,
        ]
        k32.ReadFile.restype = wintypes.BOOL
        k32.FlushFileBuffers.argtypes = [wintypes.HANDLE]
        k32.FlushFileBuffers.restype = wintypes.BOOL
        k32.GetVolumeInformationW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.LPWSTR,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
            ctypes.POINTER(wintypes.DWORD),
            ctypes.POINTER(wintypes.DWORD),
            wintypes.LPWSTR,
            wintypes.DWORD,
        ]
        k32.GetVolumeInformationW.restype = wintypes.BOOL
        k32.GetVolumeNameForVolumeMountPointW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.LPWSTR,
            wintypes.DWORD,
        ]
        k32.GetVolumeNameForVolumeMountPointW.restype = wintypes.BOOL
        self.shell32.IsUserAnAdmin.argtypes = []
        self.shell32.IsUserAnAdmin.restype = wintypes.BOOL

    def _fail(self, category: str, operation: str) -> None:
        code = ctypes.get_last_error()
        raise QualificationError(category, operation, f"Win32 error {code}: {ctypes.FormatError(code)}")

    def open_handle(
        self, path: str, access: int, share: int, operation: str
    ) -> wintypes.HANDLE:
        handle = self.kernel32.CreateFileW(
            path, access, share, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None
        )
        if handle == self.invalid_handle:
            self._fail("invalid", operation)
        return handle

    def close_handle(self, handle: wintypes.HANDLE, operation: str) -> None:
        if not self.kernel32.CloseHandle(handle):
            self._fail("invalid", operation)

    def device_io(
        self,
        handle: wintypes.HANDLE,
        control_code: int,
        input_bytes: bytes | None,
        output_size: int,
        operation: str,
    ) -> bytes:
        input_buffer = ctypes.create_string_buffer(input_bytes) if input_bytes else None
        output_buffer = ctypes.create_string_buffer(output_size)
        returned = wintypes.DWORD()
        ok = self.kernel32.DeviceIoControl(
            handle,
            control_code,
            input_buffer,
            len(input_bytes) if input_bytes else 0,
            output_buffer,
            output_size,
            ctypes.byref(returned),
            None,
        )
        if not ok:
            self._fail("invalid", operation)
        return output_buffer.raw[: returned.value]

    def file_identity(self, handle: wintypes.HANDLE) -> dict[str, Any]:
        info = BY_HANDLE_FILE_INFORMATION()
        if not self.kernel32.GetFileInformationByHandle(handle, ctypes.byref(info)):
            self._fail("invalid", "GetFileInformationByHandle")
        file_id64 = compose_file_id64(info.nFileIndexHigh, info.nFileIndexLow)
        return {
            "method": "BY_HANDLE_FILE_INFORMATION",
            "volume_serial_number": {
                "decimal": str(info.dwVolumeSerialNumber),
                "hex": f"0x{info.dwVolumeSerialNumber:08X}",
            },
            "nFileIndexHigh": str(info.nFileIndexHigh),
            "nFileIndexLow": str(info.nFileIndexLow),
            "fileID64": _u64(file_id64),
        }

    def volume_identity(self, root: str) -> dict[str, Any]:
        name = ctypes.create_unicode_buffer(261)
        filesystem = ctypes.create_unicode_buffer(261)
        serial = wintypes.DWORD()
        max_component = wintypes.DWORD()
        flags = wintypes.DWORD()
        if not self.kernel32.GetVolumeInformationW(
            root,
            name,
            len(name),
            ctypes.byref(serial),
            ctypes.byref(max_component),
            ctypes.byref(flags),
            filesystem,
            len(filesystem),
        ):
            self._fail("invalid", "GetVolumeInformationW")
        guid = ctypes.create_unicode_buffer(261)
        if not self.kernel32.GetVolumeNameForVolumeMountPointW(root, guid, len(guid)):
            self._fail("invalid", "GetVolumeNameForVolumeMountPointW")
        return {
            "root": root,
            "volume_guid_path": guid.value,
            "volume_label": name.value,
            "volume_serial_number": {
                "decimal": str(serial.value),
                "hex": f"0x{serial.value:08X}",
            },
            "filesystem": filesystem.value,
            "filesystem_flags": {
                "decimal": str(flags.value),
                "hex": f"0x{flags.value:08X}",
            },
        }

    def write_once(self, handle: wintypes.HANDLE, content: bytes) -> dict[str, Any]:
        buffer = ctypes.create_string_buffer(content)
        written = wintypes.DWORD()
        if not self.kernel32.WriteFile(
            handle, buffer, len(content), ctypes.byref(written), None
        ):
            self._fail("invalid", "synchronous WriteFile")
        if written.value != len(content):
            raise QualificationError(
                "invalid",
                "synchronous WriteFile",
                f"short write: {written.value} of {len(content)} bytes",
            )
        if not self.kernel32.FlushFileBuffers(handle):
            self._fail("invalid", "FlushFileBuffers")
        return {
            "write_calls": 1,
            "requested_bytes": len(content),
            "written_bytes": written.value,
            "synchronous": True,
            "flush_completed": True,
        }

    def read_exact(self, handle: wintypes.HANDLE, length: int) -> bytes:
        buffer = ctypes.create_string_buffer(length)
        read = wintypes.DWORD()
        if not self.kernel32.ReadFile(handle, buffer, length, ctypes.byref(read), None):
            self._fail("invalid", "ReadFile endpoint observation")
        if read.value != length:
            raise QualificationError(
                "invalid",
                "ReadFile endpoint observation",
                f"short read: {read.value} of {length} bytes",
            )
        return buffer.raw[: read.value]


def _volume_root(path: Path) -> str:
    drive = path.resolve().drive
    if not drive:
        raise QualificationError("invalid", "resolve volume", f"no drive for {path}")
    return drive + "\\"


def _volume_device(root: str) -> str:
    return rf"\\.\{root[:2]}"


def query_journal(win32: Win32, volume_handle: wintypes.HANDLE) -> dict[str, Any]:
    raw = win32.device_io(
        volume_handle,
        FSCTL_QUERY_USN_JOURNAL,
        None,
        128,
        "FSCTL_QUERY_USN_JOURNAL",
    )
    if len(raw) < 56:
        raise QualificationError(
            "invalid", "parse USN_JOURNAL_DATA", f"only {len(raw)} bytes returned"
        )
    journal_id, first, next_usn, lowest, maximum, maximum_size, allocation = struct.unpack_from(
        "<QqqqqQQ", raw, 0
    )
    result: dict[str, Any] = {
        "bytes_returned": len(raw),
        "UsnJournalID": _u64(journal_id),
        "FirstUsn": _i64(first),
        "NextUsn": _i64(next_usn),
        "LowestValidUsn": _i64(lowest),
        "MaxUsn": _i64(maximum),
        "MaximumSize": str(maximum_size),
        "AllocationDelta": str(allocation),
    }
    if len(raw) >= 64:
        minimum_major, maximum_major, flags = struct.unpack_from("<HHI", raw, 56)
        result.update(
            {
                "MinSupportedMajorVersion": minimum_major,
                "MaxSupportedMajorVersion": maximum_major,
                "Flags": {"decimal": str(flags), "hex": f"0x{flags:08X}"},
            }
        )
    return result


def _journal_int(snapshot: dict[str, Any], name: str) -> int:
    return int(snapshot[name]["decimal"])


def read_interval(
    win32: Win32,
    volume_handle: wintypes.HANDLE,
    *,
    start_usn: int,
    end_usn: int,
    journal_id: int,
) -> dict[str, Any]:
    cursor = start_usn
    calls: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    while cursor < end_usn:
        request = READ_USN_JOURNAL_DATA_V1.pack(
            cursor,
            USN_REASON_CLOSE,
            1,
            0,
            0,
            journal_id,
            2,
            2,
        )
        raw = win32.device_io(
            volume_handle,
            FSCTL_READ_USN_JOURNAL,
            request,
            1024 * 1024,
            "FSCTL_READ_USN_JOURNAL",
        )
        continuation, batch = parse_v2_records(raw)
        calls.append(
            {
                "request": {
                    "StartUsn": _i64(cursor),
                    "ReasonMask": {
                        "decimal": str(USN_REASON_CLOSE),
                        "hex": f"0x{USN_REASON_CLOSE:08X}",
                        "name": "USN_REASON_CLOSE",
                    },
                    "ReturnOnlyOnClose": 1,
                    "Timeout": 0,
                    "BytesToWaitFor": 0,
                    "UsnJournalID": _u64(journal_id),
                    "MinMajorVersion": 2,
                    "MaxMajorVersion": 2,
                },
                "bytes_returned": len(raw),
                "returned_continuation_usn": _i64(continuation),
                "records_returned": len(batch),
            }
        )
        records.extend(batch)
        if continuation <= cursor:
            raise QualificationError(
                "invalid",
                "bounded journal acquisition",
                f"non-advancing continuation {continuation} from cursor {cursor}",
            )
        cursor = continuation
    return {
        "interval": {"S_inclusive": _i64(start_usn), "E_exclusive": _i64(end_usn)},
        "read_mode": "READ_USN_JOURNAL_DATA_V1",
        "calls": calls,
        "acquisition_complete": cursor >= end_usn,
        "final_continuation_usn": _i64(cursor),
        "records": records,
    }


def probe_read_mode(
    win32: Win32,
    volume_handle: wintypes.HANDLE,
    *,
    start_usn: int,
    journal_id: int,
) -> dict[str, Any]:
    """Issue exactly one non-waiting frozen-mode read for pre-flight evidence."""

    request = READ_USN_JOURNAL_DATA_V1.pack(
        start_usn,
        USN_REASON_CLOSE,
        1,
        0,
        0,
        journal_id,
        2,
        2,
    )
    raw = win32.device_io(
        volume_handle,
        FSCTL_READ_USN_JOURNAL,
        request,
        1024 * 1024,
        "pre-flight FSCTL_READ_USN_JOURNAL",
    )
    continuation, records = parse_v2_records(raw)
    return {
        "request": {
            "StartUsn": _i64(start_usn),
            "ReasonMask": "USN_REASON_CLOSE",
            "ReturnOnlyOnClose": 1,
            "Timeout": 0,
            "BytesToWaitFor": 0,
            "UsnJournalID": _u64(journal_id),
            "MinMajorVersion": 2,
            "MaxMajorVersion": 2,
        },
        "bytes_returned": len(raw),
        "returned_continuation_usn": _i64(continuation),
        "records_returned": len(records),
        "records": records,
        "device_io_completed": True,
    }


def _identity_for_path(win32: Win32, path: Path) -> dict[str, Any]:
    handle = win32.open_handle(
        str(path),
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        "open file for identity",
    )
    try:
        return win32.file_identity(handle)
    finally:
        win32.close_handle(handle, "close identity handle")


def _endpoint_for_path(win32: Win32, path: Path, length: int) -> dict[str, Any]:
    handle = win32.open_handle(
        str(path), GENERIC_READ, FILE_SHARE_READ, "open endpoint observation"
    )
    try:
        identity = win32.file_identity(handle)
        content = win32.read_exact(handle, length)
    finally:
        win32.close_handle(handle, "close endpoint observation")
    return {
        "identity": identity,
        "byte_length": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "all_bytes_equal_ascii": chr(content[0]) if content and len(set(content)) == 1 else None,
    }


def _baseline(path: Path) -> None:
    with path.open("wb", buffering=0) as stream:
        written = stream.write(CONTENT_A)
        if written != len(CONTENT_A):
            raise QualificationError(
                "invalid", "establish content A", f"short write {written}"
            )
        os.fsync(stream.fileno())


def _same_volume(a: dict[str, Any], b: dict[str, Any]) -> bool:
    keys = ("root", "volume_guid_path", "filesystem")
    return all(a[key] == b[key] for key in keys) and (
        a["volume_serial_number"] == b["volume_serial_number"]
    )


def run_arm(
    win32: Win32,
    volume_handle: wintypes.HANDLE,
    volume_root: str,
    fixture_path: Path,
    arm_name: str,
    target: bytes,
) -> dict[str, Any]:
    arm: dict[str, Any] = {
        "arm": arm_name,
        "declared_transition": "A -> A" if target == CONTENT_A else "A -> B",
        "same_length": len(target) == len(CONTENT_A),
        "logical_endpoint_inequality_declared": target != CONTENT_A,
        "source_info_inclusion_policy": SOURCE_INFO_POLICY,
    }
    try:
        _baseline(fixture_path)
        baseline_endpoint = _endpoint_for_path(win32, fixture_path, len(CONTENT_A))
        arm["baseline_endpoint"] = baseline_endpoint
        before_volume = win32.volume_identity(volume_root)
        before_journal = query_journal(win32, volume_handle)
        start_usn = _journal_int(before_journal, "NextUsn")
        journal_id = int(before_journal["UsnJournalID"]["decimal"])
        arm["before"] = {
            "volume_identity": before_volume,
            "journal": before_journal,
            "S": _i64(start_usn),
        }

        writer = win32.open_handle(
            str(fixture_path),
            GENERIC_READ | GENERIC_WRITE,
            0,
            "open selected file writer after S",
        )
        writer_closed = False
        try:
            writer_identity = win32.file_identity(writer)
            write_result = win32.write_once(writer, target)
        finally:
            win32.close_handle(writer, "controlled final close")
            writer_closed = True
        arm["controlled_write"] = {
            "opened_after_S": True,
            "identity": writer_identity,
            **write_result,
            "handle_closed_before_E": writer_closed,
        }

        after_journal = query_journal(win32, volume_handle)
        end_usn = _journal_int(after_journal, "NextUsn")
        after_volume = win32.volume_identity(volume_root)
        arm["after"] = {
            "volume_identity": after_volume,
            "journal": after_journal,
            "E": _i64(end_usn),
        }

        journal_continuity = {
            "same_volume_identity": _same_volume(before_volume, after_volume),
            "filesystem_is_ntfs": before_volume["filesystem"].upper() == "NTFS",
            "same_UsnJournalID": (
                before_journal["UsnJournalID"] == after_journal["UsnJournalID"]
            ),
            "S_not_below_final_FirstUsn": start_usn
            >= _journal_int(after_journal, "FirstUsn"),
            "S_not_below_final_LowestValidUsn": start_usn
            >= _journal_int(after_journal, "LowestValidUsn"),
            "nonempty_or_zero_width_valid_interval": end_usn >= start_usn,
        }
        arm["journal_continuity"] = journal_continuity
        if not all(journal_continuity.values()):
            raise QualificationError(
                "invalid", "journal continuity", json.dumps(journal_continuity, sort_keys=True)
            )

        acquisition = read_interval(
            win32,
            volume_handle,
            start_usn=start_usn,
            end_usn=end_usn,
            journal_id=journal_id,
        )
        arm["bounded_acquisition"] = acquisition
        final_endpoint = _endpoint_for_path(win32, fixture_path, len(target))
        arm["final_endpoint"] = final_endpoint

        expected_hash = hashlib.sha256(target).hexdigest()
        baseline_id = int(baseline_endpoint["identity"]["fileID64"]["decimal"])
        writer_id = int(writer_identity["fileID64"]["decimal"])
        final_id = int(final_endpoint["identity"]["fileID64"]["decimal"])
        volume_serial = before_volume["volume_serial_number"]
        identity_checks = {
            "baseline_writer_final_fileID64_equal": baseline_id == writer_id == final_id,
            "file_identity_volume_matches_selected_volume": (
                baseline_endpoint["identity"]["volume_serial_number"]
                == writer_identity["volume_serial_number"]
                == final_endpoint["identity"]["volume_serial_number"]
                == volume_serial
            ),
            "endpoint_bytes_match_declared_target": final_endpoint["sha256"] == expected_hash,
            "endpoint_length_preserved": final_endpoint["byte_length"] == len(CONTENT_A),
        }
        arm["identity_and_endpoint_checks"] = identity_checks
        if not all(identity_checks.values()):
            raise QualificationError(
                "invalid", "file identity continuity", json.dumps(identity_checks, sort_keys=True)
            )

        selected_records: list[dict[str, Any]] = []
        qualifying_records: list[dict[str, Any]] = []
        source_policy_ambiguity = False
        for record in acquisition["records"]:
            acceptance = record_acceptance(
                record, start_usn=start_usn, end_usn=end_usn, file_id64=baseline_id
            )
            annotated = {**record, "acceptance": acceptance}
            checks = acceptance["checks"]
            if checks["file_reference_matches_complete_file_id64"] and checks[
                "within_frozen_interval"
            ]:
                selected_records.append(annotated)
                if (
                    checks["major_version_is_2"]
                    and checks["reason_contains_close"]
                    and checks["reason_contains_data_overwrite"]
                    and not checks["source_info_policy_satisfied"]
                ):
                    source_policy_ambiguity = True
            if acceptance["accepted"]:
                qualifying_records.append(annotated)

        lifecycle = {
            "baseline_closed_before_S": True,
            "selected_writer_opened_after_S": True,
            "exactly_one_synchronous_write_call": write_result["write_calls"] == 1,
            "controlled_final_close_before_E": writer_closed,
            "bounded_read_completed": acquisition["acquisition_complete"],
            "same_file_identity_through_arm": baseline_id == writer_id == final_id,
            "association_basis": (
                "unique fixture object; baseline handle closed before S; exclusive selected-file "
                "writer opened after S; one synchronous write; controlled close before E; complete "
                "fileID64 match; endpoint re-observed after E"
            ),
        }
        arm["lifecycle_association"] = lifecycle
        arm["selected_file_records"] = selected_records
        arm["qualifying_records"] = qualifying_records
        if not all(value for key, value in lifecycle.items() if key != "association_basis"):
            arm["verdict"] = "INVALID"
            arm["verdict_reason"] = "Lifecycle association integrity was not established."
        elif source_policy_ambiguity and not qualifying_records:
            arm["verdict"] = "UNRESOLVED"
            arm["verdict_reason"] = (
                "A matching CLOSE + DATA_OVERWRITE record existed but failed the frozen SourceInfo == 0 policy."
            )
        elif qualifying_records:
            arm["verdict"] = "QUALIFYING RECORD"
            arm["verdict_reason"] = (
                f"{len(qualifying_records)} associated V2 record(s) satisfied every frozen acceptance check."
            )
        else:
            arm["verdict"] = "NO QUALIFYING RECORD"
            arm["verdict_reason"] = (
                "No record satisfied the conjunction despite otherwise valid bounded acquisition; absence is not stasis."
            )
    except QualificationError as exc:
        arm["verdict"] = "INVALID" if exc.category == "invalid" else "UNRESOLVED"
        arm["error"] = exc.as_dict()
    return arm


def _git(command: Iterable[str]) -> str:
    completed = subprocess.run(
        ["git", *command], text=True, capture_output=True, check=True
    )
    return completed.stdout.strip()


def run(output: Path) -> tuple[dict[str, Any], int]:
    trace: dict[str, Any] = {
        "experiment": EXPERIMENT_ID,
        "scope": "one-shot frozen NTFS USN observation-basis qualification",
        "not_a_general_observer": True,
        "repository": {
            "HEAD": _git(["rev-parse", "HEAD"]),
            "origin_main": _git(["rev-parse", "origin/main"]),
        },
        "frozen_acceptance": {
            "record_major_version": 2,
            "identity_method": "BY_HANDLE_FILE_INFORMATION",
            "read_mode": "READ_USN_JOURNAL_DATA_V1",
            "ReasonMask": "USN_REASON_CLOSE",
            "ReturnOnlyOnClose": 1,
            "BytesToWaitFor": 0,
            "SourceInfo_policy": SOURCE_INFO_POLICY,
            "manual_reason_conjunction": [
                "USN_REASON_CLOSE",
                "USN_REASON_DATA_OVERWRITE",
            ],
        },
    }
    exit_code = 1
    fixture_dir: Path | None = None
    volume_handle: wintypes.HANDLE | None = None
    try:
        win32 = Win32()
        root = _volume_root(Path.cwd())
        volume_identity = win32.volume_identity(root)
        preflight: dict[str, Any] = {
            "platform": sys.platform,
            "elevated": bool(win32.shell32.IsUserAnAdmin()),
            "volume_identity": volume_identity,
            "journal_was_not_created_enabled_resized_or_deleted": True,
        }
        trace["preflight"] = preflight
        if volume_identity["filesystem"].upper() != "NTFS":
            raise QualificationError(
                "invalid", "filesystem pre-flight", volume_identity["filesystem"]
            )
        if not preflight["elevated"]:
            raise QualificationError("invalid", "privilege pre-flight", "process is not elevated")
        volume_handle = win32.open_handle(
            _volume_device(root),
            GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            "open selected NTFS volume",
        )
        initial_journal = query_journal(win32, volume_handle)
        jid = int(initial_journal["UsnJournalID"]["decimal"])
        next_usn = _journal_int(initial_journal, "NextUsn")
        empty_probe = probe_read_mode(
            win32,
            volume_handle,
            start_usn=next_usn,
            journal_id=jid,
        )
        preflight.update(
            {
                "journal_query": initial_journal,
                "frozen_read_mode_probe": empty_probe,
                "qualified_to_mutate_fixture": True,
            }
        )

        fixture_dir = Path(tempfile.mkdtemp(prefix="dme_usn_basis_", dir=Path.cwd()))
        fixture_path = fixture_dir / "selected_file.bin"
        trace["fixture"] = {
            "directory": str(fixture_dir),
            "same_selected_volume_as_repository": _volume_root(fixture_dir) == root,
            "content_length": len(CONTENT_A),
            "content_A_sha256": hashlib.sha256(CONTENT_A).hexdigest(),
            "content_B_sha256": hashlib.sha256(CONTENT_B).hexdigest(),
            "same_selected_file_object_between_arms_required": True,
            "arm_sequence_is_not_A_to_B_to_A": True,
        }
        aa = run_arm(win32, volume_handle, root, fixture_path, "AA", CONTENT_A)
        ab = run_arm(win32, volume_handle, root, fixture_path, "AB", CONTENT_B)
        trace["arms"] = {"AA": aa, "AB": ab}
        if aa["verdict"] not in ("INVALID", "UNRESOLVED") and ab["verdict"] not in (
            "INVALID",
            "UNRESOLVED",
        ):
            aa_id = aa["baseline_endpoint"]["identity"]["fileID64"]
            ab_id = ab["baseline_endpoint"]["identity"]["fileID64"]
            trace["fixture"]["cross_arm_identity"] = {
                "AA_fileID64": aa_id,
                "AB_fileID64": ab_id,
                "same_complete_fileID64": aa_id == ab_id,
            }
            if aa_id != ab_id:
                trace["cross_arm"] = {
                    "basis": "INVALID",
                    "operation_vs_content": (
                        "The selected file object identity changed between arms."
                    ),
                }
            else:
                trace["cross_arm"] = adjudicate_cross_arm(aa["verdict"], ab["verdict"])
        else:
            trace["cross_arm"] = adjudicate_cross_arm(aa["verdict"], ab["verdict"])
        exit_code = 0 if trace["cross_arm"]["basis"].startswith("LOCAL BASIS QUALIFIED") else 2
    except QualificationError as exc:
        trace.setdefault("preflight", {})["qualified_to_mutate_fixture"] = False
        trace["execution_error"] = exc.as_dict()
        trace["cross_arm"] = {
            "basis": "INVALID" if exc.category == "invalid" else "UNRESOLVED",
            "operation_vs_content": "The controlled arms were not both executable.",
        }
    finally:
        if volume_handle is not None:
            try:
                win32.close_handle(volume_handle, "close selected NTFS volume")
            except QualificationError as exc:
                trace["volume_close_error"] = exc.as_dict()
                trace["cross_arm"]["basis"] = "INVALID"
                exit_code = 2
        cleanup: dict[str, Any] = {"attempted": fixture_dir is not None}
        if fixture_dir is not None:
            try:
                shutil.rmtree(fixture_dir)
                cleanup["completed"] = True
            except OSError as exc:
                cleanup.update({"completed": False, "error": str(exc)})
        trace["fixture_cleanup"] = cleanup
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
    return trace, exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_TRACE)
    args = parser.parse_args()
    trace, exit_code = run(args.output)
    print(json.dumps({"trace": str(args.output), "result": trace["cross_arm"]}, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
