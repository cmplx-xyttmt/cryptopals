"""Tests for Challenge 12 — byte-at-a-time ECB decryption (simple).

Run from the repo root:  pytest
"""
import secrets

import pytest
from Crypto.Cipher import AES

from challenge_utils import load_solution
from cryptolib import pkcs7

_sol = load_solution(__file__, "stdlib")
oracle = _sol.oracle
find_sizes = _sol.find_sizes
get_unknown_string = _sol.get_unknown_string


def make_oracle(secret: bytes):
    """An oracle like the challenge's, with its own key and secret."""
    aes = AES.new(key=secrets.token_bytes(16), mode=AES.MODE_ECB)
    return lambda plaintext: aes.encrypt(pkcs7(plaintext + secret, 16))


def test_official():
    assert get_unknown_string(oracle) == _sol.UNKNOWN_DECODED


@pytest.mark.parametrize("length", [0, 1, 15, 16, 17, 31, 32, 33, 50])
def test_recovers_secrets_of_any_length(length):
    # The block boundaries (16, 32) are where the size detection and the
    # end of the loop are easiest to get wrong.
    secret = secrets.token_bytes(length)
    assert get_unknown_string(make_oracle(secret)) == secret


@pytest.mark.parametrize("length", [0, 1, 15, 16, 17, 138])
def test_find_sizes(length):
    assert find_sizes(make_oracle(b"x" * length)) == (16, length)
