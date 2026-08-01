from cryptolib import xor_bytes, english_score


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
        except UnicodeDecodeError as _:
            continue
    possible_messages.sort(reverse=True)
    return possible_messages[0]


if __name__ == '__main__':
    hex_string = "1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736"
    print(single_byte_xor_decrypt(hex_string))
