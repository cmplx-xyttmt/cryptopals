from pathlib import Path

from cryptolib import has_repeated_block

DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "8.txt"


def find_ecb_line(hex_lines: list[str]) -> int:
    """Index of the (single) line whose ciphertext has a repeated block."""
    for i, line in enumerate(hex_lines):
        if has_repeated_block(bytes.fromhex(line.strip())):
            return i
    return -1


if __name__ == '__main__':
    lines = DATA_FILE.read_text().splitlines()
    idx = find_ecb_line(lines)
    print(f"Likely ECB at line {idx}: {lines[idx]}")
