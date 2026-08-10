import base64
from pathlib import Path

from Crypto.Cipher import AES


def decrypt_aes_ecb(key: bytes, ciphertext: bytes) -> bytes:
    aes = AES.new(key=key, mode=AES.MODE_ECB)
    return aes.decrypt(ciphertext)


DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "7.txt"
if __name__ == '__main__':
    key_ = "YELLOW SUBMARINE".encode()
    b64_text = DATA_FILE.read_text()
    ciphertext_ = base64.b64decode(b64_text)
    print(decrypt_aes_ecb(key_, ciphertext_).decode())
