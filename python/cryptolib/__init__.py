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
