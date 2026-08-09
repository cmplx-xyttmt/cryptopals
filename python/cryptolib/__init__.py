"""cryptolib — my hand-rolled crypto primitives, reused across challenges."""
from collections import namedtuple
from itertools import cycle


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two equal-length byte buffers, returning a new ``bytes``.

    XOR is the workhorse of Set 1 (fixed XOR, single-byte, repeating-key).
    Requires equal lengths — ``zip`` would otherwise silently truncate to the
    shorter buffer, which is a bug for a *fixed* XOR.

    :raises ValueError: if ``a`` and ``b`` differ in length.
    """
    if len(a) != len(b):
        raise ValueError("xor_bytes requires equal-length buffers")
    return bytes(x ^ y for x, y in zip(a, b))


def repeating_key_xor(data: bytes, key: bytes) -> bytes:
    """XOR `data` against `key` repeated cyclically (Vigenère-style XOR).

    `cycle(key)` repeats the key for any length (no modulus to get wrong) and
    `zip` stops at `len(data)`.
    """
    return bytes(b ^ k for b, k in zip(data, cycle(key)))


# Rough relative frequencies of letters + space in English text (%)
ENGLISH_FREQ = {
    ' ': 18.0, 'e': 10.2, 't': 7.5, 'a': 6.5, 'o': 6.1, 'i': 5.7, 'n': 5.5,
    'h': 4.9, 's': 5.1, 'r': 4.8, 'd': 3.5, 'l': 3.3, 'c': 2.3, 'u': 2.3,
    'm': 2.0, 'w': 1.6, 'f': 1.8, 'g': 1.6, 'y': 1.6, 'p': 1.6, 'b': 1.3,
    'v': 0.8, 'k': 0.6, 'j': 0.1, 'x': 0.1, 'q': 0.1, 'z': 0.1
}


def english_score(text: str) -> float:
    if not text:
        return 0.0
    score = 0.0
    for ch in text.lower():
        if ch in ENGLISH_FREQ:
            score += ENGLISH_FREQ[ch]  # reward frequent letters + space
        elif ch.isprintable():
            pass  # punctuation/digits neutral
        else:
            score -= 15.0  # control byte: strong wrong-key signal

    return score / len(text)  # normalize -> fair across lengths


XorResult = namedtuple("XorResult", "key score plaintext")


def single_byte_xor_decrypt(data: bytes) -> XorResult:
    """Best single-byte-XOR decryption of `data`, chosen by english_score.

    Tries all 256 keys and returns the highest-scoring candidate as an
    ``XorResult(key, score, plaintext)``. Candidates that aren't valid UTF-8 are
    skipped. If none decode, returns a sentinel with score ``-inf`` so it never
    wins a comparison (e.g. across lines in Challenge 4).
    """
    best = XorResult(key=0, score=float("-inf"), plaintext="")
    for key in range(256):
        decoded = xor_bytes(data, bytes([key]) * len(data))  # XOR is reversible
        try:
            text = decoded.decode()
        except UnicodeDecodeError:
            continue
        score = english_score(text)
        if score > best.score:
            best = XorResult(key, score, text)
    return best
