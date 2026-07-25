ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def convert_hex_to_base64(hex_string: str) -> str:
    raw_bytes = bytes.fromhex(hex_string)
    b64_chars = []
    length = len(raw_bytes)

    # Full 3-byte groups: start indices 0, 3, ... up to the last complete group.
    for i in range(0, length - 2, 3):
        chunk = (raw_bytes[i] << 16) | (raw_bytes[i + 1] << 8) | raw_bytes[i + 2]
        b64_chars.extend([
            ALPHABET[(chunk >> 18) & 63],
            ALPHABET[(chunk >> 12) & 63],
            ALPHABET[(chunk >> 6) & 63],
            ALPHABET[chunk & 63]
        ])

    # Leftover 1 or 2 bytes: pad with zero bits on the right, then add '='.
    remainder = length % 3
    if remainder == 2:
        j = length - 2
        chunk = ((raw_bytes[j] << 8) | raw_bytes[j + 1]) << 2  # 16 -> 18 bits
        b64_chars.extend([
            ALPHABET[(chunk >> 12) & 63],
            ALPHABET[(chunk >> 6) & 63],
            ALPHABET[chunk & 63],
            "="
        ])
    elif remainder == 1:
        chunk = raw_bytes[length - 1] << 4  # 8 -> 12 bits
        b64_chars.extend([
            ALPHABET[(chunk >> 6) & 63],
            ALPHABET[chunk & 63],
            "==",
        ])
    return "".join(b64_chars)


if __name__ == '__main__':
    print(convert_hex_to_base64("61626364"))
