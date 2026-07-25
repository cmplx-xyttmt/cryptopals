def build_index():
    uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lowercase = "abcdefghijklmnopqrstuvwxyz"
    numbers = "0123456789"

    b64_char_index = dict()
    for value in range(26):
        b64_char_index[value] = uppercase[value]

    for value in range(26, 52):
        b64_char_index[value] = lowercase[value - 26]

    for value in range(52, 62):
        b64_char_index[value] = numbers[value - 52]

    b64_char_index[62] = "+"
    b64_char_index[63] = "/"

    return b64_char_index


def three_to_four_bit_transform(raw_bytes: bytes) -> tuple[list[int], int]:
    """
    Groups data into blocks of 3 bytes (24 bits) and splits them into 4 segments of 6 bits each.
    Returns a list of the 6-bit integers.
    :param raw_bytes:
    :return: list of the 6-bit integers
    """
    six_bit_ints = []
    while len(raw_bytes) >= 3:
        buffer = raw_bytes[0:3]
        b1, b2, b3 = buffer
        chunk = (b1 << 16) | (b2 << 8) | b3  # combining the 3 bytes into a 24-bit chunk.

        # Pulling out 6-bit pieces from left to right
        p1 = (chunk >> 18) & 63
        p2 = (chunk >> 12) & 63
        p3 = (chunk >> 6) & 63
        p4 = chunk & 63
        six_bit_ints.extend([p1, p2, p3, p4])
        raw_bytes = raw_bytes[3:]

    padding = 0
    if len(raw_bytes) == 2:
        # remainder of 2 bytes, append 2 0-bits
        b1, b2 = raw_bytes
        chunk = (b1 << 8) | b2  # 16-bit number
        chunk <<= 2  # left-shift to make it an 18-bit number

        # Pulling out 6-bit pieces.
        p1 = (chunk >> 12) & 63
        p2 = (chunk >> 6) & 63
        p3 = chunk & 63
        six_bit_ints.extend([p1, p2, p3])
        padding = 1
    elif len(raw_bytes) == 1:
        # remainder of 1 bytes, append 4 0-bits
        chunk = raw_bytes[0] << 4  # left-shift to make it a 12-bit number

        # Pulling out 6-bit pieces
        p1 = (chunk >> 6) & 63
        p2 = chunk & 63
        six_bit_ints.extend([p1, p2])
        padding = 2
    return six_bit_ints, padding


def convert_hex_to_base64(hex_string: str) -> str:
    raw_bytes = bytes.fromhex(hex_string)
    six_bit_ints, padding = three_to_four_bit_transform(raw_bytes)
    b64_char_index = build_index()
    b64 = [b64_char_index[value] for value in six_bit_ints]
    print(six_bit_ints)
    return "".join(b64) + "=" * padding


if __name__ == '__main__':
    print(three_to_four_bit_transform(b"abc"))
    print(convert_hex_to_base64("61626364"))
