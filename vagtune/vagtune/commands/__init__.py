"""
CLI subcommand areas.

Each area module exposes ``register(sub, add_common_args)``: it adds its subparsers
to ``sub`` (an ``argparse`` subparsers action) and uses ``add_common_args`` to attach
the shared transport/module options where a command talks to the car. ``cli.py``
iterates :data:`REGISTRARS`; adding an area means adding one entry here and nothing
else. ``print()`` is allowed in this package only.
"""

from __future__ import annotations

from typing import Callable, Tuple

from . import calibration, diag

Registrar = Callable[..., None]

REGISTRARS: Tuple[Registrar, ...] = (
    diag.register,
    calibration.register,
)

__all__ = ["REGISTRARS", "Registrar"]
