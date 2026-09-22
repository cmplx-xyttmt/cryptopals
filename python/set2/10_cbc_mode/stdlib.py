from pathlib import Path
from Crypto.Cipher import AES
from cryptolib import xor_bytes, pkcs7
from base64 import b64decode

DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "10.txt"
BLOCK_SIZE = 16


def encrypt_aes_ecb(key: bytes, plaintext: bytes) -> bytes:
    aes = AES.new(key=key, mode=AES.MODE_ECB)
    return aes.encrypt(plaintext)


def decrypt_aes_ecb(key: bytes, ciphertext: bytes) -> bytes:
    aes = AES.new(key=key, mode=AES.MODE_ECB)
    return aes.decrypt(ciphertext)


def aes_cbc_encrypt(key: bytes, plaintext: bytes, iv: bytes) -> bytes:
    result = []
    plaintext = pkcs7(plaintext, BLOCK_SIZE)
    prev_cipher = iv
    for i in range(0, len(plaintext), BLOCK_SIZE):
        block = plaintext[i:i + BLOCK_SIZE]
        prev_cipher = encrypt_aes_ecb(key, xor_bytes(prev_cipher, block))
        result.extend(list(prev_cipher))
    return bytes(result)


def aes_cbc_decrypt(key: bytes, ciphertext: bytes, iv: bytes) -> bytes:
    plaintext = []
    prev = iv
    for i in range(0, len(ciphertext), BLOCK_SIZE):
        block = ciphertext[i:i + BLOCK_SIZE]
        plain = xor_bytes(prev, decrypt_aes_ecb(key, block))
        plaintext.extend(list(plain))
        prev = block

    return bytes(plaintext)


if __name__ == '__main__':
    text = DATA_FILE.read_text()
    cipher_text_ = b64decode(text)
    key_ = "YELLOW SUBMARINE".encode()
    initialisation_vector = bytes([0] * BLOCK_SIZE)

    pt = "I'm encrypting thine."
    ct = aes_cbc_encrypt(key_, pt.encode(), iv=initialisation_vector)
    print(aes_cbc_decrypt(key_, ct, initialisation_vector))

    print(aes_cbc_decrypt(key_, cipher_text_, initialisation_vector).decode())

    # def decrypt_aes_cbc(key: bytes, ciphertext: bytes) -> bytes:
    #     aes = AES.new(key=key, mode=AES.MODE_CBC, iv=initialisation_vector)
    #     return aes.decrypt(ciphertext)
    #
    #
    # print(ct)
    # print(decrypt_aes_cbc(key_, ct))
