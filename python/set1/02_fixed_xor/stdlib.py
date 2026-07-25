from cryptolib import xor_bytes


def fixed_xor(first: str, second: str) -> str:
    """
    Takes 2 equal length buffers and produces their XOR combination
    """
    first_bytes = bytes.fromhex(first)
    second_bytes = bytes.fromhex(second)

    return xor_bytes(first_bytes, second_bytes).hex()


if __name__ == '__main__':
    string1 = "1c0111001f010100061a024b53535009181c"
    string2 = "686974207468652062756c6c277320657965"
    print(fixed_xor(string1, string2))
