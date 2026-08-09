"""Tests for Challenge 5 — implement repeating-key XOR.

Run from the repo root:  pytest
Or just this file:        pytest python/set1/05_repeating_key_xor/
"""
from itertools import cycle

import pytest

from challenge_utils import load_solution

repeating_key_xor = load_solution(__file__, "stdlib").repeating_key_xor


def reference(data: bytes, key: bytes) -> bytes:
    """Independent, obviously-correct repeating-key XOR — a differential oracle."""
    return bytes(d ^ k for d, k in zip(data, cycle(key)))


def test_official_ice_vector():
    text = (
        "Burning 'em, if you ain't quick and nimble\n"
        "I go crazy when I hear a cymbal"
    ).encode()
    expected = bytes.fromhex(
        "0b3637272a2b2e63622c2e69692a23693a2a3c6324202d623d63343c2a262263"
        "24272765272a282b2f20430a652e2c652a3124333a653e2b2027630c692b2028"
        "3165286326302e27282f"
    )
    assert repeating_key_xor(text, b"ICE") == expected


@pytest.mark.parametrize("key", [b"A", b"AB", b"ICE", b"KEY!", b"abcde"])
@pytest.mark.parametrize("data", [
    b"hello world",
    b"The quick brown fox jumps over the lazy dog",
    b"attack at dawn, then retreat by noon",
])
def test_matches_reference_for_various_key_lengths(data, key):
    # The point of this suite: keys of length != 3 must be correct. This is what
    # the original `% 3` (hardcoded len('ICE')) got wrong — crash for len<3,
    # silently wrong for len>3.
    assert repeating_key_xor(data, key) == reference(data, key)


def test_single_char_key_is_plain_single_byte_xor():
    data, k = b"hello", 0x58
    assert repeating_key_xor(data, bytes([k])) == bytes(b ^ k for b in data)


def test_key_longer_than_text():
    # Only the first len(data) key bytes get used.
    assert repeating_key_xor(b"hi", b"LONGKEY") == reference(b"hi", b"LONGKEY")


def test_empty_text():
    assert repeating_key_xor(b"", b"ICE") == b""


def test_roundtrip_is_symmetric():
    # Repeating-key XOR is its own inverse — encrypting the ciphertext with the
    # same key restores the plaintext. Challenge 6 relies on exactly this to
    # decrypt once the key is recovered.
    data = b"attack at dawn, then retreat by noon"
    for key in (b"A", b"ICE", b"secret"):
        assert repeating_key_xor(repeating_key_xor(data, key), key) == data
