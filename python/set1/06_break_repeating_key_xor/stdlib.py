import statistics
from pathlib import Path
import base64

from cryptolib import hamming_distance, single_byte_xor_decrypt, repeating_key_xor

DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "6.txt"
MAX_KEY_SIZE = 40


def keysize_score(ciphertext: bytes, size: int) -> float:
    blocks = [ciphertext[i:i + size] for i in range(0, len(ciphertext) - size + 1, size)]
    pairs = [(a, b) for i, a in enumerate(blocks) for b in blocks[i + 1:]]
    return statistics.mean(hamming_distance(a, b) for a, b in pairs) / size


def get_key_size(ciphertext: bytes) -> int:
    return min(range(2, MAX_KEY_SIZE + 1), key=lambda size_: keysize_score(ciphertext, size_))


def get_key(ciphertext: bytes, key_size: int) -> bytes:
    # transpose
    blocks = [ciphertext[i::key_size] for i in range(key_size)]
    return bytes(single_byte_xor_decrypt(block).key for block in blocks)


def decrypt(ciphertext: bytes, key: bytes) -> bytes:
    return repeating_key_xor(ciphertext, key)


if __name__ == '__main__':
    b64_text = DATA_FILE.read_text()
    ciphertext_ = base64.b64decode(b64_text)
    key_size_ = get_key_size(ciphertext_)
    print(f"Key size: {key_size_}")

    key_ = get_key(ciphertext_, key_size=key_size_)
    print(f"Key: {key_}")

    cleartext = decrypt(ciphertext_, key_)
    print(cleartext.decode())
