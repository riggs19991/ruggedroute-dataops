"""
Packaged data files (``dtc_db.json``).

Read them through :func:`open_data` / :func:`read_json` so the lookup works from a
checkout, an installed wheel and a zipped package alike (``importlib.resources``).
"""

from __future__ import annotations

import json
from importlib import resources
from typing import Any, BinaryIO, Iterator, List
from contextlib import contextmanager

DTC_DB_FILENAME = "dtc_db.json"


@contextmanager
def open_data(name: str) -> Iterator[BinaryIO]:
    """Open a packaged data file in binary mode."""
    ref = resources.files(__name__).joinpath(name)
    if not ref.is_file():
        raise FileNotFoundError(f"packaged data file {name!r} is missing from vagtune.data "
                                f"(run tools/build_dtc_db.py or reinstall the package)")
    with ref.open("rb") as fh:
        yield fh


def read_json(name: str) -> Any:
    with open_data(name) as fh:
        return json.load(fh)


def data_size(name: str) -> int:
    ref = resources.files(__name__).joinpath(name)
    if not ref.is_file():
        raise FileNotFoundError(name)
    with ref.open("rb") as fh:
        fh.seek(0, 2)
        return fh.tell()


def list_data() -> List[str]:
    return sorted(p.name for p in resources.files(__name__).iterdir()
                  if p.is_file() and not p.name.startswith("__"))
