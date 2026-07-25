import base64


def convert_hex_to_base64(hex_string: str) -> str:
    raw_bytes = bytes.fromhex(hex_string)
    b64 = base64.b64encode(raw_bytes)
    return b64.decode("ascii")   # bytes -> str, so callers get clean text


if __name__ == '__main__':
    string = "49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d"
    print(convert_hex_to_base64(string))
    print(convert_hex_to_base64("61626364"))
