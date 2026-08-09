def repeating_key_xor(text: bytes, key: bytes) -> bytes:
    encoded = []
    for idx, tbyte in enumerate(text):
        encoded.append(tbyte ^ key[idx % len(key)])
    encoded = bytes(encoded)
    return encoded


if __name__ == '__main__':
    text = """Burning 'em, if you ain't quick and nimble
I go crazy when I hear a cymbal"""
    key = "ICE"
    expected = "0b3637272a2b2e63622c2e69692a23693a2a3c6324202d623d63343c2a26226324272765272a282b2f20430a652e2c652a3124333a653e2b2027630c692b20283165286326302e27282f"
    encrypted = repeating_key_xor(text.encode(), key.encode())
    print(encrypted.hex() == expected)
    print(encrypted.hex())
