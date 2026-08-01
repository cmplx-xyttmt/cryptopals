"""Tests for Challenge 4 — detect single-character XOR.

Run from the repo root:  pytest
Or just this file:        pytest python/set1/04_detect_single_character_xor/
"""
from cryptolib import xor_bytes

from challenge_utils import load_solution

_sol = load_solution(__file__, "stdlib")
detect_single_char_xor = _sol.detect_single_char_xor
DATA_FILE = _sol.DATA_FILE


def _encrypt_hex(plaintext: str, key: int) -> str:
    raw = plaintext.encode()
    return xor_bytes(raw, bytes([key]) * len(raw)).hex()


def test_official_challenge_vector():
    """The known answer: exactly one line of 4.txt is single-byte-XOR'd English."""
    lines = DATA_FILE.read_text().splitlines()
    result = detect_single_char_xor(lines)
    assert result.plaintext == "Now that the party is jumping\n"
    assert result.key == 53  # 0x35, the character '5'


def test_detects_planted_line_among_decoys():
    """Plant one XOR'd English sentence in a pile of non-English hex lines."""
    plaintext = "Every good detective follows the evidence closely."
    key = 91
    planted = _encrypt_hex(plaintext, key)

    # Deterministic gibberish decoys of the same length (won't read as English).
    n = len(plaintext)
    decoys = [
        bytes((i * 31 + j * 17 + 3) % 256 for j in range(n)).hex()
        for i in range(1, 25)
    ]
    lines = decoys[:12] + [planted] + decoys[12:]

    result = detect_single_char_xor(lines)
    assert result.plaintext == plaintext
    assert result.key == key


def test_ignores_blank_lines():
    """Blank/whitespace lines must not crash bytes.fromhex."""
    plaintext = "The pen is mightier than the sword indeed."
    key = 7
    lines = ["", "   ", _encrypt_hex(plaintext, key), ""]
    assert detect_single_char_xor(lines).plaintext == plaintext
