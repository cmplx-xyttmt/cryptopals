from cryptolib import xor_bytes, english_score, single_byte_xor_decrypt


if __name__ == '__main__':
    hex_string = "1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736"
    encoded_bytes = bytes.fromhex(hex_string)
    print(single_byte_xor_decrypt(encoded_bytes))
