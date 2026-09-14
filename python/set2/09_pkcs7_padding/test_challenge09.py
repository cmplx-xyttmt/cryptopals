"""Tests for Challenge 9 — implement PKCS#7 padding.

Run from the repo root:  pytest python/set2/09_pkcs7_padding/
"""
import random

import pytest
from Crypto.Util.Padding import pad as reference_pad

from challenge_utils import load_solution

_sol = load_solution(__file__, "stdlib")
pkcs7 = _sol.pkcs7


def test_official_vector():
    assert pkcs7(b"YELLOW SUBMARINE", 20) == b"YELLOW SUBMARINE\x04\x04\x04\x04"


def test_returns_bytes_not_str():
    assert isinstance(pkcs7(b"abc", 8), bytes)


def test_pad_byte_value_equals_pad_count():
    # 10 bytes into a 16-byte block: six pad bytes, each with the value 6.
    assert pkcs7(b"YELLOW SUB", 16) == b"YELLOW SUB" + b"\x06" * 6


def test_aligned_input_gets_a_full_block():
    # Already a multiple of the block size -> a whole extra block, not nothing.
    assert pkcs7(b"YELLOW SUBMARINE", 16) == b"YELLOW SUBMARINE" + b"\x10" * 16


def test_empty_input_gets_a_full_block():
    assert pkcs7(b"", 8) == b"\x08" * 8


def test_single_byte_short():
    assert pkcs7(b"a" * 15, 16) == b"a" * 15 + b"\x01"


@pytest.mark.parametrize("block_size", [1, 2, 8, 16, 20, 255])
def test_padding_properties_across_lengths(block_size):
    """For every data length up to three blocks, the padding is self-describing."""
    for n in range(3 * block_size + 1):
        data = bytes(range(256))[:n] if n <= 256 else bytes(n)
        padded = pkcs7(data, block_size)
        added = len(padded) - len(data)

        assert padded.startswith(data)
        assert len(padded) % block_size == 0
        assert 1 <= added <= block_size
        # Every pad byte carries the count, so the last byte says how many to strip.
        assert padded[-added:] == bytes([added]) * added
        assert padded[: -padded[-1]] == data


def test_matches_pycryptodome_on_random_inputs():
    rng = random.Random(9)
    for _ in range(500):
        block_size = rng.randint(1, 255)
        data = rng.randbytes(rng.randint(0, 3 * block_size))
        assert pkcs7(data, block_size) == reference_pad(data, block_size)
