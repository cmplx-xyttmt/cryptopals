from pathlib import Path

from cryptolib import single_byte_xor_decrypt, XorResult

# Challenge inputs live in the repo-root data/ dir (see CLAUDE.md convention).
# parents: [0]=this challenge dir, [1]=set1, [2]=python, [3]=repo root.
DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "04.txt"


def detect_single_char_xor(hex_lines) -> XorResult:
    """Of many hex lines, find the one encrypted with single-byte XOR.

    Score every line's best single-byte decryption and return the global winner.
    Scores are length-normalised (see english_score), so comparing across lines
    is fair.
    """
    candidates = (
        single_byte_xor_decrypt(bytes.fromhex(line.strip()))
        for line in hex_lines
        if line.strip()
    )
    return max(candidates, key=lambda result: result.score)


if __name__ == '__main__':
    print(detect_single_char_xor(DATA_FILE.read_text().splitlines()))
