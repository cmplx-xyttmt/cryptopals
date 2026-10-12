import secrets
from typing import Callable

from Crypto.Cipher import AES
from cryptolib import has_repeated_block, pkcs7


def rand_key() -> bytes:
    return secrets.token_bytes(16)


def pad_with_rand(inp: bytes) -> bytes:
    n_before = 5 + secrets.randbelow(6)  # 5..10
    n_after = 5 + secrets.randbelow(6)
    return secrets.token_bytes(n_before) + inp + secrets.token_bytes(n_after)


def encryption_oracle(plaintext: bytes) -> tuple[bytes, str]:
    """Encrypt under a fresh key, in ECB or CBC at random.

    Returns the ciphertext and the mode it picked. The mode is for checking
    the detector only; the detector itself never sees it.
    """
    plaintext = pkcs7(pad_with_rand(plaintext), 16)
    key = rand_key()
    mode = secrets.choice(["ECB", "CBC"])
    if mode == "CBC":
        aes = AES.new(key=key, mode=AES.MODE_CBC, iv=secrets.token_bytes(16))
    else:
        aes = AES.new(key=key, mode=AES.MODE_ECB)
    return aes.encrypt(plaintext), mode


def detect_mode(oracle: Callable[[bytes], bytes]) -> str:
    ciphertext = oracle(b"repeat" * 200)
    return "ECB" if has_repeated_block(ciphertext) else "CBC"


def detect_against_oracle() -> tuple[str, str]:
    """Run detect_mode once against encryption_oracle. Returns (actual, detected)."""
    actual = []

    def oracle(plaintext: bytes) -> bytes:
        ciphertext, mode = encryption_oracle(plaintext)
        actual.append(mode)
        return ciphertext

    detected = detect_mode(oracle)
    return actual[0], detected


if __name__ == '__main__':
    for _ in range(1000):
        actual_mode, detected_mode = detect_against_oracle()
        assert actual_mode == detected_mode
