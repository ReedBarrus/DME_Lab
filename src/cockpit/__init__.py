"""Bounded read-only Cockpit projection helpers."""

from importlib import import_module
from typing import Any


__all__ = ["ADAPTER_VERSION", "ProjectionAdapterError", "build_projection"]


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(name)
    adapter = import_module(".projection_adapter", __name__)
    return getattr(adapter, name)
