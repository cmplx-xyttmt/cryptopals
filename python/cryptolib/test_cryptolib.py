"""Unit tests for cryptolib — the shared crypto primitives.

These test the helpers directly (not via any challenge), so a primitive stays
trustworthy no matter which challenge leans on it later.

Run from the repo root:  pytest
Or just this module:      pytest python/cryptolib/
"""
import pytest

from cryptolib import xor_bytes, english_score, single_byte_xor_decrypt, XorResult


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


# A spread of plain-ASCII English sentences: varied length, punctuation, case.
CORPUS = [
    "Cooking MC's like a pound of bacon",
    "The quick brown fox jumps over the lazy dog.",
    "To be, or not to be, that is the question.",
    "All that glitters is not gold.",
    "It was the best of times, it was the worst of times.",
    "I think, therefore I am.",
    "A journey of a thousand miles begins with a single step.",
    "Better late than never, but never late is better.",
    "The early bird catches the worm.",
    "Knowledge is power, and power corrupts.",
]

CHAR_ORDER = "ETAOINSHRDLCUMWFGYPBVKJXQ "


class TestEnglishScore:
    def test_english_beats_random_bytes(self):
        english = "The quick brown fox jumps over the lazy dog"
        garbage = "".join(chr((i * 37 + 11) % 128) for i in range(len(english)))
        assert english_score(english) > english_score(garbage)

    def test_english_beats_control_chars(self):
        # Real text vs a string full of nulls/controls (the Challenge 3 false-positive).
        english = "Cooking MC's like a pound of bacon"
        controlly = "cOOKING\x00mc\x07S\x00LIKE\x00A\x00POUND\x00OF\x00BACON"
        assert english_score(english) > english_score(controlly)

    def test_english_beats_string_gaming_count_equals_position(self):
        # Regression guard for the old count-vs-position scorer: gibberish tuned so
        # each char appears exactly `position` times used to out-score English.
        gamed = "".join(ch * pos for pos, ch in enumerate(CHAR_ORDER))
        english = "the quick brown fox jumps over the lazy dog and runs away"
        assert english_score(english) > english_score(gamed)

    def test_invariant_to_repetition(self):
        # Length-normalised: repeating a text keeps its frequency profile, so the
        # score is unchanged. (The old raw-count scorer jumped 383 -> 429.)
        text = "the quick brown fox jumps over the lazy dog"
        assert english_score(text) == pytest.approx(english_score(text * 3))

    def test_empty_string_is_zero(self):
        assert english_score("") == 0.0


class TestSingleByteXorDecrypt:
    def _encrypt(self, plaintext: str, key: int) -> bytes:
        return xor_bytes(plaintext.encode(), bytes([key]) * len(plaintext.encode()))

    def test_official_challenge3_vector(self):
        data = bytes.fromhex(
            "1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736"
        )
        result = single_byte_xor_decrypt(data)
        assert result.plaintext == "Cooking MC's like a pound of bacon"
        assert result.key == 88  # 0x58

    @pytest.mark.parametrize("key", [1, 13, 42, 88, 200, 255])
    @pytest.mark.parametrize("plaintext", CORPUS)
    def test_roundtrip_recovers_plaintext_and_key(self, plaintext, key):
        result = single_byte_xor_decrypt(self._encrypt(plaintext, key))
        assert result.plaintext == plaintext
        assert result.key == key

    def test_returns_xorresult(self):
        result = single_byte_xor_decrypt(self._encrypt("hello world today", 7))
        assert isinstance(result, XorResult)

    def test_empty_data_decodes_to_empty(self):
        # b"" decodes to "" for every key, scoring 0.0 — harmless (real English
        # scores far higher, so an empty line never wins a cross-line comparison).
        result = single_byte_xor_decrypt(b"")
        assert result.plaintext == ""
        assert result.score == 0.0

    def test_sentinel_when_nothing_decodes(self):
        # [0x00, 0x80] can't be valid UTF-8 under ANY single-byte key: the two bytes
        # always differ in their high bit, so no key makes both ASCII, and they can't
        # form a 2-byte sequence either. Every candidate raises -> -inf sentinel.
        result = single_byte_xor_decrypt(bytes([0x00, 0x80]))
        assert result.score == float("-inf")
        assert result.plaintext == ""
