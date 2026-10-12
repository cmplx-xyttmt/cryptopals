"""Tests for Challenge 11 — an ECB/CBC detection oracle.

Run from the repo root:  pytest
"""
from collections import Counter

from challenge_utils import load_solution

_sol = load_solution(__file__, "stdlib")
encryption_oracle = _sol.encryption_oracle
detect_mode = _sol.detect_mode
detect_against_oracle = _sol.detect_against_oracle


def test_detector_is_right_every_time():
    results = [detect_against_oracle() for _ in range(500)]
    assert all(actual == detected for actual, detected in results)
    # and both modes actually came up, so neither branch went untested
    assert {actual for actual, _ in results} == {"ECB", "CBC"}


def test_oracle_picks_both_modes_roughly_evenly():
    counts = Counter(encryption_oracle(b"x")[1] for _ in range(2000))
    assert 800 < counts["ECB"] < 1200


def test_forty_three_identical_bytes_are_always_enough():
    # Isaac's bound: with a 5..10 byte random prefix, 43 bytes of one value
    # always fill two whole aligned blocks.
    for _ in range(500):
        ciphertext, mode = encryption_oracle(b"A" * 43)
        detected = detect_mode(lambda _: ciphertext)
        assert detected == mode
