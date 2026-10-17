import secrets
import base64

from Crypto.Cipher import AES
from cryptolib import pkcs7, has_repeated_block

BLOCK_SIZE = 16
RAND_KEY = secrets.token_bytes(BLOCK_SIZE)
UNKNOWN_STRING = b"Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkgaGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBqdXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUgYnkK"
UNKNOWN_DECODED = base64.b64decode(UNKNOWN_STRING)


def oracle(plaintext: bytes) -> bytes:
    to_encrypt = plaintext + UNKNOWN_DECODED
    to_encrypt = pkcs7(to_encrypt, BLOCK_SIZE)
    aes = AES.new(key=RAND_KEY, mode=AES.MODE_ECB)
    return aes.encrypt(to_encrypt)


def build_dict(pref: bytes, oracle_=oracle) -> dict[bytes, bytes]:
    dictionary = dict()
    for bt in range(256):
        pt = pref + bytes([bt])
        ct = oracle_(pt)
        dictionary[ct[:len(pref) + 1]] = pt

    return dictionary


def get_byte(pref: bytes, dictionary: dict[bytes, bytes], oracle_=oracle) -> int:
    ct = oracle_(pref)
    size_to_use = len(next(iter(dictionary)))
    return dictionary[ct[:size_to_use]][-1]


def get_unknown_string(block_size: int):
    unknown = []
    blocks = 1
    i = 0
    while True:
        # for i in range(block_size * blocks):
        pref_length = ((i + 1) // block_size + 1) * block_size - (i + 1) % block_size
        prefix = b'a' * pref_length
        dictionary = build_dict(prefix + bytes(unknown))
        unknown.append(get_byte(prefix, dictionary))
        if len(unknown) == len(UNKNOWN_DECODED):
            break
        i += 1
    return bytes(unknown)


if __name__ == '__main__':
    ct_length = 0
    pt_ = b''
    block_size_ = 0
    while True:
        pt_ += b'A'
        ct_ = oracle(pt_)
        if 0 < ct_length != len(ct_):
            block_size_ = len(ct_) - ct_length
            print("Block size: ", block_size_)
            break
        else:
            ct_length = len(ct_)

    print("Is ECB?: ", has_repeated_block(oracle(b'a' * 32), block_size_))
    # pt_ = b'a' * (block_size_ - 1)
    # dictionary_ = build_dict(pt_)
    # print(len(dictionary_))
    print(get_unknown_string(block_size_).decode())
