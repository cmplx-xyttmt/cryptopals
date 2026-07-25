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
  `base64.b64encode`). Then wrote the scratch version (my own base64 encoder) —
  that's where the 3-bytes→4-chars grouping actually got internalised.
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
  - This was a bit challenging. After looking up the rules, the trickiest part was the "3-to-4 bit" transformation.
  - After failing to think of a nice way to split a 24-bit number into 6 distinct integers, I searched online and found an interesting way of doing that: First, creating the 24-bit chunk from the 3 bytes. Then using right shifts and bitwise-AND to split it into 6-bit integers.
  - After getting some critique from Gemini, I improved the solution to use 1 function, use a string instead of a dictionary as the index and optimizing memory by mapping characters on the fly and streaming them into the final string accumulator.

- **The refactor arc (worth showing in the post — it's the "AI as critic" loop in miniature):**
  - **v1 (my original — commit `3ff410c`):** three functions —
    `build_index()` built a `{0:'A', 1:'B', …}` dict, `three_to_four_bit_transform()`
    produced a list of 6-bit ints (+ a `padding` count), and `convert_hex_to_base64()`
    mapped ints→chars. Correct, but ~80 lines, a stray debug `print`, and it
    sliced `raw_bytes = raw_bytes[3:]` every loop.
  - **v2 (after Gemini's critique — current `scratch.py`):** collapsed to one
    function. Key realisations:
    - A **string is already an int→char map** — `ALPHABET[i]` does exactly what the
      dict did, because the indices 0–63 *are* the keys. The whole `build_index()`
      disappears.
    - **Map on the fly** — index into `ALPHABET` as each 6-bit group is computed and
      stream chars straight into the accumulator, instead of building a whole
      intermediate list of ints first.
    - (Bonus I didn't clock at the time: switching from `raw_bytes = raw_bytes[3:]`
      to an index `i += 3` also turns an accidental **O(n²)** — re-copying the tail
      each loop — into **O(n)**.)
  - **Why the padding shifts work (so future-me remembers the *why*, not just the *how*):**
    base64 packs 8-bit bytes into 6-bit groups; 3 bytes = 24 bits = 4 groups exactly.
    Leftovers get **zero bits padded on the right** to fill the last group, then `=`
    records how many bytes were real. `chunk <<= 2` (2 leftover bytes: 16→18 bits)
    and `byte << 4` (1 leftover byte: 8→12 bits) *are* that right-zero-padding, done
    as arithmetic. So the trick I found online is principled, not magic.

- **v3 — Claude's "make the special case disappear" version (a different technique, kept for reference):**
  Instead of two remainder branches, pad the input bytes up to a multiple of 3
  with zero bytes, run one clean loop, then overwrite the trailing chars with `=`
  (one per padding byte added):
  ```python
  B64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

  def convert_hex_to_base64(hex_string: str) -> str:
      raw = bytes.fromhex(hex_string)
      pad = (-len(raw)) % 3                # 0, 1, or 2 zero-bytes to add
      raw = raw + b"\x00" * pad
      out = []
      for i in range(0, len(raw), 3):
          chunk = (raw[i] << 16) | (raw[i+1] << 8) | raw[i+2]
          for shift in (18, 12, 6, 0):
              out.append(B64_ALPHABET[(chunk >> shift) & 63])
      if pad:                             # replace the last `pad` chars with '='
          out[-pad:] = "=" * pad
      return "".join(out)
  ```
  Trade-off: v2 makes the mechanism *visible* (good for learning); v3 removes
  duplication via a "normalise then handle uniformly" trick I'll reuse elsewhere.
  Neither is strictly better — the contrast is the point.

- **Small nits still open in v2 (from Claude's review):** `ALPHABET` should live at
  module scope (it's a constant, currently rebuilt each call); the `while i <= length - 3`
  could be the more Pythonic `for i in range(0, length - 2, 3)`; and `chunk <<=2`
  wants a space (`chunk <<= 2`).

- **Blog hook (scratch):** three versions of the same 30-line function —
  mine, Gemini's, Claude's — each teaching a different lesson (a string *is* a
  lookup table; stream don't buffer; make the special case vanish). A tiny,
  concrete illustration of using multiple AI critics and keeping what each is
  good at.

- **Status:** solved — both versions done (stdlib + scratch v2). v2 nits optional.
