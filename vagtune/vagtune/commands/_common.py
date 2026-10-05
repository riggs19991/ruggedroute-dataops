"""
Shared CLI plumbing: common arguments, context opening, module token resolution.

``--module`` accepts either a module *name* from :data:`vagtune.vag.modules.MODULES`
(``engine``, ``gateway``, ...) or a VAG diagnostic *address word* (``01``, ``0x19``,
``19``). The address-word table here is deliberately minimal and will be replaced by
``vag/addresses.py`` (the full table) by another slice; it only has to cover the
modules ``vag/modules.py`` already knows.
"""

from __future__ import annotations

import argparse
import logging
from typing import Dict, Optional, Tuple

from ..transport.context import TransportContext
from ..transport.fakebus import SimulatedVehicle
from ..uds.client import UdsClient, UdsTiming
from ..vag import modules as vag_modules
from ..vag.ecu import VagEcuSession
from ..vag.profiles import get_profile

log = logging.getLogger(__name__)

# address word -> (module name, request id, response id). Minimal on purpose; see
# module docstring. Kept consistent with vag/modules.py.
ADDRESS_WORDS: Dict[str, Tuple[str, int, int]] = {
    "01": ("engine", 0x7E0, 0x7E8),
    "02": ("transmission", 0x7E1, 0x7E9),
    "03": ("abs", 0x713, 0x77D),
    "19": ("gateway", 0x710, 0x77A),
    "22": ("haldex", 0x70F, 0x779),
}


def resolve_module(token: str) -> vag_modules.ModuleAddress:
    """Map a ``--module`` token to a :class:`~vagtune.vag.modules.ModuleAddress`.

    Accepts module names (case-insensitive) and address words as ``01``, ``1``,
    ``0x19`` or ``19`` (hex). Raises ``ValueError`` listing the accepted tokens.
    """
    raw = token.strip()
    key = raw.lower()
    if key in vag_modules.MODULES:
        return vag_modules.MODULES[key]
    word = key[2:] if key.startswith("0x") else key
    if word and all(c in "0123456789abcdef" for c in word):
        word = word.zfill(2)
        if word in ADDRESS_WORDS:
            name, req, resp = ADDRESS_WORDS[word]
            mod = vag_modules.MODULES.get(name)
            if mod is not None and (mod.request_id, mod.response_id) == (req, resp):
                return mod
            return vag_modules.ModuleAddress(name, req, resp, f"address word {word}")
    names = ", ".join(sorted(vag_modules.MODULES))
    words = ", ".join(sorted(ADDRESS_WORDS))
    raise ValueError(f"unknown module {raw!r}; use a name ({names}) or an address word ({words})")


def _module_arg(token: str) -> vag_modules.ModuleAddress:
    try:
        return resolve_module(token)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def add_common_args(parser: argparse.ArgumentParser) -> None:
    """Attach the transport + module options every car-facing command shares."""
    parser.add_argument("--transport", choices=list(TransportContext.KINDS), default="fake",
                        help="backend (default: fake, no hardware required; j2534 = raw CAN via "
                             "pass-thru, j2534-fw = device-side ISO-TP, best for flashing)")
    parser.add_argument("--dll", default=None, help="J2534 DLL path (or VAGTUNE_J2534_DLL)")
    parser.add_argument("--can-interface", default="socketcan", help="python-can interface")
    parser.add_argument("--can-channel", default="can0", help="python-can channel")
    parser.add_argument("--vehicle", default=None, metavar="PRESET",
                        help="simulated vehicle preset for --transport fake "
                             f"(one of: {', '.join(SimulatedVehicle.available_presets())}; default: demo)")
    parser.add_argument("--module", default="engine", type=_module_arg, metavar="TOKEN",
                        help="control module to address: a name "
                             f"({', '.join(sorted(vag_modules.MODULES))}) or a VAG address word "
                             f"({', '.join(sorted(ADDRESS_WORDS))}); default: engine")


def open_context(args: argparse.Namespace) -> TransportContext:
    """Build the :class:`TransportContext` described by the common arguments."""
    return TransportContext(
        args.transport,
        dll_path=getattr(args, "dll", None),
        can_interface=getattr(args, "can_interface", "socketcan"),
        can_channel=getattr(args, "can_channel", "can0"),
        vehicle_preset=getattr(args, "vehicle", None),
    )


def open_session(ctx: TransportContext, module: vag_modules.ModuleAddress, *,
                 profile_key: Optional[str] = None,
                 timing: Optional[UdsTiming] = None) -> VagEcuSession:
    """A :class:`VagEcuSession` on a fresh ISO-TP link to ``module``.

    The caller closes it with ``session.client.close()`` (which releases the link).
    """
    link = ctx.isotp_link(module.request_id, module.response_id)
    client = UdsClient(link, timing)
    profile = get_profile(profile_key) if profile_key else None
    return VagEcuSession(client, profile)
