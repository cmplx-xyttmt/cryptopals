"""Tests for Challenge 8 — detect AES in ECB mode.

Run from the repo root:  pytest
"""
from challenge_utils import load_solution

_sol = load_solution(__file__, "stdlib")
find_ecb_line = _sol.find_ecb_line


def test_official_vector():
    lines = _sol.DATA_FILE.read_text().splitlines()
    assert find_ecb_line(lines) == 132
