import random, statistics
from cryptolib import repeating_key_xor

# Experiment 1: confirming that English xor English results in fewer bits vs random xor random
letters = "abcdefghijklmnopqrstuvwxyz"
w = lambda x: bin(x).count('1')

eng = [w(ord(random.choice(letters)) ^ ord(random.choice(letters))) for _ in range(100_000)]
rnd = [w(random.randrange(256) ^ random.randrange(256)) for _ in range(100_000)]
print("english ^ english, avg differing bits:", round(statistics.mean(eng), 2))
print("random ^ random, avg differing bits:", round(statistics.mean(rnd), 2))

# ================================================================

# Experiment 2
text = b'the quick brown fox jumps over the lazy dog again and again and again'
key = b'KEY'
ciphertext = repeating_key_xor(text, key)
K = len(key)
w = lambda x: bin(x).count("1")

apart_K = [w(ciphertext[i] ^ ciphertext[i + K]) for i in range(len(ciphertext) - K)]
adjacent = [w(ciphertext[i] ^ ciphertext[i + 1]) for i in range(len(ciphertext) - 1)]
print("bytes K apart, avg differing bits:", round(statistics.mean(apart_K), 2))
print("adjacent bytes, avg differing bits:", round(statistics.mean(adjacent), 2))

print("ciphertext[i] ^ ciphertext[i + K] == text[i] ^ text[i + k] for all i? :", all(ciphertext[i] ^ ciphertext[i + K] == text[i] ^ text[i + K] for i in range(len(ciphertext) - K)))
