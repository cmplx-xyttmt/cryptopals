def pkcs7(data: bytes, block_size: int) -> bytes:
    padding = block_size - len(data) % block_size
    padded_data = data + bytes([padding] * padding)
    return padded_data


if __name__ == '__main__':
    data_ = "YELLOW SUBMARINE".encode()
    print(pkcs7(data_, 20))
