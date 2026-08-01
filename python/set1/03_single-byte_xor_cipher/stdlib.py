from cryptolib import xor_bytes
from collections import Counter

# Rough relative frequencies of letters + space in English text (%)
ENGLISH_FREQ = {
    ' ': 18.0, 'e': 10.2, 't': 7.5, 'a': 6.5, 'o': 6.1, 'i': 5.7, 'n': 5.5,
    'h': 4.9, 's': 5.1, 'r': 4.8, 'd': 3.5, 'l': 3.3, 'c': 2.3, 'u': 2.3,
    'm': 2.0, 'w': 1.6, 'f': 1.8, 'g': 1.6, 'y': 1.6, 'p': 1.6, 'b': 1.3,
    'v': 0.8, 'k': 0.6, 'j': 0.1, 'x': 0.1, 'q': 0.1, 'z': 0.1
}


def english_score(text: str) -> float:
    if not text:
        return 0.0
    score = 0.0
    for ch in text.lower():
        if ch in ENGLISH_FREQ:
            score += ENGLISH_FREQ[ch]  # reward frequent letters + space
        elif ch.isprintable():
            pass  # punctuation/digits neutral
        else:
            score -= 15.0  # control byte: strong wrong-key signal

    return score / len(text)  # normalize -> fair across lengths


def single_byte_xor_decrypt(hex_encoded: str) -> str:
    encoded_bytes = bytes.fromhex(hex_encoded)
    length = len(encoded_bytes)
    possible_messages = []
    for key in range(256):
        padded_key = bytes([key] * length)
        decoded = xor_bytes(encoded_bytes, padded_key)  # because XOR is reversible.
        try:
            text = decoded.decode()
            possible_messages.append((english_score(text), text))
        except Exception as _:
            continue
    possible_messages.sort(reverse=True)
    return possible_messages[0]


if __name__ == '__main__':
    hex_string = "1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736"
    print(single_byte_xor_decrypt(hex_string))
