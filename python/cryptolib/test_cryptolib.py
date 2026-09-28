"""Unit tests for cryptolib — the shared crypto primitives.

These test the helpers directly (not via any challenge), so a primitive stays
trustworthy no matter which challenge leans on it later.

Run from the repo root:  pytest
Or just this module:      pytest python/cryptolib/
"""
import random
from itertools import cycle

import pytest
from Crypto.Util.Padding import pad as reference_pad

from cryptolib import (
    pkcs7,
    strip_pkcs7,
    xor_bytes,
    hamming_distance,
    english_score,
    single_byte_xor_decrypt,
    repeating_key_xor,
    XorResult,
)


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


def _rkx_reference(data: bytes, key: bytes) -> bytes:
    """Independent, obviously-correct repeating-key XOR — a differential oracle."""
    return bytes(d ^ k for d, k in zip(data, cycle(key)))


class TestRepeatingKeyXor:
    def test_official_ice_vector(self):
        text = (
            "Burning 'em, if you ain't quick and nimble\n"
            "I go crazy when I hear a cymbal"
        ).encode()
        expected = bytes.fromhex(
            "0b3637272a2b2e63622c2e69692a23693a2a3c6324202d623d63343c2a262263"
            "24272765272a282b2f20430a652e2c652a3124333a653e2b2027630c692b2028"
            "3165286326302e27282f"
        )
        assert repeating_key_xor(text, b"ICE") == expected

    @pytest.mark.parametrize("key", [b"A", b"AB", b"ICE", b"KEY!", b"abcde"])
    @pytest.mark.parametrize("data", [
        b"hello world",
        b"The quick brown fox jumps over the lazy dog",
        b"attack at dawn, then retreat by noon",
    ])
    def test_matches_reference_for_various_key_lengths(self, data, key):
        # Guards the key-length correctness the old `% 3` hardcode got wrong.
        assert repeating_key_xor(data, key) == _rkx_reference(data, key)

    def test_single_char_key_is_plain_single_byte_xor(self):
        data, k = b"hello", 0x58
        assert repeating_key_xor(data, bytes([k])) == bytes(b ^ k for b in data)

    def test_key_longer_than_text(self):
        assert repeating_key_xor(b"hi", b"LONGKEY") == _rkx_reference(b"hi", b"LONGKEY")

    def test_empty_text(self):
        assert repeating_key_xor(b"", b"ICE") == b""


class TestHammingDistance:
    def test_official_vector(self):
        # The Challenge 6 sanity check.
        assert hamming_distance(b"this is a test", b"wokka wokka!!!") == 37

    def test_identical_is_zero(self):
        assert hamming_distance(b"same bytes", b"same bytes") == 0

    def test_single_bit_difference(self):
        # 0x00 vs 0x01 differ in exactly one bit.
        assert hamming_distance(bytes([0x00]), bytes([0x01])) == 1

    def test_counts_all_bits_including_leading_zero_bytes(self):
        # int.from_bytes drops leading zero bytes, but popcount is unaffected:
        # 0x00 ^ 0x00 = 0 bits, 0x00 ^ 0xFF = 8 bits.
        assert hamming_distance(bytes([0x00, 0x00]), bytes([0x00, 0xFF])) == 8

    def test_is_symmetric(self):
        a, b = b"hello", b"world"
        assert hamming_distance(a, b) == hamming_distance(b, a)

    def test_unequal_lengths_raise(self):
        with pytest.raises(ValueError):
            hamming_distance(b"abc", b"ab")


class TestPkcs7:
    def test_returns_bytes_not_str(self):
        assert isinstance(pkcs7(b"abc", 8), bytes)

    def test_pad_byte_value_equals_pad_count(self):
        # 10 bytes into a 16-byte block: six pad bytes, each with the value 6.
        assert pkcs7(b"YELLOW SUB", 16) == b"YELLOW SUB" + b"\x06" * 6

    def test_aligned_input_gets_a_full_block(self):
        # Already a multiple of the block size -> a whole extra block, not
        # nothing. That is what keeps the last byte a usable pad count.
        assert pkcs7(b"YELLOW SUBMARINE", 16) == b"YELLOW SUBMARINE" + b"\x10" * 16

    def test_empty_input_gets_a_full_block(self):
        assert pkcs7(b"", 8) == b"\x08" * 8

    def test_single_byte_short(self):
        assert pkcs7(b"a" * 15, 16) == b"a" * 15 + b"\x01"

    @pytest.mark.parametrize("block_size", [1, 2, 8, 16, 20, 255])
    def test_padding_properties_across_lengths(self, block_size):
        """For every length up to three blocks, the padding is self-describing."""
        for n in range(3 * block_size + 1):
            data = bytes(range(256))[:n] if n <= 256 else bytes(n)
            padded = pkcs7(data, block_size)
            added = len(padded) - len(data)

            assert padded.startswith(data)
            assert len(padded) % block_size == 0
            assert 1 <= added <= block_size
            # Every pad byte carries the count, so the last byte says how many
            # to strip.
            assert padded[-added:] == bytes([added]) * added
            assert padded[: -padded[-1]] == data

    def test_matches_pycryptodome_on_random_inputs(self):
        rng = random.Random(9)
        for _ in range(500):
            block_size = rng.randint(1, 255)
            data = rng.randbytes(rng.randint(0, 3 * block_size))
            assert pkcs7(data, block_size) == reference_pad(data, block_size)


class TestStripPkcs7:
    def test_strips_a_partial_block(self):
        assert strip_pkcs7(b"YELLOW SUB" + b"\x06" * 6, 16) == b"YELLOW SUB"

    def test_strips_a_whole_block_of_padding(self):
        assert strip_pkcs7(b"YELLOW SUBMARINE" + b"\x10" * 16, 16) == b"YELLOW SUBMARINE"

    def test_strips_back_to_empty(self):
        assert strip_pkcs7(b"\x08" * 8, 8) == b""

    @pytest.mark.parametrize("block_size", [1, 2, 8, 16, 20, 255])
    def test_round_trips_with_pkcs7(self, block_size):
        for n in range(3 * block_size + 1):
            data = bytes(range(256))[:n] if n <= 256 else bytes(n)
            assert strip_pkcs7(pkcs7(data, block_size), block_size) == data

    def test_rejects_a_zero_count(self):
        # data[:-0] would be empty, so a 0 has to be caught rather than sliced.
        with pytest.raises(ValueError):
            strip_pkcs7(b"A" * 15 + b"\x00", 16)

    def test_rejects_a_count_larger_than_the_block(self):
        with pytest.raises(ValueError):
            strip_pkcs7(b"A" * 15 + b"\x11", 16)

    def test_rejects_pad_bytes_that_disagree(self):
        with pytest.raises(ValueError):
            strip_pkcs7(b"A" * 12 + b"\x04\x04\x03\x04", 16)

    def test_rejects_a_short_or_ragged_buffer(self):
        with pytest.raises(ValueError):
            strip_pkcs7(b"", 16)
        with pytest.raises(ValueError):
            strip_pkcs7(b"A" * 20, 16)

    def test_matches_pycryptodome(self):
        from Crypto.Util.Padding import unpad as reference_unpad

        rng = random.Random(12)
        for _ in range(300):
            block_size = rng.randint(2, 255)
            data = rng.randbytes(rng.randint(0, 3 * block_size))
            padded = pkcs7(data, block_size)
            assert strip_pkcs7(padded, block_size) == reference_unpad(padded, block_size)
