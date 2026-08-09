"""Tests for Challenge 6 — break repeating-key XOR.

Run from the repo root:  pytest
Or just this file:        pytest python/set1/06_break_repeating_key_xor/
"""
import base64

from cryptolib import repeating_key_xor

from challenge_utils import load_solution

_sol = load_solution(__file__, "stdlib")
get_key_size = _sol.get_key_size
get_key = _sol.get_key
decrypt = _sol.decrypt
DATA_FILE = _sol.DATA_FILE


def test_official_vector():
    """Break the real base64 ciphertext from the challenge file."""
    ciphertext = base64.b64decode(DATA_FILE.read_text())
    key_size = get_key_size(ciphertext)
    key = get_key(ciphertext, key_size)
    plaintext = decrypt(ciphertext, key).decode()

    assert key_size == 29
    assert key == b"Terminator X: Bring the noise"
    assert plaintext.startswith("I'm back and I'm ringin' the bell")


def test_breaks_synthetic_ciphertext():
    """Encrypt known text with a known key, then break it blind and recover it."""
    plaintext = (
        b"We choose to go to the Moon in this decade and do the other things, "
        b"not because they are easy, but because they are hard, because that "
        b"goal will serve to organize and measure the best of our energies and "
        b"skills, because that challenge is one that we are willing to accept, "
        b"one we are unwilling to postpone, and one we intend to win, and the "
        b"others, too."
    )
    key = b"MOON!"                      # length 5
    ciphertext = repeating_key_xor(plaintext, key)

    key_size = get_key_size(ciphertext)
    recovered_key = get_key(ciphertext, key_size)

    # Keysize detection may land on a MULTIPLE of the true length (a repeated key
    # decrypts identically) — e.g. 5-byte "MOON!" often detects as 15 / "MOON!MOON!MOON!".
    assert key_size % len(key) == 0
    # Regardless of which multiple, decrypting with the recovered key round-trips.
    assert decrypt(ciphertext, recovered_key) == plaintext
