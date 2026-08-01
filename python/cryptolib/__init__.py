"""cryptolib — my hand-rolled crypto primitives, reused across challenges."""


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
