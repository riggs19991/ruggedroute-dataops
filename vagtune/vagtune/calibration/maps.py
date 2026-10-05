"""
Calibration maps (tables).

A tuning "map" is a block of numbers in the flash image - 1D (curve) or 2D (table) -
stored as raw integers that must be scaled to physical units with a linear transform
``physical = raw * factor + offset``. The axes (breakpoints) are stored the same way.

This module gives you:

* :class:`ScalarValue`  - a single scaled number (e.g. a rev limiter).
* :class:`Axis`         - a 1D list of scaled breakpoints.
* :class:`Map`          - an N x M table of scaled values with optional axes.

All of them read from and write back to a :class:`~vagtune.calibration.image.FlashImage`,
converting between raw storage and physical units, clamping to the storage range so an
edit can never silently corrupt neighbouring bytes.

Definitions (where each map lives, its size, scaling) come from JSON definition files;
see :mod:`vagtune.calibration.definition`.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from .image import FlashImage

# struct format per (dtype) -> (struct char, size, signed, min, max)
_DTYPES = {
    "u8":  ("B", 1, False, 0, 0xFF),
    "s8":  ("b", 1, True, -0x80, 0x7F),
    "u16": ("H", 2, False, 0, 0xFFFF),
    "s16": ("h", 2, True, -0x8000, 0x7FFF),
    "u32": ("I", 4, False, 0, 0xFFFFFFFF),
    "s32": ("i", 4, True, -0x80000000, 0x7FFFFFFF),
    "f32": ("f", 4, True, float("-inf"), float("inf")),
}


def _endian_char(endian: str) -> str:
    return "<" if endian == "little" else ">"


@dataclass
class Scaling:
    dtype: str = "u16"
    factor: float = 1.0
    offset: float = 0.0
    endian: str = "big"          # VAG Tricore ECUs are big-endian in most cal data
    unit: str = ""

    def __post_init__(self) -> None:
        if self.dtype not in _DTYPES:
            raise ValueError(f"unknown dtype {self.dtype!r}; known: {', '.join(_DTYPES)}")

    @property
    def size(self) -> int:
        return _DTYPES[self.dtype][1]

    def raw_to_phys(self, raw: int) -> float:
        return raw * self.factor + self.offset

    def phys_to_raw(self, phys: float) -> int:
        _, _, is_float, lo, hi = _DTYPES[self.dtype]
        if self.dtype == "f32":
            return phys  # stored as float; struct handles it
        raw = round((phys - self.offset) / self.factor)
        return max(lo, min(hi, raw))

    def unpack(self, buf: bytes) -> float:
        fmt = _endian_char(self.endian) + _DTYPES[self.dtype][0]
        return struct.unpack(fmt, buf)[0]

    def pack(self, raw) -> bytes:
        fmt = _endian_char(self.endian) + _DTYPES[self.dtype][0]
        return struct.pack(fmt, raw)


@dataclass
class ScalarValue:
    name: str
    address: int
    scaling: Scaling = field(default_factory=Scaling)
    description: str = ""

    def read(self, image: FlashImage) -> float:
        buf = image.read_at_address(self.address, self.scaling.size)
        return self.scaling.raw_to_phys(self.scaling.unpack(buf))

    def write(self, image: FlashImage, phys: float) -> None:
        raw = self.scaling.phys_to_raw(phys)
        image.write_at_address(self.address, self.scaling.pack(raw))


@dataclass
class Axis:
    name: str
    address: int
    count: int
    scaling: Scaling = field(default_factory=Scaling)
    unit: str = ""

    def read(self, image: FlashImage) -> List[float]:
        out = []
        sz = self.scaling.size
        for i in range(self.count):
            buf = image.read_at_address(self.address + i * sz, sz)
            out.append(self.scaling.raw_to_phys(self.scaling.unpack(buf)))
        return out

    def write(self, image: FlashImage, values: Sequence[float]) -> None:
        if len(values) != self.count:
            raise ValueError(f"axis {self.name}: expected {self.count} values, got {len(values)}")
        sz = self.scaling.size
        for i, v in enumerate(values):
            raw = self.scaling.phys_to_raw(v)
            image.write_at_address(self.address + i * sz, self.scaling.pack(raw))


@dataclass
class Map:
    """A 1D or 2D calibration table.

    Layout is row-major: ``rows`` = y-axis length, ``cols`` = x-axis length. For a 1D
    map set ``rows = 1``. Cell (r, c) is stored at ``address + (r*cols + c)*size``.
    """
    name: str
    address: int
    rows: int
    cols: int
    scaling: Scaling = field(default_factory=Scaling)
    x_axis: Optional[Axis] = None
    y_axis: Optional[Axis] = None
    description: str = ""

    @property
    def cell_count(self) -> int:
        return self.rows * self.cols

    def _cell_address(self, r: int, c: int) -> int:
        return self.address + (r * self.cols + c) * self.scaling.size

    def read(self, image: FlashImage) -> List[List[float]]:
        table: List[List[float]] = []
        sz = self.scaling.size
        for r in range(self.rows):
            row: List[float] = []
            for c in range(self.cols):
                buf = image.read_at_address(self._cell_address(r, c), sz)
                row.append(self.scaling.raw_to_phys(self.scaling.unpack(buf)))
            table.append(row)
        return table

    def read_cell(self, image: FlashImage, r: int, c: int) -> float:
        buf = image.read_at_address(self._cell_address(r, c), self.scaling.size)
        return self.scaling.raw_to_phys(self.scaling.unpack(buf))

    def write_cell(self, image: FlashImage, r: int, c: int, phys: float) -> None:
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError(f"cell ({r},{c}) outside map {self.name} ({self.rows}x{self.cols})")
        raw = self.scaling.phys_to_raw(phys)
        image.write_at_address(self._cell_address(r, c), self.scaling.pack(raw))

    def write(self, image: FlashImage, table: Sequence[Sequence[float]]) -> None:
        if len(table) != self.rows or any(len(row) != self.cols for row in table):
            raise ValueError(f"map {self.name}: expected {self.rows}x{self.cols} table")
        for r in range(self.rows):
            for c in range(self.cols):
                self.write_cell(image, r, c, table[r][c])

    def scale_all(self, image: FlashImage, multiplier: float,
                  clamp_phys: Optional[float] = None) -> None:
        """Multiply every cell by ``multiplier`` (e.g. 1.10 for +10% across the map).

        If ``clamp_phys`` is given, no cell is written above that physical value - a
        crude but useful safety rail for things like a boost-target ceiling.
        """
        for r in range(self.rows):
            for c in range(self.cols):
                v = self.read_cell(image, r, c) * multiplier
                if clamp_phys is not None:
                    v = min(v, clamp_phys)
                self.write_cell(image, r, c, v)

    def as_text(self, image: FlashImage) -> str:
        """Render the map as a readable grid with axis labels (for CLI display)."""
        table = self.read(image)
        xs = self.x_axis.read(image) if self.x_axis else list(range(self.cols))
        ys = self.y_axis.read(image) if self.y_axis else list(range(self.rows))
        lines = [f"{self.name}  [{self.rows}x{self.cols}] unit={self.scaling.unit or '-'}"]
        header = "        " + " ".join(f"{x:8.1f}" for x in xs)
        lines.append(header)
        for r in range(self.rows):
            row_label = f"{ys[r]:8.1f}" if self.y_axis else f"{r:8d}"
            cells = " ".join(f"{table[r][c]:8.2f}" for c in range(self.cols))
            lines.append(f"{row_label} {cells}")
        return "\n".join(lines)
