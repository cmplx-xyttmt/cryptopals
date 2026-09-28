"""Tests for Challenge 10 — implement CBC mode.

Run from the repo root:  pytest python/set2/10_cbc_mode/
"""
import base64
import random

import pytest
from Crypto.Cipher import AES

from challenge_utils import load_solution
from cryptolib import pkcs7, strip_pkcs7

_sol = load_solution(__file__, "stdlib")
aes_cbc_encrypt = _sol.aes_cbc_encrypt
aes_cbc_decrypt = _sol.aes_cbc_decrypt

KEY = b"YELLOW SUBMARINE"
ZERO_IV = bytes(16)


def _library_cbc(key, iv):
    """A fresh pycryptodome CBC cipher. One object per operation: it is stateful."""
    return AES.new(key=key, mode=AES.MODE_CBC, iv=iv)


def test_official_vector():
    ciphertext = base64.b64decode(_sol.DATA_FILE.read_text())
    plaintext = aes_cbc_decrypt(KEY, ciphertext, ZERO_IV)
    assert plaintext.startswith(b"I'm back and I'm ringin' the bell")
    assert plaintext.endswith(b"Play that funky music \n" + b"\x04" * 4)
    assert len(plaintext) == 2880
    assert len(strip_pkcs7(plaintext, 16)) == 2876


def test_encrypt_matches_pycryptodome():
    """Cross-check against a reference implementation, not just against myself."""
    rng = random.Random(10)
    for _ in range(200):
        key = rng.randbytes(16)
        iv = rng.randbytes(16)
        plaintext = rng.randbytes(rng.randint(0, 200))
        assert aes_cbc_encrypt(key, plaintext, iv) == _library_cbc(key, iv).encrypt(
            pkcs7(plaintext, 16)
        )


def test_decrypt_matches_pycryptodome():
    rng = random.Random(11)
    for _ in range(200):
        key = rng.randbytes(16)
        iv = rng.randbytes(16)
        ciphertext = rng.randbytes(16 * rng.randint(1, 12))
        assert aes_cbc_decrypt(key, ciphertext, iv) == _library_cbc(key, iv).decrypt(
            ciphertext
        )


@pytest.mark.parametrize("length", [0, 1, 15, 16, 17, 31, 32, 100])
def test_round_trip_recovers_the_padded_plaintext(length):
    plaintext = bytes(range(256))[:length]
    recovered = aes_cbc_decrypt(KEY, aes_cbc_encrypt(KEY, plaintext, ZERO_IV), ZERO_IV)
    assert recovered == pkcs7(plaintext, 16)
    assert recovered[: len(plaintext)] == plaintext


def test_ciphertext_is_always_a_whole_number_of_blocks():
    for length in range(0, 65):
        ciphertext = aes_cbc_encrypt(KEY, bytes(length), ZERO_IV)
        assert len(ciphertext) % 16 == 0
        assert len(ciphertext) > length


def test_repeated_plaintext_blocks_do_not_repeat_in_the_ciphertext():
    """The property CBC buys over ECB: chaining hides the repetition."""
    plaintext = b"YELLOW SUBMARINE" * 4

    cbc = aes_cbc_encrypt(KEY, plaintext, ZERO_IV)
    cbc_blocks = [cbc[i : i + 16] for i in range(0, 64, 16)]
    assert len(set(cbc_blocks)) == 4

    ecb = AES.new(key=KEY, mode=AES.MODE_ECB).encrypt(plaintext)
    ecb_blocks = [ecb[i : i + 16] for i in range(0, 64, 16)]
    assert len(set(ecb_blocks)) == 1


def test_the_iv_only_affects_the_first_block():
    ciphertext = aes_cbc_encrypt(KEY, b"A" * 64, ZERO_IV)
    right = aes_cbc_decrypt(KEY, ciphertext, ZERO_IV)
    wrong = aes_cbc_decrypt(KEY, ciphertext, b"0" * 16)

    assert wrong[:16] != right[:16]
    assert wrong[16:] == right[16:]


def test_ecb_helpers_round_trip():
    block = b"YELLOW SUBMARINE"
    assert _sol.decrypt_aes_ecb(KEY, _sol.encrypt_aes_ecb(KEY, block)) == block
