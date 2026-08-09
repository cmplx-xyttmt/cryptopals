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

### Challenge 2 — Fixed XOR · [link](https://cryptopals.com/sets/1/challenges/2)

- **Concept it teaches:** XOR over equal-length byte buffers — the single most
  reused primitive in Set 1 (challenges 3, 4, 5, 6 all build on it). Also a
  second dose of the bytes-vs-text lesson, from the opposite direction.
- **First approach:** `bytes.fromhex` both inputs, XOR them with a comprehension
  (`a ^ b for a, b in zip(...)`), return `.hex()`. Core logic was right first try.
- **Wrong turns / bugs:** I left in a debug line — `xor.decode('ascii')` + a
  `print` — from checking that the answer spelled "the kid don't play". That's a
  latent crash: XOR output is *arbitrary bytes*, not text, so `decode('ascii')`
  blows up (`UnicodeDecodeError`) the moment a byte is ≥ 128. The official vector
  hid it because that particular result happens to be printable ASCII.
- **How it got caught — the executable critique:** wrote `test_challenge02.py`
  first, and 4 of 6 tests went red immediately, all with the same
  `UnicodeDecodeError` on byte `0x80`. The failing test I'd added on purpose was
  `test_non_ascii_result_is_fine` (`"00" ^ "80"` should just be `"80"`). Removing
  the two debug lines turned it green. Nice demonstration of tests surfacing a
  bug that the official example actively concealed.
- **Critique → change:**
  - Deleted the `decode('ascii')` + `print` (the function returns hex; letting a
    caller interpret the bytes is *their* job).
  - Added an equal-length guard (`raise ValueError` on mismatch) — `zip` silently
    truncates otherwise, which is wrong for a *fixed* XOR.
  - Started a shared `python/cryptolib/` package with a reusable
    `xor_bytes(a: bytes, b: bytes) -> bytes` core, since every later challenge
    needs it. Hit (and fixed) two snags: a copy-paste guard bug (`len(a) != len(a)`
    — always False) and, more instructively, an *import* problem.
- **The import lesson (packaging, my first real Python packaging setup):** you
  can only `import cryptolib` if its parent dir (`python/`) is on `sys.path`.
  Running a script from inside `set1/02_fixed_xor/` only puts *that* folder on the
  path, so `cryptolib` was invisible → `ModuleNotFoundError`. Fixed it the proper
  way: a `pyproject.toml` declaring `cryptolib` as a package + `pip install -e .`,
  which links it into the venv so it imports from anywhere (scripts, tests, REPL)
  with no `sys.path` hacks. Side note learned: the `set1/NN_slug/` dirs can never
  be packages — names starting with a digit aren't importable — so solutions stay
  as directly-run scripts, and only `cryptolib` is a package.
- **stdlib vs scratch:** decided **no separate scratch version** here, and noted
  why: XOR *is* already from-scratch — `a ^ b` in a loop is me computing the
  primitive by hand; there's no library doing the work. The only stdlib
  conveniences are `bytes.fromhex`/`.hex()` (notation), and I already hand-rolled
  the analogous thing (base64) in Challenge 1. Per our CLAUDE.md convention,
  documented the single-version decision instead of writing a pointless file.
  (Optional-for-fun idea parked: hand-roll hex decode/encode to complete the
  "notation from scratch" set.)
- **Tests:** `test_challenge02.py` — official vector, returns-str, XOR identity
  (`x ^ 0 == x`), bit-flip (`x ^ 0xFF`), self-inverse (`(a ^ b) ^ b == a`, the
  property every XOR cipher leans on), and the non-ASCII-result guard. 6 passing.
- **Artifact:** none yet. (XOR bit-mixing could make a nice visual later, maybe
  when Challenge 5's repeating-key XOR makes it worth it.)
- **Blog hook:** "the test that failed for the right reason." A one-liner debug
  print that passed the official example but was a crash waiting to happen, caught
  the instant I wrote a test with a non-text result. Concrete case for writing
  tests *and* for the bytes-aren't-text mental model — and it pairs with the
  Challenge 1 artifact perfectly.
- **Status:** solved (stdlib, with equal-length guard). No scratch by design.
  `cryptolib.xor_bytes` extracted for reuse; `stdlib.fixed_xor` could be
  refactored to call it (optional tidy).

### Challenge 3 — Single-byte XOR cipher · [link](https://cryptopals.com/sets/1/challenges/3)

- **Concept it teaches:** Breaking a single-byte XOR "cipher" by brute-forcing all
  256 keys and scoring each candidate plaintext for how English-like it is. First
  taste of frequency analysis — the idea that structure in the plaintext leaks
  through, so you don't need the key, you need a way to *recognise* English.
- **First approach (mine):** brute force all 256 keys with `xor_bytes`, decode each
  to text, and score it. Decrypted the message to **"Cooking MC's like a pound of
  bacon"** — correct!
  - The hardest part was the **character frequency scoring**, and I'm still not
    sure I did it the best way. I looked up the most common English letter order
    (`ETAOIN…`) and scored a candidate by how close each character's *count* is to
    its *position* in that order, summing a reward that's larger the smaller the
    difference, and subtracting a penalty for expected characters that are missing.
  - **Thing I had to watch out for: spaces vs other characters.** The string
    `cOOKING\x00mc\x07S\x00LIKE\x00A\x00POUND\x00OF\x00BACON` scored *very* high — in
    fact it was the **winning** candidate — until I added a space to the end of
    `character_order`. That fixed it, but it felt like a patch, not a principle.
- **Open question I want to resolve (parked for study):** Claude's critique says my
  scorer works only by luck — it compares a *count* to a *rank index* (different
  units), and only discriminates correctly because all 256 candidates in one
  decrypt call share the same length, so the length bias cancels. The suggested
  fix is a frequency-weighted, length-normalised score that (a) puts **space at the
  top** (it's the single most common character in English, ~18%, which is exactly
  why my control-char string could win) and (b) explicitly penalises non-printable
  bytes. Length-normalisation apparently matters for Challenge 4, where you compare
  scores *across* different ciphertext lines. → I'll study this before applying.
- **Tests:** `test_challenge03.py` — round-trips a corpus of 12 English sentences
  through 6 keys each (encrypt → solve → must recover the original), plus the
  official vector and two scorer-discrimination tests (English must out-score
  random bytes and the exact `\x00`/`\x07` control-char string that fooled me).
  75 passing — so the scorer *does* work on this corpus, even if it's fragile.
- **Interface smells noted (from critique):** `single_byte_xor_decrypt` is typed
  `-> str` but returns a `(score, text)` tuple, and has a leftover `print(text)`
  (256 lines/call — same debug-print pattern as Challenge 2). Challenge 4 will want
  the *key* + *score* too, so a reusable `single_byte_xor(data: bytes) -> XorResult`
  in `cryptolib` is the likely refactor.
- **Blog hook:** "the scorer that worked for a reason I didn't expect." I patched
  the space bug by trial and error and moved on; the critique explained the
  *actual* mechanism (equal-length cancellation) and why it'd wobble in Challenge 4.
  Classic case of AI turning "it works ¯\\_(ツ)_/¯" into understanding.
- **Resolution:** turned out my *intent* was closeness-to-rank-position, but I'd
  coded closeness of raw **count** to position (different units) — that was the
  bug. Before rewriting, we banked two `xfail(strict=True)` regression tests that
  failed on the old scorer; the sharpest was **repetition-invariance** (repeating
  a text keeps its frequency ranking, so a correct score must be unchanged — the
  old one jumped 383→429). Replaced it with a frequency-weighted, length-normalised
  `english_score` (space weighted highest; control bytes penalised), moved to
  `cryptolib` for reuse. The strict-xfail tests then flipped to XPASS (the "bug is
  gone" signal), so I removed the markers — they're permanent green guards now.
- **Status:** solved — stdlib with `cryptolib.english_score`. No scratch (XOR/scoring
  need no from-scratch treatment). Regression tests green. `single_byte_xor_decrypt`
  still returns a `(score, text)` tuple typed `-> str` — likely refactored into a
  reusable `cryptolib.single_byte_xor` for Challenge 4.

### Challenge 4 — Detect single-character XOR · [link](https://cryptopals.com/sets/1/challenges/4)

- **Concept it teaches:** one of 60 hex lines is single-byte-XOR'd English; find
  it. It's really Challenge 3 applied to every line, then picking the global
  winner — which only works if scores are comparable *across* lines. This is
  where Challenge 3's **length-normalised** `english_score` pays off: without
  normalisation, comparing best-scores between different lines would be unfair.
- **My approach:** for each line, run `single_byte_xor_decrypt` (now in
  `cryptolib`, moved as suggested and changed to take `bytes`), collect the best
  result per line, and take the max. Answer: **"Now that the party is jumping\n"**
  (key 53 / `'5'`). Correct.
- **Things I learned / got caught on:**
  - **`namedtuple` finally clicked.** I'd defined `XorResult = namedtuple("XorResult",
    "key score plaintext")` and annotated `-> XorResult`, but hadn't actually
    wired it up — the function still returned a bare `(score, text)` tuple and
    threw the key away. Completing it to return `XorResult(key, score, plaintext)`
    is what made namedtuple make sense to me: it's a tuple with *named* fields.
  - **The sort-by-key trap (subtle, important).** My detection did
    `scores.sort(reverse=True); return scores[0]`. That worked only while the
    return was `(score, text)` (sorts by score). The moment it became
    `XorResult(key, score, plaintext)`, a bare sort compares **field 0 = key**
    first — so it'd silently return the highest-*key* result, not the best score.
    Fix: `max(candidates, key=lambda r: r.score)`. Lesson: when sorting/maxing
    namedtuples, be explicit with `key=` unless field order *is* your sort order.
  - **Hardcoded `open("4.txt")`** only worked when cwd was the challenge folder —
    which is why I couldn't run it from the repo root or under pytest. Fixed with a
    path anchored on the repo root, and moved the data file to `data/04.txt` to
    match the CLAUDE.md convention (inputs committed under `data/`).
  - Split into a pure `detect_single_char_xor(hex_lines)` + a `__main__` that reads
    the file, so it's testable with synthetic data, not just the bundled file.
- **Tests:** `test_challenge04.py` — the real-file answer, a *planted-line-among-
  decoys* test (bury one XOR'd English sentence in gibberish and detect it), and
  blank-line handling. The reusable solver + scorer tests moved to
  `test_cryptolib.py` (round-trip recovering plaintext **and** key, empty and
  never-decodes sentinel cases); `test_challenge03.py` was deleted as redundant.
- **Blog hook:** the namedtuple sort-by-key gotcha — code that's correct with a
  plain tuple becomes silently wrong when you "upgrade" to a namedtuple, because
  tuple ordering follows field order. A tiny, real bug that the AI flagged *before*
  it could bite. Pairs with "I finally understood namedtuple."
- **Status:** solved (stdlib). Reusable `single_byte_xor_decrypt` now returns a
  proper `XorResult`. No scratch planned.

### Challenge 5 — Implement repeating-key XOR · [link](https://cryptopals.com/sets/1/challenges/5)

- **Concept it teaches:** repeating-key (Vigenère-style) XOR — cycle a short key
  over the plaintext, XOR byte by byte. Sets up Challenge 6 (breaking it).
- **My initial solution:** felt fairly straightforward. I took `text` and `key`
  as strings, encoded both, and XOR'd each text byte with `key_bytes[idx % 3]`,
  returning hex. It matched the official "ICE" vector, so I thought it was done.
- **The bug (an easy one to make):** I'd hardcoded `% 3` — which is just the
  length of "ICE" leaking into the code. **Claude caught this**, and pointed out
  it's the same family of mistake as earlier ones (the `character_order` space,
  the `open("4.txt")` path): it works for the single example but breaks the
  instant the input changes. Claude demonstrated it live — a length-2 key
  *crashes* with `IndexError`, and a length-4 key runs but is *silently wrong*
  (wraps at 3, ignores the 4th key byte). The fix is `% len(key)`.
- **Claude's further advice (the "learning partner" bit, not just a fix):**
  - Since Challenge 6 needs to XOR ciphertext *bytes* with a repeating key to
    decrypt, make the core `bytes`-in/`bytes`-out and put it in `cryptolib`. I've
    already switched the signature to `bytes -> bytes` for that reason.
  - Repeating-key XOR is **symmetric** (same op encrypts and decrypts) — so the
    one function also decrypts, which is exactly what Challenge 6 will use.
  - `itertools.cycle(key)` expresses "repeat the key forever" directly and is
    *immune to the length bug by construction* (no manual modulus to get wrong).
    Planned refactor: `bytes(b ^ k for b, k in zip(data, cycle(key)))`.
- **Tests:** `test_challenge05.py` — official ICE vector, a **differential** test
  against an independent `cycle`-based oracle across key lengths 1–5 (this is what
  the `% 3` bug was really about), single-char key == single-byte XOR, key longer
  than text, empty input, and a **round-trip symmetry** test (encrypt twice ==
  original) that only became expressible once the interface was `bytes`. 20 tests.
- **Plan:** commit this (fixed-with-modulus, in-place) version first, then refactor
  into `cryptolib.repeating_key_xor` using `cycle`, as its own commit.
- **Blog hook:** "hardcoding the example." Three challenges in a row I baked a
  property of the *one given example* into the code (`ICE`→`% 3` here). Each time
  Claude caught it the same way — by running the code on inputs *off* the example.
  A concrete lesson in how an AI critic tests differently than I instinctively do.
- **Process note (feedback to Claude):** I realized Claude was mentioning other
  challenges while I was solving the current one, which would usually give me
  hints. I therefore prompted it to take note of this and edit its memory and the
  CLAUDE.md file to avoid spoilers going forward. (Good blog material on where the
  AI-as-tutor approach needs guardrails.)
- **Status:** solved (stdlib, `bytes`-based, modulus). Refactor to
  `cryptolib` + `cycle` pending (separate commit). No scratch planned.

### Challenge 6 — Break repeating-key XOR · [link](https://cryptopals.com/sets/1/challenges/6) · (in progress)

- **Concept it teaches:** breaking Vigenère-style XOR with no key and no key length —
  guess the key length via Hamming distance, then split into single-byte-XOR problems.
- **Understanding phase (before coding):** I was confused about *why* Hamming distance
  should reveal the key length. Rather than explain it, Claude built an interactive
  artifact — `interactive/vigenere-keysize.html` — where I encrypt text with a key I
  choose, sweep candidate key lengths, and watch the normalised Hamming distance dip at
  the true length (and its multiples). It also has a bit-level view and Socratic prompts.
- **How I worked it out (the part I'm proud of):** I formed a hypothesis (XOR of two
  English letters has few 1-bits because their byte values are clustered). Claude
  confirmed that half was right but pointed out the gap — the ciphertext bytes aren't
  English, so *what happens to the key?* — and suggested two experiments (see
  `06_break_repeating_key_xor/experiments.py`). Running them, I derived it myself:
  at the correct keysize the two bytes share a key byte, so `c1 ⊕ c2 = (p1⊕k) ⊕ (p2⊕k)
  = p1 ⊕ p2` — the key cancels (because `k ⊕ k = 0`), leaving English⊕English (few
  bits). At a wrong keysize the key bytes differ, leaving a scrambling `kA ⊕ kB` term
  (many bits). The artifact's reveal box now holds that full explanation.
- **Process note:** this was the AI-as-tutor loop working well — a visualization + guided
  experiments led me to the insight instead of being handed it. (Contrast with the
  earlier session where Claude *over*-shared about this challenge; we added a no-spoiler
  rule to CLAUDE.md after that. Both are useful blog material.)
- **Status:** in progress — understand keysize detection; now implementing the full break.
