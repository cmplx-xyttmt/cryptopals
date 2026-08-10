from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "8.txt"
BLOCK_SIZE = 16


def has_repeated_block(ciphertext: bytes, block_size: int = BLOCK_SIZE) -> bool:
    """True if any block repeats — the tell-tale sign of ECB.

    ECB encrypts identical plaintext blocks to identical ciphertext blocks, so a
    duplicate block is a near-certain ECB signal (random ciphertext effectively
    never collides: a 16-byte block has 2**128 values, birthday bound ~2**64).
    Needs no key and no decryption — the leak is purely structural.
    """
    blocks = [ciphertext[i:i + block_size] for i in range(0, len(ciphertext), block_size)]
    return len(set(blocks)) != len(blocks)


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
