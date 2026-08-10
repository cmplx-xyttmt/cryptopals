"""Tests for Challenge 7 — AES in ECB mode.

This does NOT test AES itself (that's the library's job) — it's a known-answer
check on our own wiring (right file, key, and mode). It would have caught the
copy-pasted wrong-filename bug immediately.

Run from the repo root:  pytest
"""
import base64

from challenge_utils import load_solution

_sol = load_solution(__file__, "stdlib")


def test_official_vector():
    ciphertext = base64.b64decode(_sol.DATA_FILE.read_text())
    plaintext = _sol.decrypt_aes_ecb(b"YELLOW SUBMARINE", ciphertext)
    assert plaintext.decode().startswith("I'm back and I'm ringin' the bell")
