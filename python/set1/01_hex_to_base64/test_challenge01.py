"""Tests for Challenge 1 — convert hex to base64.

Run from the repo root:  pytest
Or just this file:        pytest python/set1/01_hex_to_base64/

Solutions are loaded via load_solution() under a folder-unique name, so every
challenge's `stdlib.py` can coexist in a full test run (see challenge_utils).
"""
import base64

import pytest

from challenge_utils import load_solution

# Test the from-scratch base64 encoder. Swap "scratch" -> "stdlib" to test that one.
convert_hex_to_base64 = load_solution(__file__, "scratch").convert_hex_to_base64

def test_official_challenge_vector():
    """The exact input/output given on cryptopals.com."""
    hex_in = (
        "49276d206b696c6c696e6720796f757220627261696e206c696b"
        "65206120706f69736f6e6f7573206d757368726f6f6d"
    )
    expected = "SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb29t"
    assert convert_hex_to_base64(hex_in) == expected


def test_returns_str_not_bytes():
    """Guards against the classic b'...' bug: callers want text, not bytes."""
    result = convert_hex_to_base64("4869")  # hex for "Hi"
    assert isinstance(result, str)
    assert not result.startswith("b'")


def test_simple_known_value():
    # "Hi" -> bytes [0x48, 0x69] -> base64 "SGk="
    assert convert_hex_to_base64("4869") == "SGk="


def test_empty_input():
    assert convert_hex_to_base64("") == ""


@pytest.mark.parametrize(
    "text",
    ["a", "ab", "abc", "abcd", "hello world", "The quick brown fox"],
)
def test_roundtrip_against_stdlib(text):
    """For arbitrary text, our function must agree with a direct base64 encode.

    We build the hex input from `text`, feed it through the solution, and check
    it matches encoding the same bytes directly. This also exercises all three
    base64 padding cases (0, 1, 2 '=' chars) via the varying lengths above.
    """
    raw = text.encode("utf-8")
    hex_in = raw.hex()
    expected = base64.b64encode(raw).decode("ascii")
    assert convert_hex_to_base64(hex_in) == expected


def test_odd_length_hex_is_rejected():
    """Half a byte isn't a byte — bytes.fromhex should reject odd-length hex."""
    with pytest.raises(ValueError):
        convert_hex_to_base64("abc")
