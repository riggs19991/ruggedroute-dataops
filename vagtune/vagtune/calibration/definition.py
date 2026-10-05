"""
Calibration definition files.

A *definition* is the Rosetta Stone for one ECU calibration: it says where each map
lives, how big it is, and how to scale it. It is the open-source analogue of a
commercial tool's "damos"/A2L. We store definitions as JSON so they are easy to
author, diff, and share, and so you can grow the catalogue car-by-car.

JSON shape (see ``definitions/simos18.1.example.json``):

    {
      "profile": "simos18.1",
      "name": "SIMOS18.1 community definition (example)",
      "base_address": 2158493696,        # absolute address of the CAL block start
      "scalings": {
        "boost_kpa": {"dtype": "u16", "factor": 0.1, "offset": 0, "endian": "big", "unit": "kPa"}
      },
      "scalars": [
        {"name": "rev_limit", "address": "0xA0C120", "scaling": "rpm", "description": "..."}
      ],
      "axes": [
        {"name": "rpm_axis", "address": "0xA0C200", "count": 16, "scaling": "rpm"}
      ],
      "maps": [
        {"name": "boost_target", "address": "0xA0C400", "rows": 16, "cols": 16,
         "scaling": "boost_kpa", "x_axis": "rpm_axis", "y_axis": "load_axis"}
      ]
    }

Addresses may be given as ints or hex strings. Scalings are defined once and
referenced by name from scalars/axes/maps.
"""

from __future__ import annotations

import json
import zlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .image import FlashImage
from .maps import Axis, Map, Scaling, ScalarValue


def _parse_address(value) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 0)  # handles "0x..." and decimal strings
    raise ValueError(f"invalid address {value!r}")


@dataclass
class CalibrationDefinition:
    profile: str
    name: str
    base_address: int
    scalars: Dict[str, ScalarValue] = field(default_factory=dict)
    axes: Dict[str, Axis] = field(default_factory=dict)
    maps: Dict[str, Map] = field(default_factory=dict)

    # -- loading -----------------------------------------------------------------

    @classmethod
    def from_dict(cls, doc: dict) -> "CalibrationDefinition":
        scalings: Dict[str, Scaling] = {}
        for key, s in doc.get("scalings", {}).items():
            scalings[key] = Scaling(
                dtype=s.get("dtype", "u16"),
                factor=s.get("factor", 1.0),
                offset=s.get("offset", 0.0),
                endian=s.get("endian", "big"),
                unit=s.get("unit", ""),
            )

        def resolve_scaling(ref) -> Scaling:
            if ref is None:
                return Scaling()
            if isinstance(ref, str):
                if ref not in scalings:
                    raise KeyError(f"scaling {ref!r} referenced but not defined")
                return scalings[ref]
            # inline scaling object
            return Scaling(**ref)

        axes: Dict[str, Axis] = {}
        for a in doc.get("axes", []):
            axis = Axis(
                name=a["name"],
                address=_parse_address(a["address"]),
                count=a["count"],
                scaling=resolve_scaling(a.get("scaling")),
                unit=a.get("unit", ""),
            )
            axes[axis.name] = axis

        scalars: Dict[str, ScalarValue] = {}
        for sc in doc.get("scalars", []):
            scalar = ScalarValue(
                name=sc["name"],
                address=_parse_address(sc["address"]),
                scaling=resolve_scaling(sc.get("scaling")),
                description=sc.get("description", ""),
            )
            scalars[scalar.name] = scalar

        maps: Dict[str, Map] = {}
        for m in doc.get("maps", []):
            mp = Map(
                name=m["name"],
                address=_parse_address(m["address"]),
                rows=m.get("rows", 1),
                cols=m["cols"],
                scaling=resolve_scaling(m.get("scaling")),
                x_axis=axes.get(m["x_axis"]) if m.get("x_axis") else None,
                y_axis=axes.get(m["y_axis"]) if m.get("y_axis") else None,
                description=m.get("description", ""),
            )
            maps[mp.name] = mp

        return cls(
            profile=doc["profile"],
            name=doc.get("name", doc["profile"]),
            base_address=_parse_address(doc.get("base_address", 0)),
            scalars=scalars,
            axes=axes,
            maps=maps,
        )

    @classmethod
    def from_file(cls, path: str) -> "CalibrationDefinition":
        with open(path, "r", encoding="utf-8") as fh:
            return cls.from_dict(json.load(fh))

    # -- binding to an image -----------------------------------------------------

    def open_image(self, data: bytes, name: str = "cal") -> FlashImage:
        """Wrap raw calibration bytes in a FlashImage using this definition's base."""
        return FlashImage(data, base_address=self.base_address, name=name)

    def list_maps(self) -> List[str]:
        return sorted(self.maps)

    def get_map(self, name: str) -> Map:
        if name not in self.maps:
            raise KeyError(f"map {name!r} not in definition; have: {', '.join(self.list_maps())}")
        return self.maps[name]

    def get_scalar(self, name: str) -> ScalarValue:
        if name not in self.scalars:
            raise KeyError(f"scalar {name!r} not in definition")
        return self.scalars[name]


# ---- checksum helpers ----------------------------------------------------------
# Different ECU families use different integrity checks over calibration regions.
# These are the building blocks; the per-region algorithm is named in the
# ChecksumRegion on the image. Correct checksum *locations* are ECU-specific and
# must come from the definition / reverse engineering - these just compute values.

def crc32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def sum16(data: bytes) -> int:
    return sum(data) & 0xFFFF


def sum32(data: bytes) -> int:
    total = 0
    for i in range(0, len(data) - 3, 4):
        total = (total + int.from_bytes(data[i:i + 4], "little")) & 0xFFFFFFFF
    return total


def compute_checksum(algorithm: str, data: bytes) -> int:
    algo = algorithm.lower()
    if algo == "crc32":
        return crc32(data)
    if algo == "sum16":
        return sum16(data)
    if algo == "sum32":
        return sum32(data)
    raise ValueError(f"unknown checksum algorithm {algorithm!r}")
