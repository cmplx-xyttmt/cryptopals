import secrets
import base64
from typing import Callable

from Crypto.Cipher import AES
from cryptolib import pkcs7, has_repeated_block

BLOCK_SIZE = 16
RAND_KEY = secrets.token_bytes(BLOCK_SIZE)
UNKNOWN_STRING = b"Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkgaGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBqdXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUgYnkK"
UNKNOWN_DECODED = base64.b64decode(UNKNOWN_STRING)

Oracle = Callable[[bytes], bytes]


def oracle(plaintext: bytes) -> bytes:
    to_encrypt = plaintext + UNKNOWN_DECODED
    to_encrypt = pkcs7(to_encrypt, BLOCK_SIZE)
    aes = AES.new(key=RAND_KEY, mode=AES.MODE_ECB)
    return aes.encrypt(to_encrypt)


def find_sizes(oracle_: Oracle) -> tuple[int, int]:
    """Return (block size, length of the unknown string).

    Add one byte at a time until the ciphertext grows. At that point my n bytes
    plus the unknown string exactly fill whole blocks, and padding has spilled
    into a new block, so the unknown string is len(oracle(b'')) - n bytes long.
    """
    empty_length = len(oracle_(b''))
    n = 0
    while True:
        n += 1
        length = len(oracle_(b'A' * n))
        if length != empty_length:
            return length - empty_length, empty_length - n


def build_dict(pref: bytes, oracle_: Oracle, compare: int) -> dict[bytes, int]:
    dictionary = dict()
    for bt in range(256):
        ct = oracle_(pref + bytes([bt]))
        dictionary[ct[:compare]] = bt
    return dictionary


def get_byte(pref: bytes, dictionary: dict[bytes, int], oracle_: Oracle, compare: int) -> int:
    ct = oracle_(pref)
    return dictionary[ct[:compare]]


def get_unknown_string(oracle_: Oracle) -> bytes:
    block_size, length = find_sizes(oracle_)
    assert has_repeated_block(oracle_(b'a' * 2 * block_size), block_size), "not ECB"

    unknown = b''
    for i in range(length):
        # Enough filler to put byte i at the end of a block: 15, 14, ..., 0, 15, ...
        prefix = b'a' * (block_size - 1 - i % block_size)
        # filler + known bytes + the guess always fill whole blocks, up to and
        # including the block that holds byte i
        compare = len(prefix) + len(unknown) + 1
        dictionary = build_dict(prefix + unknown, oracle_, compare)
        unknown += bytes([get_byte(prefix, dictionary, oracle_, compare)])
    return unknown


if __name__ == '__main__':
    recovered = get_unknown_string(oracle)
    print(recovered.decode())
    assert recovered == UNKNOWN_DECODED
