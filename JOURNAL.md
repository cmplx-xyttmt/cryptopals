# Cryptopals Journal

A running log of working through the [Cryptopals challenges](https://cryptopals.com/):
what I tried, where I went wrong, what the critique taught me, and the ideas
worth turning into a blog post. Newest entries at the top of each set.

> **Thesis for the eventual post:** using AI as a learning partner — an on-demand
> tutor and code critic — plus building small interactive artifacts to explore
> the tricky bits. This journal is the raw material; keep it honest and specific.

---

## Entry template (copy this per challenge)

### Challenge NN — <title> · [link](https://cryptopals.com/sets/N/challenges/NN)

- **Concept it teaches:** <the crypto idea underneath>
- **First approach:** <what I tried first, in my own words>
- **Wrong turns / bugs:** <what broke and *why* — the good stuff for the blog>
- **Critique → change:** <what the review flagged, what I changed>
- **stdlib vs scratch:** <what each version taught; anything surprising>
- **Artifact:** <interactive/xyz.html, if any — and what it made click>
- **Blog hook:** <one line if there's a story here, else "—">
- **Status:** not started / attempted / solved / both versions done

---

## Set 1 — Basics

### Challenge 1 — Convert hex to base64 · [link](https://cryptopals.com/sets/1/challenges/1)

- **Concept it teaches:** Everything in crypto is *bytes*, not text. Hex and
  base64 are just two different human-readable *notations* for the same
  underlying bytes; the challenge is really "move between notations without
  losing track of the raw bytes in the middle."
- **First approach:** Took me a while to understand how to work on raw bytes. I
  had to look up functions like `bytes.fromhex` and the base64 library. I can
  also feel a bit of the atrophying from using coding agents to write most of my
  code the past few months — but fun to get back into it.
- **Wrong turns / bugs:** My function returned the base64 as `bytes`, so
  printing it showed `b'SSdt...'` and I didn't know what the `b` meant. Turned
  out `base64.b64encode` returns `bytes`, and I was seeing its `repr`.
- **Critique → change:** Added `.decode("ascii")` to return a clean `str`. The
  bigger lesson from the critique: I'd assumed "raw bytes are hex" — but bytes
  are *numbers* (0–255), and hex is just one way to write them. `bytes.fromhex`
  reads the hex *text* and produces the actual byte numbers.
- **Things that clicked:**
  - `list(b"Hi")` → `[72, 105]` — bytes really are just a list of ints.
  - `b"Hi"[0]` → `72` (an int) but `"Hi"[0]` → `'H'` (a str). Different worlds.
  - You can XOR bytes (`b"Hi"[0] ^ 42`) but not str — which is *why* crypto
    lives in the bytes world. Challenge 2 is exactly this.
  - Default encoding is **UTF-8**, not ASCII (I guessed ASCII). They match for
    plain English, but `"é".encode()` → `b'\xc3\xa9'` (1 char → 2 bytes).
- **stdlib vs scratch:** Only did `stdlib` so far (`bytes.fromhex` +
  `base64.b64encode`). Scratch version (my own base64 encoder) still TODO — good
  next step to really internalise the 3-bytes→4-chars grouping.
- **Tests:** `test_challenge01.py` — official vector, str-not-bytes guard, all
  three base64 padding cases, empty input, odd-length-hex rejection. 11 passing.
- **Artifact:** `interactive/bytes-vs-strings.html` — type text, watch it become
  bytes → hex → base64, with the encoding table and byte/str operations shown.
  Built specifically because the bytes-vs-str distinction is hard to *see*.
- **Blog hook:** The "I thought raw bytes were hex" misconception is the perfect
  opening for the AI-tutor thesis — a wrong mental model I'd probably have
  carried for weeks got caught and unpicked in one exchange, then turned into an
  artifact I can actually play with. That loop (misconception → critique →
  interactive artifact) *is* the post.
- **Solving from scratch**
  - This was a bit challenging. After looking up the rules, and the trickiest part was the "3-to-4 bit" transformation.
  - After failing to think of a nice way to split a 24-bit number into 6 distinct integers, I searched online and found an interesting way of doing that: First, creating the 24-bit chunk from the 3 bytes. Then using right shifts and bitwise-AND to split it into 6-bit integers. 
- **Status:** solved (stdlib); (scratch).
