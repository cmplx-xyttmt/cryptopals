"""Unit tests for cryptolib — the shared crypto primitives.

These test the helpers directly (not via any challenge), so a primitive stays
trustworthy no matter which challenge leans on it later.

Run from the repo root:  pytest
Or just this module:      pytest python/cryptolib/
"""
import pytest

from cryptolib import xor_bytes


class TestXorBytes:
    def test_basic_xor(self):
        # 0x0f ^ 0xf0 == 0xff
        assert xor_bytes(bytes([0x0F]), bytes([0xF0])) == bytes([0xFF])

    def test_multi_byte(self):
        a = bytes([0x01, 0x02, 0x03])
        b = bytes([0xFF, 0x00, 0x0F])
        assert xor_bytes(a, b) == bytes([0xFE, 0x02, 0x0C])

    def test_xor_with_zeros_is_identity(self):
        a = b"\xde\xad\xbe\xef"
        assert xor_bytes(a, bytes(len(a))) == a  # bytes(n) is n zero bytes

    def test_xor_with_self_is_zero(self):
        a = b"\xde\xad\xbe\xef"
        assert xor_bytes(a, a) == bytes(len(a))

    def test_self_inverse(self):
        # (a ^ b) ^ b == a — the property every XOR cipher relies on
        a, b = b"attack at dawn!!", b"\x11\x22\x33\x44\x55\x66\x77\x88" * 2
        assert xor_bytes(xor_bytes(a, b), b) == a

    def test_empty_inputs(self):
        assert xor_bytes(b"", b"") == b""

    def test_returns_new_bytes_object(self):
        result = xor_bytes(b"\x00", b"\x00")
        assert isinstance(result, bytes)

    @pytest.mark.parametrize("a, b", [
        (b"\x00", b""),
        (b"", b"\x00"),
        (b"\x01\x02", b"\x03"),
        (b"\x01", b"\x02\x03"),
    ])
    def test_unequal_lengths_raise(self, a, b):
        with pytest.raises(ValueError):
            xor_bytes(a, b)
