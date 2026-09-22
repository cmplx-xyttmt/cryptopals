"""Tests for Challenge 9 — implement PKCS#7 padding.

Only the challenge's own answer lives here. ``pkcs7`` is a shared primitive, so
its behaviour is tested in ``python/cryptolib/test_cryptolib.py``.

Run from the repo root:  pytest python/set2/09_pkcs7_padding/
"""
from challenge_utils import load_solution

_sol = load_solution(__file__, "stdlib")
pkcs7 = _sol.pkcs7


def test_official_vector():
    assert pkcs7(b"YELLOW SUBMARINE", 20) == b"YELLOW SUBMARINE\x04\x04\x04\x04"
