"""
Flash image container.

A :class:`FlashImage` wraps the raw bytes read from (or to be written to) an ECU
calibration block. It provides safe windowed read/write, keeps the original bytes so
you can diff your edits, and tracks which regions are checksum-protected so the
checksum step knows what to recompute before a write.

Nothing here understands *maps* - that is :mod:`vagtune.calibration.maps`. This layer
is just "bytes with guardrails and provenance".
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ChecksumRegion:
    """A region whose integrity is covered by a checksum stored elsewhere."""
    name: str
    start: int
    length: int
    checksum_offset: int           # where the stored checksum lives in the image
    algorithm: str = "crc32"       # "crc32" | "sum16" | "sum32" (per-ECU)

    @property
    def end(self) -> int:
        return self.start + self.length


class FlashImage:
    def __init__(self, data: bytes, *, base_address: int = 0, name: str = "image") -> None:
        self._data = bytearray(data)
        self._original = bytes(data)
        self.base_address = base_address
        self.name = name
        self.checksum_regions: List[ChecksumRegion] = []

    # -- construction ------------------------------------------------------------

    @classmethod
    def from_file(cls, path: str, *, base_address: int = 0) -> "FlashImage":
        with open(path, "rb") as fh:
            return cls(fh.read(), base_address=base_address, name=path)

    def to_file(self, path: str) -> None:
        with open(path, "wb") as fh:
            fh.write(self._data)
        log.info("wrote %d bytes to %s", len(self._data), path)

    # -- addressing --------------------------------------------------------------

    def _to_offset(self, address: int) -> int:
        """Translate an absolute ECU address to an offset within this image."""
        off = address - self.base_address
        if not 0 <= off < len(self._data):
            raise IndexError(
                f"address 0x{address:08X} outside image "
                f"[0x{self.base_address:08X}..0x{self.base_address + len(self._data):08X})"
            )
        return off

    # -- read --------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._data)

    @property
    def data(self) -> bytes:
        return bytes(self._data)

    def read(self, offset: int, length: int) -> bytes:
        if offset < 0 or offset + length > len(self._data):
            raise IndexError(f"read [{offset}:{offset + length}] out of bounds (len {len(self._data)})")
        return bytes(self._data[offset:offset + length])

    def read_at_address(self, address: int, length: int) -> bytes:
        return self.read(self._to_offset(address), length)

    # -- write -------------------------------------------------------------------

    def write(self, offset: int, payload: bytes) -> None:
        if offset < 0 or offset + len(payload) > len(self._data):
            raise IndexError(f"write [{offset}:{offset + len(payload)}] out of bounds")
        self._data[offset:offset + len(payload)] = payload

    def write_at_address(self, address: int, payload: bytes) -> None:
        self.write(self._to_offset(address), payload)

    # -- provenance / diffing ----------------------------------------------------

    @property
    def is_modified(self) -> bool:
        return bytes(self._data) != self._original

    def diff(self) -> List[Tuple[int, int, int]]:
        """Return (offset, original_byte, new_byte) for every changed byte."""
        changes: List[Tuple[int, int, int]] = []
        for i, (a, b) in enumerate(zip(self._original, self._data)):
            if a != b:
                changes.append((i, a, b))
        return changes

    def diff_summary(self) -> str:
        changes = self.diff()
        if not changes:
            return "no changes"
        lo = changes[0][0]
        hi = changes[-1][0]
        return (f"{len(changes)} byte(s) changed, span 0x{lo:X}..0x{hi:X} "
                f"(original sha1 {hashlib.sha1(self._original).hexdigest()[:12]}, "
                f"current sha1 {hashlib.sha1(bytes(self._data)).hexdigest()[:12]})")

    def reset(self) -> None:
        """Discard all edits, restoring the originally loaded bytes."""
        self._data = bytearray(self._original)

    def commit_original(self) -> None:
        """Treat the current bytes as the new baseline (after a successful flash)."""
        self._original = bytes(self._data)

    # -- checksum regions --------------------------------------------------------

    def add_checksum_region(self, region: ChecksumRegion) -> None:
        self.checksum_regions.append(region)

    def sha256(self) -> str:
        return hashlib.sha256(self._data).hexdigest()
