"""
SA2 interpreter tests.

The key correctness check: our independent implementation must produce the same
seed->key result as the reference `sa2_seed_key` opcode semantics for the documented
SIMOS18 script across many seeds. The reference implementation is reproduced inline
here (MIT-licensed by Brian Ledbetter) purely as a test oracle, so the suite is
self-contained and does not require the package to be installed.
"""

from __future__ import annotations

from collections import deque

import pytest

from vagtune.vag.sa2 import Sa2Error, Sa2Interpreter

SIMOS18_SCRIPT = bytes.fromhex(
    "6802814A10680493080820094A05872212195482499307122011824A058703112010824A0181494C"
)


# --- reference oracle (independent of our implementation) -----------------------
class _RefSa2:
    def __init__(self, tape, seed):
        self.tape = tape
        self.reg = seed & 0xFFFFFFFF
        self.carry = 0
        self.ip = 0
        self.fp = deque()
        self.fi = deque()

    def run(self):
        ops = {
            0x81: self._rsl, 0x82: self._rsr, 0x93: self._add, 0x84: self._sub,
            0x87: self._eor, 0x68: self._for, 0x49: self._next, 0x4A: self._bcc,
            0x6B: self._bra, 0x4C: self._fin,
        }
        while self.ip < len(self.tape):
            ops[self.tape[self.ip]]()
        return self.reg

    def _u32(self):
        o = self.tape[self.ip + 1:self.ip + 5]
        return o[0] << 24 | o[1] << 16 | o[2] << 8 | o[3]

    def _rsl(self):
        self.carry = self.reg & 0x80000000
        self.reg = (self.reg << 1) & 0xFFFFFFFF
        if self.carry:
            self.reg |= 1
        self.ip += 1

    def _rsr(self):
        self.carry = self.reg & 1
        self.reg >>= 1
        if self.carry:
            self.reg |= 0x80000000
        self.ip += 1

    def _add(self):
        n = self._u32(); r = self.reg + n
        self.carry = 1 if r > 0xFFFFFFFF else 0
        self.reg = r & 0xFFFFFFFF; self.ip += 5

    def _sub(self):
        n = self._u32(); r = self.reg - n
        self.carry = 1 if r < 0 else 0
        self.reg = r & 0xFFFFFFFF; self.ip += 5

    def _eor(self):
        self.reg ^= self._u32(); self.ip += 5

    def _for(self):
        self.fi.appendleft(self.tape[self.ip + 1] - 1)
        self.ip += 2
        self.fp.appendleft(self.ip)

    def _next(self):
        if self.fi[0] > 0:
            self.fi[0] -= 1
            self.ip = self.fp[0]
        else:
            self.fi.popleft(); self.fp.popleft(); self.ip += 1

    def _bcc(self):
        skip = self.tape[self.ip + 1] + 2
        self.ip += skip if self.carry == 0 else 2

    def _bra(self):
        self.ip += self.tape[self.ip + 1] + 2

    def _fin(self):
        self.ip += 1


@pytest.mark.parametrize("seed", [
    0x00000000, 0x00000001, 0xFFFFFFFF, 0x1A2B3C4D, 0xDEADBEEF,
    0x12345678, 0x80000000, 0x7FFFFFFF, 0xABCDEF01, 0x0000FFFF,
])
def test_matches_reference_oracle(seed):
    ours = Sa2Interpreter(SIMOS18_SCRIPT).compute_key(seed)
    theirs = _RefSa2(SIMOS18_SCRIPT, seed).run()
    assert ours == theirs, f"seed 0x{seed:08X}: ours 0x{ours:08X} != ref 0x{theirs:08X}"


def test_matches_reference_fuzz():
    import random
    rng = random.Random(1234)
    for _ in range(2000):
        seed = rng.randrange(0, 1 << 32)
        assert Sa2Interpreter(SIMOS18_SCRIPT).compute_key(seed) == _RefSa2(SIMOS18_SCRIPT, seed).run()


def test_bytes_roundtrip():
    interp = Sa2Interpreter(SIMOS18_SCRIPT)
    key_int = interp.compute_key(0x1A2B3C4D)
    key_bytes = interp.compute_key_bytes((0x1A2B3C4D).to_bytes(4, "big"))
    assert key_bytes == key_int.to_bytes(4, "big")


def test_short_seed_is_left_padded():
    interp = Sa2Interpreter(SIMOS18_SCRIPT)
    assert interp.compute_key_bytes(b"\x12\x34") == interp.compute_key_bytes(b"\x00\x00\x12\x34")


def test_empty_script_rejected():
    with pytest.raises(Sa2Error):
        Sa2Interpreter(b"")


def test_unknown_opcode_rejected():
    with pytest.raises(Sa2Error):
        Sa2Interpreter(bytes([0xFF])).compute_key(0)


def test_simple_eor_program():
    # EEOR 0x0000FFFF then FIN: key = seed ^ 0x0000FFFF
    script = bytes([0x87, 0x00, 0x00, 0xFF, 0xFF, 0x4C])
    assert Sa2Interpreter(script).compute_key(0x12345678) == (0x12345678 ^ 0x0000FFFF)


def test_add_with_carry_wraps():
    # ADD 0x00000002 to 0xFFFFFFFF -> 0x00000001 (wrapped)
    script = bytes([0x93, 0x00, 0x00, 0x00, 0x02, 0x4C])
    assert Sa2Interpreter(script).compute_key(0xFFFFFFFF) == 0x00000001
