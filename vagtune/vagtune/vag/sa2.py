"""
VAG SA2 security seed/key interpreter.

Modern Volkswagen Group ECUs protect UDS SecurityAccess with the "SA2" scheme: the
ECU does not use a fixed algorithm, it ships a short *bytecode program* (the SA2
script, distributed inside the ODX/ASAM flash container) that the tester must run
over the 4-byte seed to produce the 4-byte key. Genuine tools (ODIS) and community
tools read this script and execute it. Implementing the little virtual machine is
what lets you answer the seed/key challenge without hard-coding per-ECU secrets.

This is an independent implementation written from the publicly documented opcode
table (the same table used by the open-source `sa2_seed_key` project, MIT licensed
by Brian Ledbetter). The algorithm is a published interoperability fact; only the
script bytes differ per ECU, and those come from the ECU's own flash container.

The VM:
  * one 32-bit accumulator register, initialized to the seed,
  * a carry flag set by shifts and by add/sub overflow/underflow,
  * a FOR/NEXT loop stack,
  * conditional/unconditional relative branches.

Opcode table (byte = opcode, some take a 4-byte or 1-byte operand):

    0x81  RSL     rotate register left through carry
    0x82  RSR     rotate register right through carry
    0x93  ADD n   register = (register + n) & 0xFFFFFFFF, carry on overflow      (operand: 4 bytes)
    0x84  SUB n   register = (register - n) & 0xFFFFFFFF, carry on underflow      (operand: 4 bytes)
    0x87  EOR n   register ^= n                                                   (operand: 4 bytes)
    0x68  FOR k   push loop with (k-1) remaining iterations                       (operand: 1 byte)
    0x49  NEXT    if iterations remain, jump back to loop start; else pop
    0x4A  BCC d   if carry clear, skip forward (d + 2) bytes                      (operand: 1 byte)
    0x6B  BRA d   unconditionally skip forward (d + 2) bytes                      (operand: 1 byte)
    0x4C  FIN     terminate; register holds the key

The result (``compute_key``) is the 32-bit key; ``compute_key_bytes`` returns it as
4 big-endian bytes, which is what UDS SecurityAccess sendKey expects.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Deque

log = logging.getLogger(__name__)

MASK32 = 0xFFFFFFFF
HIGH_BIT = 0x80000000


class Sa2Error(Exception):
    """Raised on a malformed SA2 script or an operand that runs off the tape."""


class Sa2Interpreter:
    """Executes one SA2 script. Reusable across seeds (state is reset per run)."""

    def __init__(self, script: bytes) -> None:
        if not script:
            raise Sa2Error("empty SA2 script")
        self.script = bytes(script)

    # -- public API --------------------------------------------------------------

    def compute_key(self, seed: int) -> int:
        """Run the script over a 32-bit integer seed, return the 32-bit key."""
        return _Sa2Run(self.script, seed & MASK32).execute()

    def compute_key_bytes(self, seed: bytes) -> bytes:
        """Run over a big-endian seed, return a big-endian 4-byte key."""
        if len(seed) != 4:
            # Some ECUs pad with leading zeros; accept anything <= 4 and right-align.
            if len(seed) > 4:
                raise Sa2Error(f"seed too long: {len(seed)} bytes (expected 4)")
            seed = seed.rjust(4, b"\x00")
        key = self.compute_key(int.from_bytes(seed, "big"))
        return key.to_bytes(4, "big")


class _Sa2Run:
    """Single execution; separate object so the interpreter itself stays stateless."""

    def __init__(self, tape: bytes, seed: int) -> None:
        self.tape = tape
        self.reg = seed & MASK32
        self.carry = 0
        self.ip = 0
        self.loop_start: Deque[int] = deque()
        self.loop_count: Deque[int] = deque()
        self._guard = 0
        self._guard_limit = 1_000_000  # defensive: SA2 scripts are tiny and always halt

    # -- operand fetch -----------------------------------------------------------

    def _u32_operand(self) -> int:
        operands = self.tape[self.ip + 1:self.ip + 5]
        if len(operands) != 4:
            raise Sa2Error(f"4-byte operand runs past end of script at ip={self.ip}")
        return (operands[0] << 24) | (operands[1] << 16) | (operands[2] << 8) | operands[3]

    def _u8_operand(self) -> int:
        if self.ip + 1 >= len(self.tape):
            raise Sa2Error(f"1-byte operand runs past end of script at ip={self.ip}")
        return self.tape[self.ip + 1]

    # -- opcodes -----------------------------------------------------------------

    def _rsl(self) -> None:
        self.carry = self.reg & HIGH_BIT
        self.reg = (self.reg << 1) & MASK32
        if self.carry:
            self.reg |= 0x1
        self.ip += 1

    def _rsr(self) -> None:
        self.carry = self.reg & 0x1
        self.reg >>= 1
        if self.carry:
            self.reg |= HIGH_BIT
        self.ip += 1

    def _add(self) -> None:
        n = self._u32_operand()
        total = self.reg + n
        self.carry = 1 if total > MASK32 else 0
        self.reg = total & MASK32
        self.ip += 5

    def _sub(self) -> None:
        n = self._u32_operand()
        diff = self.reg - n
        self.carry = 1 if diff < 0 else 0
        self.reg = diff & MASK32
        self.ip += 5

    def _eor(self) -> None:
        n = self._u32_operand()
        self.reg ^= n
        self.reg &= MASK32
        self.ip += 5

    def _for(self) -> None:
        iterations = self._u8_operand()
        self.loop_count.appendleft(iterations - 1)
        self.ip += 2
        self.loop_start.appendleft(self.ip)

    def _next(self) -> None:
        if not self.loop_count:
            raise Sa2Error("NEXT without matching FOR")
        if self.loop_count[0] > 0:
            self.loop_count[0] -= 1
            self.ip = self.loop_start[0]
        else:
            self.loop_count.popleft()
            self.loop_start.popleft()
            self.ip += 1

    def _bcc(self) -> None:
        skip = self._u8_operand() + 2
        if self.carry == 0:
            self.ip += skip
        else:
            self.ip += 2

    def _bra(self) -> None:
        skip = self._u8_operand() + 2
        self.ip += skip

    def _fin(self) -> None:
        self.ip += 1

    # -- run loop ----------------------------------------------------------------

    def execute(self) -> int:
        dispatch = {
            0x81: self._rsl,
            0x82: self._rsr,
            0x93: self._add,
            0x84: self._sub,
            0x87: self._eor,
            0x68: self._for,
            0x49: self._next,
            0x4A: self._bcc,
            0x6B: self._bra,
            0x4C: self._fin,
        }
        n = len(self.tape)
        while self.ip < n:
            self._guard += 1
            if self._guard > self._guard_limit:
                raise Sa2Error("SA2 script did not terminate (guard limit hit)")
            opcode = self.tape[self.ip]
            handler = dispatch.get(opcode)
            if handler is None:
                raise Sa2Error(f"unknown SA2 opcode 0x{opcode:02X} at ip={self.ip}")
            handler()
        return self.reg & MASK32


def make_seed_key_fn(script: bytes):
    """Return a ``(level, seed_bytes) -> key_bytes`` callable for UdsClient.security_access.

    The level argument is accepted and ignored: on VAG the script already encodes
    everything, and the same script answers whatever level the ECU challenged.
    """
    interp = Sa2Interpreter(script)

    def seed_key_fn(level: int, seed: bytes) -> bytes:
        return interp.compute_key_bytes(seed)

    return seed_key_fn
