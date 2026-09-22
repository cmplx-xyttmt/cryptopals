"""Challenge 9 — implement PKCS#7 padding.

The primitive itself lives in ``cryptolib.pkcs7``, since Challenge 10 uses it
too. This file is the challenge's own self-check.
"""
from cryptolib import pkcs7

if __name__ == '__main__':
    data_ = "YELLOW SUBMARINE".encode()
    assert pkcs7(data_, 20) == b"YELLOW SUBMARINE\x04\x04\x04\x04"
    print(pkcs7(data_, 20))
