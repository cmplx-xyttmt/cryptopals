"""Tests for Challenge 3 — single-byte XOR cipher.

Strategy: take known English sentences, encrypt each under a known single-byte
key, then check the solver recovers the original plaintext. This is a much
stronger test than the one official vector, because it exercises the *scorer*
across many texts and keys.

Run from the repo root:  pytest
"""
import pytest

from challenge_utils import load_solution

_sol = load_solution(__file__, "stdlib")
single_byte_xor_decrypt = _sol.single_byte_xor_decrypt
character_frequency = _sol.english_score

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
    "Now is the winter of our discontent.",
    "We hold these truths to be self-evident.",
]

KEYS = [1, 13, 42, 88, 200, 255]


def encrypt(plaintext: str, key: int) -> str:
    """XOR every byte with `key`, return hex — the inverse of the solver."""
    return bytes(b ^ key for b in plaintext.encode()).hex()


def recovered_text(result):
    """The solver currently returns (score, text); tolerate str too."""
    return result[1] if isinstance(result, tuple) else result


def test_official_challenge_vector():
    hex_in = "1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736"
    assert recovered_text(single_byte_xor_decrypt(hex_in)) == "Cooking MC's like a pound of bacon"


@pytest.mark.parametrize("plaintext", CORPUS)
@pytest.mark.parametrize("key", KEYS)
def test_roundtrip_recovers_plaintext(plaintext, key):
    ciphertext_hex = encrypt(plaintext, key)
    assert recovered_text(single_byte_xor_decrypt(ciphertext_hex)) == plaintext


# --- scorer sanity: real English should out-score garbage ------------------

def test_english_scores_higher_than_random_bytes():
    english = "The quick brown fox jumps over the lazy dog"
    garbage = "".join(chr((i * 37 + 11) % 128) for i in range(len(english)))
    assert character_frequency(english) > character_frequency(garbage)


def test_english_scores_higher_than_control_chars():
    # The exact false-positive you hit: real text vs a string full of nulls/controls.
    english = "Cooking MC's like a pound of bacon"
    controlly = "cOOKING\x00mc\x07S\x00LIKE\x00A\x00POUND\x00OF\x00BACON"
    assert character_frequency(english) > character_frequency(controlly)


# --- Regression tests capturing the count-vs-position scorer bug ---------------
# The current character_frequency compares a character's raw COUNT to its expected
# rank POSITION (different units); the intent was to compare its frequency RANK to
# that position. These two tests fail because of that, and should pass once the
# scorer is reworked (frequency-weighted or true rank-based).
#
# Marked xfail(strict=True): today they fail, so the suite stays green (they show as
# "xfailed"). After the fix they'll pass -> strict mode turns that XPASS into a
# failure, which is the cue to DELETE these markers and keep them as green guards.
# To watch them actually fail right now:
#     pytest --runxfail python/set1/03_single-byte_xor_cipher/
CHAR_ORDER = "ETAOINSHRDLCUMWFGYPBVKJXQ "


@pytest.mark.xfail(strict=True, reason="count-vs-position bug: nonsense out-scores English")
def test_english_beats_string_gaming_count_equals_position():
    # Gibberish tuned so each character appears exactly `position` times, which
    # maximises the buggy score (|count - position| == 0) despite being nonsense.
    gamed = "".join(ch * pos for pos, ch in enumerate(CHAR_ORDER))
    english = "the quick brown fox jumps over the lazy dog and runs away"
    assert character_frequency(english) > character_frequency(gamed)


@pytest.mark.xfail(strict=True, reason="count-vs-position bug: score should depend on rank, not raw counts")
def test_score_is_invariant_to_repetition():
    # Repeating a text leaves its frequency RANK order identical, so a correct
    # position/rank-based score must be unchanged. A raw-count score is not.
    text = "the quick brown fox jumps over the lazy dog"
    assert character_frequency(text) == pytest.approx(character_frequency(text * 3))
