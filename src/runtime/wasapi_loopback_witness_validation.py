"""Pressure-only WASAPI loopback witness validation.

The watcher and emitter are deliberately separate OS processes. The watcher
receives an endpoint ID and capture paths only; trial meaning is joined by the
orchestrator after capture.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
import platform
import random
import struct
import subprocess
import sys
import time
import uuid
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory
from typing import Any

from src.runtime.acoustic_basis_entry_pressure import (
    CHANNEL_COUNT,
    SAMPLE_RATE,
    SAMPLE_WIDTH_BYTES,
    _WinMMBackend,
    _select_named_device,
)


EXPERIMENT = "wasapi_loopback_witness_validation_v0"
OBSERVER = "wasapi_shared_mode_loopback_pressure"
OBSERVER_VERSION = "wasapi_loopback_witness_v0"
TRACE_PATH = Path("traces") / "wasapi_loopback_witness_validation_v0.json"
TARGET_FRIENDLY_NAME = "Speakers (Realtek High Definition Audio)"
TRIAL_SEED = 20_260_908_17
TRIAL_ORDER = (
    "S1", "S1", "C0", "S1", "S2",
    "C0", "C0", "C0", "S2", "S1",
    "S2", "S2", "C0", "S1", "S2",
)
FREQUENCIES_HZ = {"S1": 900.0, "S2": 1_500.0}
PREFLIGHT_AMPLITUDE = 0.001
PRIMARY_AMPLITUDE = 0.002
TONE_SECONDS = 0.18
CAPTURE_SECONDS = 0.70
PRE_ROLL_SECONDS = 0.18
MEDIAN_DOMINANCE_DB = 12.0
MINIMUM_TRIAL_DOMINANCE_DB = 6.0
TARGET_OVER_CONTROL_DB = 12.0
MAX_CONTROL_IMITATIONS = 1

AUDCLNT_SHAREMODE_SHARED = 0
AUDCLNT_STREAMFLAGS_LOOPBACK = 0x00020000
AUDCLNT_BUFFERFLAGS_DATA_DISCONTINUITY = 0x1
AUDCLNT_BUFFERFLAGS_SILENT = 0x2
AUDCLNT_BUFFERFLAGS_TIMESTAMP_ERROR = 0x4
DEVICE_STATE_ACTIVE = 0x1
E_RENDER = 0
CLSCTX_ALL = 23
STGM_READ = 0
COINIT_MULTITHREADED = 0
VT_LPWSTR = 31
WAVE_FORMAT_PCM = 0x0001
WAVE_FORMAT_IEEE_FLOAT = 0x0003
WAVE_FORMAT_EXTENSIBLE = 0xFFFE

CLSID_MMDEVICE_ENUMERATOR = "BCDE0395-E52F-467C-8E3D-C4579291692E"
IID_IMMDEVICE_ENUMERATOR = "A95664D2-9614-4F35-A746-DE8DB63617E6"
IID_IAUDIO_CLIENT = "1CB9AD4C-DBFA-4c32-B178-C2F568A703B2"
IID_IAUDIO_CAPTURE_CLIENT = "C8ADBD64-E71E-48a0-A4DE-185C395CD317"
PKEY_FRIENDLY_NAME_FMTID = "a45c254e-df1c-4efd-8020-67d146a850e0"
PKEY_FRIENDLY_NAME_PID = 14

HRESULT = ctypes.c_long
UINT32 = ctypes.c_uint32
UINT64 = ctypes.c_uint64


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]

    @classmethod
    def parse(cls, value: str) -> "GUID":
        raw = uuid.UUID(value).bytes_le
        return cls(
            int.from_bytes(raw[0:4], "little"),
            int.from_bytes(raw[4:6], "little"),
            int.from_bytes(raw[6:8], "little"),
            (ctypes.c_ubyte * 8)(*raw[8:]),
        )

    def text(self) -> str:
        raw = (
            int(self.Data1).to_bytes(4, "little")
            + int(self.Data2).to_bytes(2, "little")
            + int(self.Data3).to_bytes(2, "little")
            + bytes(self.Data4)
        )
        return str(uuid.UUID(bytes_le=raw))


class PROPERTYKEY(ctypes.Structure):
    _fields_ = [("fmtid", GUID), ("pid", wintypes.DWORD)]


class _PropVariantUnion(ctypes.Union):
    _fields_ = [
        ("pwszVal", ctypes.c_wchar_p),
        ("ulVal", wintypes.ULONG),
        ("uhVal", ctypes.c_ulonglong),
        ("pointer", ctypes.c_void_p),
    ]


class PROPVARIANT(ctypes.Structure):
    _anonymous_ = ("value",)
    _fields_ = [
        ("vt", wintypes.USHORT),
        ("reserved1", wintypes.USHORT),
        ("reserved2", wintypes.USHORT),
        ("reserved3", wintypes.USHORT),
        ("value", _PropVariantUnion),
    ]


class CoreWaveFormat(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("wFormatTag", wintypes.WORD),
        ("nChannels", wintypes.WORD),
        ("nSamplesPerSec", wintypes.DWORD),
        ("nAvgBytesPerSec", wintypes.DWORD),
        ("nBlockAlign", wintypes.WORD),
        ("wBitsPerSample", wintypes.WORD),
        ("cbSize", wintypes.WORD),
    ]


def _com_method(
    pointer: ctypes.c_void_p,
    index: int,
    restype: Any,
    *argtypes: Any,
) -> Any:
    vtable = ctypes.cast(
        pointer, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))
    ).contents
    return ctypes.WINFUNCTYPE(restype, ctypes.c_void_p, *argtypes)(vtable[index])


def _check_hresult(result: int, operation: str) -> None:
    if result < 0:
        code = ctypes.c_uint32(result).value
        raise OSError(f"{operation} failed with HRESULT 0x{code:08x}")


def _release(pointer: ctypes.c_void_p | None) -> None:
    if pointer is not None and pointer.value:
        _com_method(pointer, 2, wintypes.ULONG)(pointer)
        pointer.value = None


def _ole32() -> Any:
    ole = ctypes.OleDLL("ole32")
    ole.CoInitializeEx.argtypes = [ctypes.c_void_p, wintypes.DWORD]
    ole.CoInitializeEx.restype = HRESULT
    ole.CoCreateInstance.argtypes = [
        ctypes.POINTER(GUID),
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(GUID),
        ctypes.POINTER(ctypes.c_void_p),
    ]
    ole.CoCreateInstance.restype = HRESULT
    ole.CoTaskMemFree.argtypes = [ctypes.c_void_p]
    ole.PropVariantClear.argtypes = [ctypes.POINTER(PROPVARIANT)]
    ole.PropVariantClear.restype = HRESULT
    return ole


def _new_enumerator(ole: Any) -> ctypes.c_void_p:
    enumerator = ctypes.c_void_p()
    clsid = GUID.parse(CLSID_MMDEVICE_ENUMERATOR)
    iid = GUID.parse(IID_IMMDEVICE_ENUMERATOR)
    _check_hresult(
        ole.CoCreateInstance(
            ctypes.byref(clsid), None, CLSCTX_ALL, ctypes.byref(iid), ctypes.byref(enumerator)
        ),
        "CoCreateInstance(MMDeviceEnumerator)",
    )
    return enumerator


def _device_metadata(device: ctypes.c_void_p, ole: Any) -> dict[str, Any]:
    endpoint_id = ctypes.c_wchar_p()
    _check_hresult(
        _com_method(device, 5, HRESULT, ctypes.POINTER(ctypes.c_wchar_p))(
            device, ctypes.byref(endpoint_id)
        ),
        "IMMDevice.GetId",
    )
    state = wintypes.DWORD()
    _check_hresult(
        _com_method(device, 6, HRESULT, ctypes.POINTER(wintypes.DWORD))(
            device, ctypes.byref(state)
        ),
        "IMMDevice.GetState",
    )
    store = ctypes.c_void_p()
    variant = PROPVARIANT()
    try:
        _check_hresult(
            _com_method(
                device,
                4,
                HRESULT,
                wintypes.DWORD,
                ctypes.POINTER(ctypes.c_void_p),
            )(device, STGM_READ, ctypes.byref(store)),
            "IMMDevice.OpenPropertyStore",
        )
        key = PROPERTYKEY(GUID.parse(PKEY_FRIENDLY_NAME_FMTID), PKEY_FRIENDLY_NAME_PID)
        _check_hresult(
            _com_method(
                store,
                5,
                HRESULT,
                ctypes.POINTER(PROPERTYKEY),
                ctypes.POINTER(PROPVARIANT),
            )(store, ctypes.byref(key), ctypes.byref(variant)),
            "IPropertyStore.GetValue(PKEY_Device_FriendlyName)",
        )
        friendly_name = variant.pwszVal if variant.vt == VT_LPWSTR else None
        return {
            "endpoint_id": endpoint_id.value,
            "friendly_name": friendly_name,
            "endpoint_state": int(state.value),
            "endpoint_state_active": bool(state.value & DEVICE_STATE_ACTIVE),
        }
    finally:
        if variant.vt:
            ole.PropVariantClear(ctypes.byref(variant))
        _release(store)
        if endpoint_id:
            ole.CoTaskMemFree(endpoint_id)


def enumerate_render_endpoints() -> list[dict[str, Any]]:
    """Enumerate active Core Audio render endpoints without opening a stream."""
    if os.name != "nt":
        raise OSError("WASAPI is available only on Windows")
    ole = _ole32()
    initialized = False
    enumerator = ctypes.c_void_p()
    collection = ctypes.c_void_p()
    try:
        _check_hresult(ole.CoInitializeEx(None, COINIT_MULTITHREADED), "CoInitializeEx")
        initialized = True
        enumerator = _new_enumerator(ole)
        _check_hresult(
            _com_method(
                enumerator,
                3,
                HRESULT,
                ctypes.c_int,
                wintypes.DWORD,
                ctypes.POINTER(ctypes.c_void_p),
            )(
                enumerator,
                E_RENDER,
                DEVICE_STATE_ACTIVE,
                ctypes.byref(collection),
            ),
            "IMMDeviceEnumerator.EnumAudioEndpoints",
        )
        count = UINT32()
        _check_hresult(
            _com_method(collection, 3, HRESULT, ctypes.POINTER(UINT32))(
                collection, ctypes.byref(count)
            ),
            "IMMDeviceCollection.GetCount",
        )
        endpoints = []
        for index in range(count.value):
            device = ctypes.c_void_p()
            try:
                _check_hresult(
                    _com_method(
                        collection,
                        4,
                        HRESULT,
                        UINT32,
                        ctypes.POINTER(ctypes.c_void_p),
                    )(collection, index, ctypes.byref(device)),
                    "IMMDeviceCollection.Item",
                )
                endpoints.append({"enumeration_index": index, **_device_metadata(device, ole)})
            finally:
                _release(device)
        return endpoints
    finally:
        _release(collection)
        _release(enumerator)
        if initialized:
            ole.CoUninitialize()


def select_realtek_endpoint(endpoints: list[dict[str, Any]]) -> dict[str, Any]:
    matches = [
        item
        for item in endpoints
        if item.get("friendly_name") == TARGET_FRIENDLY_NAME
        and item.get("endpoint_state_active") is True
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"expected exactly one active {TARGET_FRIENDLY_NAME!r} endpoint; found {len(matches)}"
        )
    return matches[0]


def _get_device_by_id(enumerator: ctypes.c_void_p, endpoint_id: str) -> ctypes.c_void_p:
    device = ctypes.c_void_p()
    _check_hresult(
        _com_method(
            enumerator,
            5,
            HRESULT,
            ctypes.c_wchar_p,
            ctypes.POINTER(ctypes.c_void_p),
        )(enumerator, endpoint_id, ctypes.byref(device)),
        "IMMDeviceEnumerator.GetDevice",
    )
    return device


def parse_mix_format(raw: bytes) -> dict[str, Any]:
    if len(raw) < 18:
        raise ValueError("mix format shorter than WAVEFORMATEX")
    tag, channels, rate, avg_bytes, align, bits, cb_size = struct.unpack_from(
        "<HHIIHHH", raw, 0
    )
    result: dict[str, Any] = {
        "format_tag": tag,
        "format_tag_hex": f"0x{tag:04x}",
        "channel_count": channels,
        "sample_rate_hz": rate,
        "average_bytes_per_second": avg_bytes,
        "block_align_bytes": align,
        "container_bits_per_sample": bits,
        "extra_size_bytes": cb_size,
        "format_bytes_sha256": hashlib.sha256(raw).hexdigest(),
        "format_bytes_hex": raw.hex(),
    }
    subformat = None
    if tag == WAVE_FORMAT_EXTENSIBLE and cb_size >= 22 and len(raw) >= 40:
        valid_bits, channel_mask = struct.unpack_from("<HI", raw, 18)
        subformat = GUID.from_buffer_copy(raw[24:40]).text()
        result.update(
            {
                "valid_bits_per_sample": valid_bits,
                "channel_mask": channel_mask,
                "channel_mask_hex": f"0x{channel_mask:08x}",
                "subformat_guid": subformat,
            }
        )
    if tag == WAVE_FORMAT_IEEE_FLOAT or subformat == "00000003-0000-0010-8000-00aa00389b71":
        representation = f"float{bits}_little_endian"
    elif tag == WAVE_FORMAT_PCM or subformat == "00000001-0000-0010-8000-00aa00389b71":
        representation = f"signed_pcm_{bits}_little_endian"
    else:
        representation = "unsupported_or_unknown"
    result["sample_representation"] = representation
    return result


def _activate_audio_client(device: ctypes.c_void_p) -> ctypes.c_void_p:
    client = ctypes.c_void_p()
    iid = GUID.parse(IID_IAUDIO_CLIENT)
    _check_hresult(
        _com_method(
            device,
            3,
            HRESULT,
            ctypes.POINTER(GUID),
            wintypes.DWORD,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
        )(device, ctypes.byref(iid), CLSCTX_ALL, None, ctypes.byref(client)),
        "IMMDevice.Activate(IAudioClient)",
    )
    return client


def watch_endpoint(
    endpoint_id: str,
    duration_seconds: float,
    ready_path: Path,
    result_path: Path,
    pcm_path: Path,
) -> dict[str, Any]:
    """Acquire loopback packets. This function receives no condition metadata."""
    ole = _ole32()
    initialized = False
    enumerator = ctypes.c_void_p()
    device = ctypes.c_void_p()
    client = ctypes.c_void_p()
    capture = ctypes.c_void_p()
    mix_pointer = ctypes.c_void_p()
    started = False
    packets: list[dict[str, Any]] = []
    pcm = bytearray()
    started_at = None
    finished_at = None
    try:
        _check_hresult(ole.CoInitializeEx(None, COINIT_MULTITHREADED), "CoInitializeEx")
        initialized = True
        enumerator = _new_enumerator(ole)
        device = _get_device_by_id(enumerator, endpoint_id)
        endpoint = _device_metadata(device, ole)
        if endpoint["endpoint_id"] != endpoint_id:
            raise RuntimeError("watcher reacquired a different endpoint ID")
        if not endpoint["endpoint_state_active"]:
            raise RuntimeError("selected endpoint is not active")
        client = _activate_audio_client(device)
        _check_hresult(
            _com_method(client, 8, HRESULT, ctypes.POINTER(ctypes.c_void_p))(
                client, ctypes.byref(mix_pointer)
            ),
            "IAudioClient.GetMixFormat",
        )
        base = ctypes.cast(mix_pointer, ctypes.POINTER(CoreWaveFormat)).contents
        mix_bytes = ctypes.string_at(mix_pointer, 18 + int(base.cbSize))
        mix = parse_mix_format(mix_bytes)
        if mix["sample_representation"] == "unsupported_or_unknown":
            raise RuntimeError("unsupported WASAPI mix sample representation")
        _check_hresult(
            _com_method(
                client,
                3,
                HRESULT,
                ctypes.c_int,
                wintypes.DWORD,
                ctypes.c_longlong,
                ctypes.c_longlong,
                ctypes.c_void_p,
                ctypes.c_void_p,
            )(
                client,
                AUDCLNT_SHAREMODE_SHARED,
                AUDCLNT_STREAMFLAGS_LOOPBACK,
                10_000_000,
                0,
                mix_pointer,
                None,
            ),
            "IAudioClient.Initialize(shared loopback)",
        )
        buffer_frames = UINT32()
        _check_hresult(
            _com_method(client, 4, HRESULT, ctypes.POINTER(UINT32))(
                client, ctypes.byref(buffer_frames)
            ),
            "IAudioClient.GetBufferSize",
        )
        capture_iid = GUID.parse(IID_IAUDIO_CAPTURE_CLIENT)
        _check_hresult(
            _com_method(
                client,
                14,
                HRESULT,
                ctypes.POINTER(GUID),
                ctypes.POINTER(ctypes.c_void_p),
            )(client, ctypes.byref(capture_iid), ctypes.byref(capture)),
            "IAudioClient.GetService(IAudioCaptureClient)",
        )
        _check_hresult(_com_method(client, 10, HRESULT)(client), "IAudioClient.Start")
        started = True
        started_at = utc_now()
        start_perf_ns = time.perf_counter_ns()
        ready = {
            "observer": OBSERVER,
            "observer_version": OBSERVER_VERSION,
            "watcher_pid": os.getpid(),
            "endpoint": endpoint,
            "mix_format": mix,
            "stream_mode": "WASAPI shared-mode loopback",
            "capture_api": "IAudioCaptureClient",
            "stream_buffer_frames": int(buffer_frames.value),
            "capture_started_at_utc": started_at,
            "capture_started_perf_counter_ns": start_perf_ns,
            "semantic_condition_received": False,
            "playback_metadata_received": False,
        }
        ready_path.write_text(json.dumps(ready, indent=2, sort_keys=True), encoding="utf-8")
        deadline = time.perf_counter() + duration_seconds
        packet_ordinal = 0
        while time.perf_counter() < deadline:
            next_frames = UINT32()
            _check_hresult(
                _com_method(capture, 5, HRESULT, ctypes.POINTER(UINT32))(
                    capture, ctypes.byref(next_frames)
                ),
                "IAudioCaptureClient.GetNextPacketSize",
            )
            if next_frames.value == 0:
                time.sleep(0.002)
                continue
            while next_frames.value:
                data = ctypes.c_void_p()
                frames = UINT32()
                flags = wintypes.DWORD()
                device_position = UINT64()
                qpc_position = UINT64()
                _check_hresult(
                    _com_method(
                        capture,
                        3,
                        HRESULT,
                        ctypes.POINTER(ctypes.c_void_p),
                        ctypes.POINTER(UINT32),
                        ctypes.POINTER(wintypes.DWORD),
                        ctypes.POINTER(UINT64),
                        ctypes.POINTER(UINT64),
                    )(
                        capture,
                        ctypes.byref(data),
                        ctypes.byref(frames),
                        ctypes.byref(flags),
                        ctypes.byref(device_position),
                        ctypes.byref(qpc_position),
                    ),
                    "IAudioCaptureClient.GetBuffer",
                )
                byte_count = int(frames.value) * int(mix["block_align_bytes"])
                if flags.value & AUDCLNT_BUFFERFLAGS_SILENT:
                    packet_bytes = bytes(byte_count)
                else:
                    packet_bytes = ctypes.string_at(data, byte_count)
                pcm.extend(packet_bytes)
                packet_ordinal += 1
                packets.append(
                    {
                        "packet_ordinal": packet_ordinal,
                        "frame_count": int(frames.value),
                        "byte_count": byte_count,
                        "flags": int(flags.value),
                        "silent": bool(flags.value & AUDCLNT_BUFFERFLAGS_SILENT),
                        "data_discontinuity": bool(
                            flags.value & AUDCLNT_BUFFERFLAGS_DATA_DISCONTINUITY
                        ),
                        "timestamp_error": bool(
                            flags.value & AUDCLNT_BUFFERFLAGS_TIMESTAMP_ERROR
                        ),
                        "stream_device_position_frames": int(device_position.value),
                        "qpc_position_100ns": int(qpc_position.value),
                        "observer_received_at_utc": utc_now(),
                        "observer_received_perf_counter_ns": time.perf_counter_ns(),
                    }
                )
                _check_hresult(
                    _com_method(capture, 4, HRESULT, UINT32)(capture, frames.value),
                    "IAudioCaptureClient.ReleaseBuffer",
                )
                next_frames = UINT32()
                _check_hresult(
                    _com_method(capture, 5, HRESULT, ctypes.POINTER(UINT32))(
                        capture, ctypes.byref(next_frames)
                    ),
                    "IAudioCaptureClient.GetNextPacketSize",
                )
        finished_at = utc_now()
        pcm_path.write_bytes(pcm)
        result = {
            **ready,
            "capture_finished_at_utc": finished_at,
            "capture_duration_requested_seconds": duration_seconds,
            "packet_count": len(packets),
            "total_frame_count": sum(item["frame_count"] for item in packets),
            "total_byte_count": len(pcm),
            "pcm_sha256": hashlib.sha256(pcm).hexdigest(),
            "silent_packet_count": sum(item["silent"] for item in packets),
            "data_discontinuity_packet_count": sum(
                item["data_discontinuity"] for item in packets
            ),
            "timestamp_error_packet_count": sum(item["timestamp_error"] for item in packets),
            "packets": packets,
            "raw_pcm_path_role": "ephemeral evaluator input",
            "raw_pcm_persisted": False,
        }
        result_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        return result
    except Exception as exc:
        failure = {
            "observer": OBSERVER,
            "observer_version": OBSERVER_VERSION,
            "watcher_pid": os.getpid(),
            "endpoint_id_requested": endpoint_id,
            "capture_started_at_utc": started_at,
            "capture_finished_at_utc": finished_at or utc_now(),
            "status": "failed",
            "error": str(exc),
            "semantic_condition_received": False,
            "playback_metadata_received": False,
        }
        result_path.write_text(json.dumps(failure, indent=2, sort_keys=True), encoding="utf-8")
        raise
    finally:
        if started and client.value:
            _com_method(client, 11, HRESULT)(client)
        _release(capture)
        if mix_pointer.value:
            ole.CoTaskMemFree(mix_pointer)
        _release(client)
        _release(device)
        _release(enumerator)
        if initialized:
            ole.CoUninitialize()


def build_tone_pcm(
    frequency_hz: float,
    amplitude_full_scale: float,
    duration_seconds: float = TONE_SECONDS,
) -> tuple[bytes, dict[str, Any]]:
    if not 0.0 <= amplitude_full_scale <= 0.005:
        raise ValueError("bounded loopback pressure amplitude must be in [0, 0.005]")
    frame_count = round(SAMPLE_RATE * duration_seconds)
    output = bytearray()
    for index in range(frame_count):
        if amplitude_full_scale == 0.0 or frequency_hz == 0.0:
            sample = 0
        else:
            window = math.sin(math.pi * index / max(frame_count - 1, 1)) ** 2
            sample = round(
                32767
                * amplitude_full_scale
                * window
                * math.sin(2.0 * math.pi * frequency_hz * index / SAMPLE_RATE)
            )
        output.extend(struct.pack("<hh", sample, sample))
    raw = bytes(output)
    return raw, {
        "kind": "stereo_hann_windowed_sine" if frequency_hz else "stereo_digital_silence",
        "frequency_hz": frequency_hz,
        "sample_rate_hz": SAMPLE_RATE,
        "channel_count": CHANNEL_COUNT,
        "sample_representation": "signed_pcm_16_little_endian",
        "duration_seconds": duration_seconds,
        "frame_count": frame_count,
        "amplitude_full_scale": amplitude_full_scale,
        "nominal_level_dbfs": (
            round(20.0 * math.log10(amplitude_full_scale), 6)
            if amplitude_full_scale > 0
            else None
        ),
        "command_pcm_sha256": hashlib.sha256(raw).hexdigest(),
    }


def emit_tone(
    output_device_id: int,
    frequency_hz: float,
    amplitude_full_scale: float,
) -> dict[str, Any]:
    raw, parameters = build_tone_pcm(frequency_hz, amplitude_full_scale)
    backend = _WinMMBackend()
    started_at = utc_now()
    backend._play(raw, output_device_id, backend._format(SAMPLE_RATE))
    return {
        "emitter_pid": os.getpid(),
        "backend": "Windows WinMM waveOut",
        "output_device_id": output_device_id,
        "submitted_at_utc": started_at,
        "completed_at_utc": utc_now(),
        "waveout_completed": True,
        "parameters": parameters,
    }


def _decode_pcm(raw: bytes, mix: dict[str, Any]) -> list[list[float]]:
    channels = int(mix["channel_count"])
    align = int(mix["block_align_bytes"])
    bits = int(mix["container_bits_per_sample"])
    representation = mix["sample_representation"]
    usable = len(raw) - (len(raw) % align)
    values = [[] for _ in range(channels)]
    if usable == 0:
        return values
    if representation == "float32_little_endian":
        frame_format = "<" + "f" * channels
        for frame in struct.iter_unpack(frame_format, raw[:usable]):
            for channel, value in enumerate(frame):
                values[channel].append(float(value))
        return values
    if representation == "signed_pcm_16_little_endian":
        frame_format = "<" + "h" * channels
        for frame in struct.iter_unpack(frame_format, raw[:usable]):
            for channel, value in enumerate(frame):
                values[channel].append(value / 32768.0)
        return values
    if representation == "signed_pcm_32_little_endian":
        frame_format = "<" + "i" * channels
        for frame in struct.iter_unpack(frame_format, raw[:usable]):
            for channel, value in enumerate(frame):
                values[channel].append(value / 2147483648.0)
        return values
    if representation == "signed_pcm_24_little_endian":
        for offset in range(0, usable, align):
            for channel in range(channels):
                start = offset + channel * 3
                integer = int.from_bytes(raw[start : start + 3], "little", signed=False)
                if integer & 0x800000:
                    integer -= 1 << 24
                values[channel].append(integer / 8388608.0)
        return values
    raise ValueError(f"unsupported sample representation {representation}")


def derive_pcm_measurements(raw: bytes, mix: dict[str, Any]) -> dict[str, Any]:
    channels = _decode_pcm(raw, mix)
    sample_rate = int(mix["sample_rate_hz"])
    per_channel = []
    for index, samples in enumerate(channels):
        if samples:
            rms = math.sqrt(sum(value * value for value in samples) / len(samples))
            peak = max(abs(value) for value in samples)
        else:
            rms = 0.0
            peak = 0.0
        spectral = {
            str(int(frequency)): _single_frequency_rms(samples, sample_rate, frequency)
            for frequency in FREQUENCIES_HZ.values()
        }
        per_channel.append(
            {
                "channel_index": index,
                "frame_count": len(samples),
                "rms_full_scale": rms,
                "peak_abs_full_scale": peak,
                "single_frequency_rms": spectral,
            }
        )
    combined = {}
    for frequency in FREQUENCIES_HZ.values():
        key = str(int(frequency))
        components = [item["single_frequency_rms"][key] for item in per_channel]
        combined[key] = (
            math.sqrt(sum(value * value for value in components) / len(components))
            if components
            else 0.0
        )
    return {
        "measurement_version": "whole_capture_single_frequency_projection_v0",
        "frame_count": len(channels[0]) if channels else 0,
        "per_channel": per_channel,
        "combined_single_frequency_rms": combined,
    }


def _single_frequency_rms(samples: list[float], sample_rate: int, frequency: float) -> float:
    if not samples:
        return 0.0
    omega = 2.0 * math.pi * frequency / sample_rate
    cosine = 0.0
    sine = 0.0
    for index, sample in enumerate(samples):
        cosine += sample * math.cos(omega * index)
        sine += sample * math.sin(omega * index)
    peak_amplitude = 2.0 * math.hypot(cosine, sine) / len(samples)
    return peak_amplitude / math.sqrt(2.0)


def materialize_trial_order() -> list[str]:
    generated = random.Random(TRIAL_SEED).sample(
        ["C0"] * 5 + ["S1"] * 5 + ["S2"] * 5, 15
    )
    if tuple(generated) != TRIAL_ORDER:
        raise RuntimeError("frozen loopback trial order no longer matches seed")
    return generated


def frozen_discrimination_basis() -> dict[str, Any]:
    return {
        "declared_before_primary_acquisition": True,
        "frequencies_hz": FREQUENCIES_HZ,
        "primary_amplitude_full_scale": PRIMARY_AMPLITUDE,
        "nominal_primary_level_dbfs": round(20 * math.log10(PRIMARY_AMPLITUDE), 6),
        "tone_duration_seconds": TONE_SECONDS,
        "capture_duration_seconds": CAPTURE_SECONDS,
        "pre_roll_seconds": PRE_ROLL_SECONDS,
        "randomization_seed": TRIAL_SEED,
        "trial_order": materialize_trial_order(),
        "measurement": "whole-capture single-frequency RMS projection, combined across endpoint channels",
        "requirements": {
            "median_commanded_frequency_dominance_db": MEDIAN_DOMINANCE_DB,
            "minimum_each_commanded_trial_dominance_db": MINIMUM_TRIAL_DOMINANCE_DB,
            "median_commanded_target_over_same_frequency_C0_db": TARGET_OVER_CONTROL_DB,
            "maximum_C0_trials_imitating_each_command": MAX_CONTROL_IMITATIONS,
        },
        "no_trial_exclusion": True,
        "exact_pcm_equality_required": False,
    }


def _db_ratio(numerator: float, denominator: float) -> float:
    floor = 1e-15
    return 20.0 * math.log10(max(numerator, floor) / max(denominator, floor))


def evaluate_primary_trials(trials: list[dict[str, Any]]) -> dict[str, Any]:
    if [trial["condition"] for trial in trials] != materialize_trial_order():
        raise ValueError("trials do not follow the frozen primary order")
    values: dict[str, list[dict[str, float]]] = {"C0": [], "S1": [], "S2": []}
    for trial in trials:
        combined = trial["observation"]["measurements"]["combined_single_frequency_rms"]
        values[trial["condition"]].append(
            {"900": float(combined["900"]), "1500": float(combined["1500"])}
        )
    summaries: dict[str, Any] = {}
    for condition, rows in values.items():
        summaries[condition] = {
            frequency: {
                "values": [row[frequency] for row in rows],
                "minimum": min(row[frequency] for row in rows),
                "maximum": max(row[frequency] for row in rows),
                "median": median(row[frequency] for row in rows),
            }
            for frequency in ("900", "1500")
        }
    dominance = {
        "S1": [_db_ratio(row["900"], row["1500"]) for row in values["S1"]],
        "S2": [_db_ratio(row["1500"], row["900"]) for row in values["S2"]],
    }
    target_over_control = {
        "S1_900": _db_ratio(
            summaries["S1"]["900"]["median"], summaries["C0"]["900"]["median"]
        ),
        "S2_1500": _db_ratio(
            summaries["S2"]["1500"]["median"], summaries["C0"]["1500"]["median"]
        ),
    }
    command_medians = {
        "S1": summaries["S1"]["900"]["median"],
        "S2": summaries["S2"]["1500"]["median"],
    }
    control_imitation = {
        "S1": sum(
            _db_ratio(row["900"], row["1500"]) >= MEDIAN_DOMINANCE_DB
            and row["900"] >= command_medians["S1"] / 4.0
            for row in values["C0"]
        ),
        "S2": sum(
            _db_ratio(row["1500"], row["900"]) >= MEDIAN_DOMINANCE_DB
            and row["1500"] >= command_medians["S2"] / 4.0
            for row in values["C0"]
        ),
    }
    packet_basis_ok = all(
        trial["observation"]["packet_count"] > 0
        for trial in trials
        if trial["condition"] in {"S1", "S2"}
    )
    criteria = {
        "S1_median_dominance": median(dominance["S1"]) >= MEDIAN_DOMINANCE_DB,
        "S2_median_dominance": median(dominance["S2"]) >= MEDIAN_DOMINANCE_DB,
        "S1_each_trial_dominance": min(dominance["S1"]) >= MINIMUM_TRIAL_DOMINANCE_DB,
        "S2_each_trial_dominance": min(dominance["S2"]) >= MINIMUM_TRIAL_DOMINANCE_DB,
        "S1_target_over_C0": target_over_control["S1_900"] >= TARGET_OVER_CONTROL_DB,
        "S2_target_over_C0": target_over_control["S2_1500"] >= TARGET_OVER_CONTROL_DB,
        "C0_not_systematic_S1": control_imitation["S1"] <= MAX_CONTROL_IMITATIONS,
        "C0_not_systematic_S2": control_imitation["S2"] <= MAX_CONTROL_IMITATIONS,
        "all_commanded_trials_have_packets": packet_basis_ok,
    }
    return {
        "basis": frozen_discrimination_basis(),
        "condition_summaries": summaries,
        "commanded_frequency_dominance_db": dominance,
        "target_over_control_db": target_over_control,
        "C0_command_imitation_counts": control_imitation,
        "criteria": criteria,
        "discriminated": all(criteria.values()),
    }


def _watcher_command(
    endpoint_id: str,
    duration_seconds: float,
    ready_path: Path,
    result_path: Path,
    pcm_path: Path,
) -> list[str]:
    return [
        sys.executable,
        "-m",
        "src.runtime.wasapi_loopback_witness_validation",
        "watch",
        "--endpoint-id",
        endpoint_id,
        "--duration",
        str(duration_seconds),
        "--ready-path",
        str(ready_path),
        "--result-path",
        str(result_path),
        "--pcm-path",
        str(pcm_path),
    ]


def _emitter_command(
    output_device_id: int, frequency_hz: float, amplitude: float
) -> list[str]:
    return [
        sys.executable,
        "-m",
        "src.runtime.wasapi_loopback_witness_validation",
        "emit",
        "--output-device-id",
        str(output_device_id),
        "--frequency",
        str(frequency_hz),
        "--amplitude",
        str(amplitude),
    ]


def _run_observation(
    base: Path,
    ordinal: str,
    endpoint_id: str,
    output_device_id: int,
    *,
    emission: tuple[float, float] | None,
) -> dict[str, Any]:
    ready_path = base / f"{ordinal}.ready.json"
    result_path = base / f"{ordinal}.watcher.json"
    pcm_path = base / f"{ordinal}.pcm"
    watcher_command = _watcher_command(
        endpoint_id, CAPTURE_SECONDS, ready_path, result_path, pcm_path
    )
    watcher = subprocess.Popen(
        watcher_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    deadline = time.perf_counter() + 8.0
    while not ready_path.exists() and watcher.poll() is None:
        if time.perf_counter() > deadline:
            watcher.kill()
            raise RuntimeError("WASAPI watcher did not reach ready state")
        time.sleep(0.01)
    if not ready_path.exists():
        stdout, stderr = watcher.communicate(timeout=2)
        failure = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else None
        raise RuntimeError(f"watcher failed before ready: {failure}; stdout={stdout!r}; stderr={stderr!r}")
    ready = json.loads(ready_path.read_text(encoding="utf-8"))
    emitter_result = None
    if emission is not None:
        frequency, amplitude = emission
        target = time.perf_counter() + PRE_ROLL_SECONDS
        while time.perf_counter() < target:
            time.sleep(min(target - time.perf_counter(), 0.005))
        completed = subprocess.run(
            _emitter_command(output_device_id, frequency, amplitude),
            check=True,
            capture_output=True,
            text=True,
        )
        emitter_result = json.loads(completed.stdout)
    stdout, stderr = watcher.communicate(timeout=CAPTURE_SECONDS + 8.0)
    if watcher.returncode != 0:
        failure = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else None
        raise RuntimeError(f"watcher failed: {failure}; stdout={stdout!r}; stderr={stderr!r}")
    observed = json.loads(result_path.read_text(encoding="utf-8"))
    raw = pcm_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != observed["pcm_sha256"]:
        raise RuntimeError("watcher PCM hash mismatch")
    measurements = derive_pcm_measurements(raw, observed["mix_format"])
    pcm_path.unlink()
    return {
        "ready": ready,
        "watcher_command_boundary": {
            "semantic_condition_received": False,
            "frequency_or_waveform_metadata_received": False,
            "received_endpoint_id": True,
            "received_duration_and_artifact_paths": True,
        },
        "observation": {**observed, "measurements": measurements},
        "emitter": emitter_result,
        "condition_joined_after_capture": True,
        "raw_pcm_deleted_after_hash_and_measurement": not pcm_path.exists(),
    }


def _git_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, encoding="utf-8"
        ).strip()
    except Exception:
        return None


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> dict[str, Any]:
    started_at = utc_now()
    canonical_path = Path("traces") / "live_ingest_ledger_v0.jsonl"
    canonical_before = _file_sha256(canonical_path)
    endpoints = enumerate_render_endpoints()
    selected = select_realtek_endpoint(endpoints)
    winmm = _WinMMBackend()
    output_devices = winmm.output_devices()
    output_device = _select_named_device(
        output_devices, ("Speakers", "Realtek"), "room stereo playback device"
    )
    implementation_hash = _file_sha256(Path(__file__))
    with TemporaryDirectory(prefix="dme-wasapi-loopback-") as temporary:
        base = Path(temporary)
        no_render_gate = _run_observation(
            base,
            "gate-no-render",
            selected["endpoint_id"],
            output_device["device_id"],
            emission=None,
        )
        gate = no_render_gate
        silent_render_gate = None
        if gate["observation"]["packet_count"] == 0:
            silent_render_gate = _run_observation(
                base,
                "gate-silent-render",
                selected["endpoint_id"],
                output_device["device_id"],
                emission=(0.0, 0.0),
            )
            gate = silent_render_gate
        packet_gate_succeeded = gate["observation"]["packet_count"] > 0
        preflight = []
        primary = []
        if packet_gate_succeeded:
            for condition in ("S1", "S2"):
                observation = _run_observation(
                    base,
                    f"preflight-{condition}",
                    selected["endpoint_id"],
                    output_device["device_id"],
                    emission=(FREQUENCIES_HZ[condition], PREFLIGHT_AMPLITUDE),
                )
                observation["condition"] = condition
                observation["condition_joined_at_utc"] = utc_now()
                preflight.append(observation)
            for index, condition in enumerate(materialize_trial_order(), start=1):
                emission = None
                if condition in FREQUENCIES_HZ:
                    emission = (FREQUENCIES_HZ[condition], PRIMARY_AMPLITUDE)
                observation = _run_observation(
                    base,
                    f"primary-{index:02d}",
                    selected["endpoint_id"],
                    output_device["device_id"],
                    emission=emission,
                )
                observation["trial_sequence_index"] = index
                observation["condition"] = condition
                observation["condition_joined_at_utc"] = utc_now()
                primary.append(observation)

    analysis = evaluate_primary_trials(primary) if primary else None
    all_observations = [no_render_gate]
    if silent_render_gate is not None:
        all_observations.append(silent_render_gate)
    all_observations.extend(preflight)
    all_observations.extend(primary)
    watcher_pids = [item["observation"]["watcher_pid"] for item in all_observations]
    endpoint_reacquired = bool(primary) and all(
        item["observation"]["endpoint"]["endpoint_id"] == selected["endpoint_id"]
        and item["observation"]["endpoint"]["friendly_name"] == selected["friendly_name"]
        for item in primary
    )
    mix_reacquired = bool(primary) and len(
        {item["observation"]["mix_format"]["format_bytes_sha256"] for item in primary}
    ) == 1
    fresh_process_reacquisition = (
        endpoint_reacquired
        and mix_reacquired
        and len(set(watcher_pids)) == len(watcher_pids)
        and all(pid != os.getpid() for pid in watcher_pids)
    )
    acquisition_failures = [
        item
        for item in all_observations
        if item["observation"].get("status") == "failed"
    ]
    if not packet_gate_succeeded:
        status = "post_mix_loopback_witness_unavailable"
    elif acquisition_failures or not primary or not fresh_process_reacquisition:
        status = "post_mix_loopback_witness_evidence_insufficient"
    elif analysis is not None and analysis["discriminated"]:
        status = "post_mix_loopback_witness_validated"
    else:
        status = "post_mix_loopback_witness_present_but_nondiscriminating"
    return {
        "experiment": EXPERIMENT,
        "primary_status": status,
        "repository_starting_ref": _git_head(),
        "started_at_utc": started_at,
        "finished_at_utc": utc_now(),
        "host": {
            "platform": platform.platform(),
            "windows_version": platform.version(),
            "machine": platform.machine(),
            "python": sys.version,
            "process_is_64_bit": struct.calcsize("P") == 8,
        },
        "observer": {
            "identity": OBSERVER,
            "version": OBSERVER_VERSION,
            "implementation_path": str(Path(__file__).as_posix()),
            "implementation_sha256": implementation_hash,
            "source_api": "IAudioCaptureClient.GetBuffer",
            "stream_mode": "WASAPI shared-mode loopback",
            "separate_process_required": True,
            "command_derived_witness_content": False,
        },
        "endpoint_enumeration": endpoints,
        "selected_endpoint": selected,
        "winmm_output_devices": output_devices,
        "selected_emitter_output_device": output_device,
        "packet_gate": {
            "no_render_attempt": no_render_gate,
            "silent_render_attempt": silent_render_gate,
            "succeeded": packet_gate_succeeded,
        },
        "preflight": {
            "classification": "exploratory range check; not primary evidence",
            "amplitude_full_scale": PREFLIGHT_AMPLITUDE,
            "nominal_level_dbfs": round(20 * math.log10(PREFLIGHT_AMPLITUDE), 6),
            "trials": preflight,
        },
        "frozen_primary_basis": frozen_discrimination_basis(),
        "primary_trials": primary,
        "primary_analysis": analysis,
        "process_boundary": {
            "orchestrator_pid": os.getpid(),
            "watcher_process_ids": watcher_pids,
            "unique_watcher_process_count": len(set(watcher_pids)),
            "emitter_process_ids": [
                item["emitter"]["emitter_pid"]
                for item in all_observations
                if item.get("emitter") is not None
            ],
            "watchers_received_condition_labels": False,
            "watchers_received_playback_frequency_or_waveform": False,
            "condition_labels_joined_after_capture": True,
        },
        "fresh_process_reacquisition": {
            "succeeded": fresh_process_reacquisition,
            "endpoint_id_preserved": endpoint_reacquired,
            "mix_format_preserved": mix_reacquired,
            "all_watcher_pids_unique_and_external": len(set(watcher_pids)) == len(watcher_pids)
            and all(pid != os.getpid() for pid in watcher_pids),
        },
        "endpoint_acquisition_failure_count": len(acquisition_failures),
        "raw_pcm": {
            "persisted": False,
            "per_observation_sha256_retained": True,
            "per_observation_frame_and_packet_metadata_retained": True,
        },
        "directly_observed": [
            "Core Audio endpoint identity, friendly name, and state",
            "endpoint mix format",
            "IAudioCaptureClient loopback packets and flags",
            "packet frame counts, stream positions, QPC timestamps, and observer times",
            "captured PCM bytes before deletion, their hashes, RMS, and frequency projections",
        ],
        "not_observed": [
            "specific hardware-driver receipt of the captured samples",
            "DAC voltage",
            "speaker mechanics",
            "airborne sound field",
            "microphone response or playback causality",
            "current-world state outside each bounded capture interval",
        ],
        "canonical_history": {
            "path": str(canonical_path.as_posix()),
            "sha256_before": canonical_before,
            "sha256_after": _file_sha256(canonical_path),
            "changed": canonical_before != _file_sha256(canonical_path),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=False)
    watch = subparsers.add_parser("watch")
    watch.add_argument("--endpoint-id", required=True)
    watch.add_argument("--duration", type=float, required=True)
    watch.add_argument("--ready-path", type=Path, required=True)
    watch.add_argument("--result-path", type=Path, required=True)
    watch.add_argument("--pcm-path", type=Path, required=True)
    emit = subparsers.add_parser("emit")
    emit.add_argument("--output-device-id", type=int, required=True)
    emit.add_argument("--frequency", type=float, required=True)
    emit.add_argument("--amplitude", type=float, required=True)
    args = parser.parse_args()
    if args.command == "watch":
        watch_endpoint(
            args.endpoint_id,
            args.duration,
            args.ready_path,
            args.result_path,
            args.pcm_path,
        )
        return
    if args.command == "emit":
        print(json.dumps(emit_tone(args.output_device_id, args.frequency, args.amplitude)))
        return
    report = run()
    TRACE_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "primary_status": report["primary_status"],
        "selected_endpoint": report["selected_endpoint"],
        "mix_format": (
            report["primary_trials"][0]["observation"]["mix_format"]
            if report["primary_trials"]
            else None
        ),
        "watcher_process_count": report["process_boundary"]["unique_watcher_process_count"],
        "analysis": report["primary_analysis"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
