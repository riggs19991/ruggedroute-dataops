"""
CLI subcommand areas.

Each area module in this package exposes ``register(sub, add_common_args)``: it adds
its subparsers to ``sub`` (an ``argparse`` subparsers action) and uses
``add_common_args`` to attach the shared transport/module options where a command
talks to the car.

Area modules are discovered automatically (every public module in this package that
defines ``register``), so adding a command area means adding one file and nothing
else. Help ordering follows the module's optional integer ``ORDER`` attribute
(lower first, default 100), then the module name. ``print()`` is allowed in this
package only.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import Callable, List, Tuple

Registrar = Callable[..., None]


def _discover() -> Tuple[Registrar, ...]:
    found: List[Tuple[int, str, Registrar]] = []
    for info in pkgutil.iter_modules(__path__):
        name = info.name
        if name.startswith("_"):
            continue
        module = importlib.import_module(f"{__name__}.{name}")
        register = getattr(module, "register", None)
        if register is None:
            continue
        order = int(getattr(module, "ORDER", 100))
        found.append((order, name, register))
    found.sort(key=lambda item: (item[0], item[1]))
    return tuple(reg for _, _, reg in found)


REGISTRARS: Tuple[Registrar, ...] = _discover()

__all__ = ["REGISTRARS", "Registrar"]
