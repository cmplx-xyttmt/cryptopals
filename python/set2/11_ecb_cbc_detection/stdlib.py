import random
from Crypto.Cipher import AES
from cryptolib import pkcs7

random.seed(1)


def get_random_bytes(n: int) -> bytes:
    return bytes([random.randint(0, 255) for _ in range(n)])


def rand_key() -> bytes:
    return get_random_bytes(16)


def pad_with_rand(inp: bytes) -> bytes:
    n_before = random.randint(5, 10)
    n_after = random.randint(5, 10)
    before = get_random_bytes(n_before)
    after = get_random_bytes(n_after)
    return before + inp + after


def encryption_oracle(plaintext: bytes) -> tuple[bytes, str]:
    plaintext = pad_with_rand(plaintext)
    plaintext = pkcs7(plaintext, 16)
    key = rand_key()
    modes = [AES.MODE_ECB, AES.MODE_CBC]
    mode = modes[random.randint(0, 1)]
    if mode == AES.MODE_CBC:
        iv = get_random_bytes(16)
        aes = AES.new(key=key, mode=mode, iv=iv)
    else:
        aes = AES.new(key=key, mode=mode)
    return aes.encrypt(plaintext), 'ECB' if mode == AES.MODE_ECB else 'CBC'


def detect_mode() -> tuple[str, str]:
    my_text = "repeat" * 200
    block_size = 16
    ciphertext, actual_mode = encryption_oracle(my_text.encode())
    blocks = [ciphertext[i:i + block_size] for i in range(0, len(ciphertext), block_size)]
    has_repeated = len(set(blocks)) != len(blocks)
    if has_repeated:
        return actual_mode, "ECB"
    return actual_mode, "CBC"


if __name__ == '__main__':
    for _ in range(1000):
        actual_mode, detected_mode = detect_mode()
        assert actual_mode == detected_mode
