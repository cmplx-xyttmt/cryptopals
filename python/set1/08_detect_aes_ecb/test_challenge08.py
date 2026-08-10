"""Tests for Challenge 8 — detect AES in ECB mode.

Run from the repo root:  pytest
"""
from challenge_utils import load_solution

_sol = load_solution(__file__, "stdlib")
has_repeated_block = _sol.has_repeated_block
find_ecb_line = _sol.find_ecb_line


def test_official_vector():
    lines = _sol.DATA_FILE.read_text().splitlines()
    assert find_ecb_line(lines) == 132


def test_detects_a_repeated_block():
    # two identical 16-byte blocks in a row -> True
    block = bytes(range(16))
    assert has_repeated_block(block + block) is True


def test_no_repeat_when_all_blocks_distinct():
    distinct = bytes(range(16)) + bytes(range(16, 32)) + bytes(range(32, 48))
    assert has_repeated_block(distinct) is False


def test_repeat_need_not_be_adjacent():
    a, b, c = bytes(range(16)), bytes(range(16, 32)), bytes(range(32, 48))
    assert has_repeated_block(a + b + a + c) is True
