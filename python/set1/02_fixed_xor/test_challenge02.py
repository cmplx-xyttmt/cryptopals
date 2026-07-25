"""Tests for Challenge 2 — fixed XOR.

Run from the repo root:  pytest
Or just this file:        pytest python/set1/02_fixed_xor/
"""
import pytest

from stdlib import fixed_xor


def test_official_challenge_vector():
    """The exact input/output given on cryptopals.com."""
    a = "1c0111001f010100061a024b53535009181c"
    b = "686974207468652062756c6c277320657965"
    assert fixed_xor(a, b) == "746865206b696420646f6e277420706c6179"


def test_returns_hex_str():
    result = fixed_xor("00", "00")
    assert isinstance(result, str)


def test_xor_with_zero_is_identity():
    # x ^ 0 == x
    assert fixed_xor("abcdef", "000000") == "abcdef"


def test_xor_with_all_ones_flips_bits():
    # x ^ 0xFF flips every bit; 0x0f -> 0xf0
    assert fixed_xor("0f", "ff") == "f0"


def test_xor_is_self_inverse():
    # (a ^ b) ^ b == a  — the property every XOR-based cipher relies on
    a, b = "deadbeef", "0badf00d"
    once = fixed_xor(a, b)
    twice = fixed_xor(once, b)
    assert twice == a


def test_non_ascii_result_is_fine():
    """XOR output is arbitrary bytes — it need NOT be valid text.

    0x00 ^ 0x80 == 0x80, which is not an ASCII character. A correct fixed_xor
    should return "80" regardless; it must not try to interpret the bytes as text.
    """
    assert fixed_xor("00", "80") == "80"
