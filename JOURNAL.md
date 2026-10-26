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
- **Debugging log (first attempt, not yet correct):** two symptoms while debugging:
  (1) the keysize scores for the top ~20 candidates were all bunched together
  (~2.70–2.79) with no clear winner, and they looked like multiples of 29 — so no
  confident keysize; (2) the recovered "keys" came out as the same byte repeated
  (a run of T's), and none decrypted to anything coherent. Mid-writeup I remembered
  the artifact's *blocks-averaged* lesson (more block pairs → clearer signal) and
  went to try increasing the number of blocks averaged before asking for a hint.
  Claude reviewed and nudged (without giving it away) that these are *two separate*
  bugs — the averaging idea addresses symptom (1), but symptom (2) is a different
  error in how the key is built and won't be fixed by more averaging.
- **The two bugs that cracked it:**
  1. **Transposition off-by-start.** My inner loop ran `for j in range(0, len, K)`
     and appended `ciphertext[j]` — with no `i` offset, so *every* block collected
     the same bytes (positions 0, K, 2K…). Identical blocks → `single_byte_xor_decrypt`
     returned the same byte for each → the key came out as one letter repeated
     (a run of T's). Claude didn't tell me; it nudged me to print the indices each
     block collected and compare block 0 vs block 1 — the fix was `range(i, len, K)`
     (start at `i`).
  2. **Keysize clustering.** I'd scanned a huge candidate range, so 29 and its
     multiples all bunched near ~2.7 with no clear winner. Restricting to 2..40
     made **29** the clear winner, even with only a few blocks averaged.
- **Answer:** keysize **29**, key **`Terminator X: Bring the noise`**, plaintext is
  the "Play That Funky Music" lyrics ("I'm back and I'm ringin' the bell …").
- **The multiples question (worked out myself):** multiples of the true keysize
  also score well because a repeated key is an equally-valid key — `key` and
  `keykey` produce the same keystream. Bit-wise: bytes 2K apart still share a key
  byte (same `p mod K`), so the key still cancels and you're still comparing
  English⊕English. My synthetic test literally shows this: a 5-byte key `MOON!`
  gets detected as keysize **15** and recovered as `MOON!MOON!MOON!`, which still
  decrypts perfectly.
- **Cleanups (Claude suggested, I applied):** transpose with a slice `ct[i::K]`
  instead of hand-building blocks; `min(range(2, MAX_KEY_SIZE+1), key=…)` instead of
  sort-then-index; named the `40` bound; `.key` on the `XorResult`. Moved
  `hamming_distance` into `cryptolib` (with a comment explaining the
  `int.from_bytes(...).bit_count()` whole-buffer popcount trick).
- **Tests:** `TestHammingDistance` in `test_cryptolib` (the 37 vector, symmetry,
  leading-zero-byte counting, unequal-length raises); `test_challenge06.py` breaks
  the real file (asserts key + first line) and does a synthetic blind break with a
  round-trip that also demonstrates the keysize-multiple effect.
- **Blog hook:** "the run of T's." A one-character transposition bug (start at `i`,
  not `0`) with a very specific symptom, found by *printing indices* rather than
  being handed the fix — plus the multiples insight reasoned out from first
  principles. The debug-with-the-AI-but-don't-get-spoon-fed loop, concretely.
- **Status:** solved (stdlib). No scratch — it's byte/logic work reusing cryptolib
  primitives. Artifact extension (visualise the full break) still to come.

### Challenge 7 — AES in ECB mode · [link](https://cryptopals.com/sets/1/challenges/7) · (stdlib)

- **Concept it teaches:** first block cipher. AES-128 in **ECB** (Electronic
  Codebook) mode: split the data into 16-byte blocks and encrypt/decrypt each
  block independently under the same key. Key = `YELLOW SUBMARINE` (16 bytes).
- **Depth question I asked first:** the AES internals looked complicated — did I
  need to study them? Claude's steer: **no** — AES the block cipher (S-boxes, key
  schedule, rounds) is a rabbit hole you offload to a library; the *actual* concept
  here is ECB as a **mode of operation**, which is simple ("encrypt each 16-byte
  block independently"). Study the mode, not the math. Good depth-calibration —
  knowing what you *don't* need to learn is itself useful.
- **My approach:** `Crypto.Cipher.AES.new(key, AES.MODE_ECB).decrypt(ciphertext)`.
- **The bug (embarrassing but instructive):** I copy-pasted the `DATA_FILE` line
  from Challenge 6 and forgot to change `6.txt` -> `7.txt`. So I was feeding
  Challenge 6's *repeating-key-XOR* ciphertext into AES -> undecodable garbage.
  Worse, I went down a **padding rabbit hole** (tried padding short blocks with
  0s, then with the remainder) trying to fix it.
- **Claude's hint (decisive):** the tell was in the *data*, not the code — a valid
  AES-ECB ciphertext is always an exact multiple of 16 bytes, but `6.txt` decoded
  to a length that's **12 mod 16**. That non-alignment is exactly why I hit short
  final blocks and reached for padding. Fix = point at the right file; the whole
  padding branch then becomes unreachable. Claude also corrected my mental model:
  **padding lives on the plaintext side (before encryption); on decrypt you strip
  it, never add it to the ciphertext.** And: block size (16) is not the key length
  — they only coincide here because the key is 16 bytes.
- **Fix:** point `DATA_FILE` at `7.txt`; simplified to a single `decrypt` call on
  the whole ciphertext (ECB is stateless, so no manual block loop and no padding
  handling needed). Answer decrypts to the "Play That Funky Music" lyrics again
  ("I'm back and I'm ringin' the bell ...").
- **stdlib vs scratch:** stdlib only, by design — a from-scratch AES is a large
  separate project and isn't what this challenge teaches.
- **Tests:** I argued none are needed since it's just a library call. Fair for AES
  itself, but Claude pushed back that a single *known-answer* check tests our
  *wiring* (right file/key/mode) and would have caught the filename bug — so a
  one-line assertion is cheap insurance (decision pending).
- **Blog hook:** "the padding red herring." A plain plumbing bug (wrong filename)
  disguised itself as a crypto/padding problem, and I burned time treating the
  symptom. What cut through it wasn't staring harder at the code — it was a
  *property of the data* (length mod 16 must be 0 for AES ciphertext). Also a neat
  AI-tutor beat: the most useful early advice was "you do NOT need to study AES
  internals for this," calibrating how deep to go.
- **Status:** solved (stdlib). No scratch.

### Challenge 8 — Detect AES in ECB mode · [link](https://cryptopals.com/sets/1/challenges/8) · (stdlib)

- **Concept it teaches:** detect which of many ciphertexts was ECB-encrypted,
  using only ECB's determinism (same 16-byte plaintext block -> same ciphertext
  block). No key, no decryption.
- **First approach (wrong lens):** I reached for **Hamming distance** again (carry-
  over from Challenge 6) — lowest average distance across blocks. It gave a clear
  winner, but I wasn't convinced, and rightly so.
- **Claude's reframe (the key nudge):** AES ciphertext blocks look **random**, so
  two *different* blocks differ in ~half their bits — there's no statistical
  gradient to measure. Averaging Hamming distance is measuring noise; it only
  "worked" because identical blocks have distance **0**, dragging the average down.
  The real signal isn't *similar* blocks, it's **identical** ones. Reframe:
  stop measuring similarity, search for exact duplicate 16-byte blocks.
- **Fix:** for each line, split into 16-byte blocks and check for any exact
  duplicate (`len(set(blocks)) != len(blocks)`). Exactly one line qualifies —
  **line 132** — and you can even eyeball it: the block `08649af7...44cd283`
  repeats four times.
- **Cleanup insight:** my first version imported `AES`, `hamming_distance`,
  `statistics` and built an AES object — all unused. Detecting ECB needs **no key
  and no decryption**; it's purely structural. Removing the dead code made that
  point obvious.
- **Is this general? (the question I asked after):**
  - The *mechanism* is fully general and **false-positive-free**: a duplicate
    16-byte block essentially can't happen by chance in random ciphertext (2**128
    block space, birthday bound ~2**64), so duplicates ⟹ ECB.
  - But as a *detector* it has **false negatives**: it only fires if the plaintext
    had a repeated block. ECB without repeats is indistinguishable from random.
  - English prose rarely triggers it — 16 identical bytes is long, AND the repeat
    must land on the same **16-byte alignment** (offset mod 16). The challenge data
    was chosen to contain an aligned repeat.
  - ECB's real leak is on **repetitive/structured data** — the "ECB penguin"
    (a bitmap encrypted in ECB keeps its outline, because uniform-colour regions
    are identical plaintext blocks -> identical ciphertext blocks).
- **Artifact:** planning an "ECB penguin" visual next (encrypt an image in ECB vs a
  proper mode, side by side) to *see* why repetition leaks.
- **stdlib vs scratch:** stdlib only; no scratch.
- **Tests:** `test_challenge08.py` — known-answer (line 132) + `has_repeated_block`
  unit cases (adjacent repeat, all-distinct, non-adjacent repeat).
- **Blog hook:** "Hamming distance was a proxy for the real thing." I carried a
  tool that worked in Challenge 6 into a problem where it only *coincidentally*
  worked; the fix was recognising the signal was *exact equality*, not similarity.
  Plus the neat twist: you can detect ECB **without ever decrypting**.
- **Status:** solved (stdlib). **Set 1 complete.**

---

## Set 2 — Block crypto

### Challenge 9 — Implement PKCS#7 padding · [link](https://cryptopals.com/sets/2/challenges/9)

- **Concept it teaches:** Block ciphers only eat whole blocks, so a message has
  to be stretched to a multiple of the block size. PKCS#7 does it in a way that
  is *self-describing*: every pad byte's value is the number of pad bytes added.
  The `\x04` in the challenge's example isn't a magic constant; it's a count.
- **First approach:** (Claude to ask me how I thought about it, and write it
  here.) Code-wise:
  work out how many whole blocks the data needs (integer division, plus one if
  there's a remainder), compute the shortfall, and append that many copies of a
  pad byte. The pad byte was a parameter defaulting to `b'\x04'`.
- **Wrong turns / bugs:**
  - Passing the official vector for the wrong reason. `"YELLOW SUBMARINE"` to a
    20-byte block needs 4 pad bytes, and the default pad byte happened to be
    `\x04`, so the output matched. But `pkcs7(b"YELLOW SUB", 16)` produced six
    `\x04` bytes where PKCS#7 wants six `\x06` bytes. Claude caught this by
    running the function on a second input.
  - After fixing the pad value, I wasn't sure what `\x04` even *is*, and guessed
    hex text: `hex(padding).encode()`. That gives the 3-byte string `b'0x4'`,
    so the output was `b'YELLOW SUBMARINE0x40x40x40x4'`. `\x04` is Python's
    display of a single byte whose value is 4; the `\x` is notation, same
    lesson as Challenge 1 (bytes are numbers, hex is how the repr shows the
    unprintable ones). `bytes([4])` builds that byte.
  - Data that is already block-aligned (16 bytes to a 16-byte block) came back
    untouched. The spec adds a whole block of padding in that case, so a reader
    can always strip the padding by looking at the last byte.
- **Critique → change:** Claude: the pad byte must be *derived*, not passed in;
  the "how many to add" arithmetic can be one line using `%`, which also gives
  the full-block case for free; drop the redundant `bytes(...)` wrap; the
  `__main__` block should assert the expected answer instead of printing.
  Final version is three lines: `padding = block_size - len(data) % block_size`,
  then `data + bytes([padding] * padding)`. The `%` form gives a full block
  when the data is already aligned, which the ceiling-division version could
  not. Checked against pycryptodome's `pad` on 2000 random inputs: no
  mismatches.
- **stdlib vs scratch:** One file. The hand-written version *is* the scratch
  version; the "stdlib" counterpart is pycryptodome's `Crypto.Util.Padding.pad`,
  which the tests use as a reference rather than giving it its own file.
- **Tests:** `test_challenge09.py` — official vector, pad value equals pad
  count, aligned input gets a full block, empty input, one byte short, a
  property sweep over every length up to three blocks for six block sizes
  (padded length is a multiple, last byte says how many to strip, stripping
  returns the original), and a 500-case comparison against pycryptodome.
  13 passing.
- **Artifact:** —
- **Blog hook:** A test vector where the right answer hides a wrong model. One
  extra input exposed it. Possibly the cheapest "AI as critic" win so far: the
  critic didn't need to read the spec, just try a second example.
- **Status:** solved

### Challenge 10 — Implement CBC mode · [link](https://cryptopals.com/sets/2/challenges/10)

- **Concept it teaches:** Chaining. ECB encrypts every block independently, which
  is why identical plaintext blocks leak (Challenge 8, the penguin). CBC XORs each
  plaintext block with the previous *ciphertext* block before it goes into AES, so
  the same 16 bytes encrypt differently depending on what came before. The IV is
  what stands in for "the previous ciphertext block" when there isn't one yet.
- **First approach:** I read the last two lines of the statement as contradictory:
  one says build encryption out of the ECB function plus XOR, the next says decrypt
  the file. Working out my question to Claude, I answered half of it myself — the
  XOR *is* what they mean by "each ciphertext block is added to the next plaintext
  block", and it's the same fixed XOR from Challenge 2. Claude confirmed both
  directions were wanted: decrypt is the deliverable, encrypt gives me a round-trip
  test. Then I wrote both loops, and they were right first time.
- **Wrong turns / bugs:**
  - **The big one: I never base64-decoded the file.** `DATA_FILE.read_text().encode()`
    turns the base64 *characters* into bytes, so I was feeding AES the text
    `CRIwqt4+szDb...` as if it were ciphertext. Challenge 7 had `base64.b64decode`
    and I dropped it. I blamed the IV for this.
  - **"ASCII 0" and `ascii(0)`.** I couldn't tell whether "all ASCII 0
    (`\x00\x00\x00` &c)" meant the character `'0'` or the value 0, and reached for
    the builtin `ascii()`. But `ascii(0)` returns the *repr string* `'0'`, so
    `ord(ascii(0))` is 48 and my IV was sixteen copies of the character zero. The
    challenge means the NUL byte, value 0, which is literally what `\x00` spells.
    My commented-out `bytes([0] * BLOCK_SIZE)` was right all along.
  - **Third time for the same trap.** Challenge 1 was `b'SSdt'` and not knowing what
    the `b` meant. Challenge 9 was `hex(4)` giving the text `'0x4'` instead of the
    byte `\x04`. Now `ascii(0)` giving `'0'` instead of `\x00`. Every time, a
    function that *formats a number as text* when I wanted the raw byte.
  - **Padding only when the last block is short.** I padded inside the loop with
    `if len(block) < BLOCK_SIZE`, so a plaintext that's an exact multiple of 16
    got no padding at all — exactly the Challenge 9 bug again, one challenge later.
    And my own `pkcs7` already handles the aligned case, so the conditional was
    undoing the fix I'd just made.
  - **My round trip wasn't one.** `aes_cbc_decrypt` never strips padding, so
    encrypting 21 bytes and decrypting gave back 32 with `\x0b` × 11 on the end.
    It "passed" because I was eyeballing a `print` and the text looked right.
    Claude: an `assert x == pt` would have failed on the spot. Same lesson as
    Challenge 9 — a check that isn't `==` isn't a check.
- **Debugging thing worth keeping:** with the base64 fixed but the IV still wrong,
  only the *first 16 bytes* came out as garbage and the rest of the song was
  perfect. That instantly localises the bug: the IV is only wired into block one.
  Reading *where* the corruption stopped was faster than re-reading my code.
- **Critique → change:** Added the `b64decode`, switched the IV to
  `bytes([0] * BLOCK_SIZE)`, and moved `pkcs7` above the loop so every block is
  full and the aligned case gets its own block. Still to do: the unpad, which
  goes in `cryptolib` next to `pkcs7` rather than inside `aes_cbc_decrypt`, so a
  failure in the chaining and a failure in the padding can't hide each other.
  `strip_pkcs7` is now written and does exactly that. I'd guessed the shape of
  it correctly before writing any code: read the last byte as a count, check the
  final *count* bytes all carry that value, then slice them off. It raises
  `ValueError` on anything `pkcs7` couldn't have produced, matching how
  `xor_bytes` already rejects unequal lengths, and Claude pointed out the one
  slice trap worth a test: a count of 0 would make `data[:-0]` return empty
  instead of everything. Challenge 10's `__main__` now strips explicitly and
  asserts, so a direct run prints the lyrics with no `\x04` tail.
- **Unpadding — the thing I had backwards:** I asked whether reading the last
  byte breaks when the plaintext is a multiple of the block size. It doesn't,
  and the reason is the rule I'd already implemented a week earlier without
  connecting it: because `pkcs7` *always* adds padding, an aligned input gets a
  full block of `\x10`, so the last byte is always a count. If padding were ever
  skipped, a message ending in the byte 6 would be indistinguishable from one
  carrying six pad bytes. Challenge 9 taught me the rule; Challenge 10 is where
  I understood what it was for.
- **Why the library CBC "didn't work":** I'd tried `AES.new(key, AES.MODE_CBC)`
  with no `iv=` to check my encryption. pycryptodome doesn't default the IV to
  zeros, it generates a *random* one. So the output had sixteen bytes of garbage
  followed by clean text — the exact signature I'd just learned to read. With
  `iv=bytes(16)` my ciphertext matches the library's byte for byte, both ways.
- **stdlib vs scratch:** One file again. The mode itself is the from-scratch part
  (pycryptodome's `MODE_CBC` is the stdlib version, used only as the test oracle);
  AES on a single block stays a library call, as in Challenge 7.
- **Tests:** `test_challenge10.py`, 15 cases. The backbone is a cross-check
  against pycryptodome's `MODE_CBC` on 200 random key/IV/length combinations in
  each direction. Claude's point: a self round-trip passes even when both halves
  share the same misunderstanding, so encrypt and decrypt have to be checked
  against something that isn't me. Plus the official vector, round trips over
  eight lengths, a test that repeated plaintext blocks stay distinct under CBC
  while ECB collapses them to one, and one pinning that a wrong IV corrupts only
  the first block.
- **Artifact:** —
- **Blog hook:** "The bug was never where I thought it was." I was sure the IV
  spec was ambiguous and spent my effort there; the IV *was* wrong, but the thing
  actually destroying the output was a missing `b64decode` one line above. Also
  the running gag of this project: three challenges, three different Python
  functions that hand you *text describing a number* when you wanted the number.
  Worth saying plainly: I did Challenge 9 a week ago and had forgotten the
  padding rule I'd just implemented. The gap between sessions is part of the
  story, and it's the argument for this journal existing at all.
- **Status:** solved, both halves of the padding done

### Challenge 11 — An ECB/CBC detection oracle · [link](https://cryptopals.com/sets/2/challenges/11)

- **Status:** solved (stdlib, 12 Oct 2026). Critique below still to act on.
- **Concept it teaches (and the thing I actually learnt today):** the difference
  between a **threat model** and an **attack**. The threat model is the seating
  plan: who holds the key, who picks the plaintext, who gets to see the
  ciphertext, and how many times you may ask. The attack is the mechanical trick
  you run *once you know which seat you are in*. I had been treating every
  challenge as the same seat.
- **Where I went wrong:** the statement says "write a function that encrypts data
  under an unknown key", and I read "data" as arbitrary data handed to me. So I
  asked Claude whether I could assume the plaintext was random, and concluded my
  Challenge 8 detector was useless because English structure wouldn't be there.
  Claude pointed out that the oracle takes *my* argument. I didn't work that out
  myself and wouldn't have from the text alone. I still think the text is unclear
  on this, but the deeper reason I missed it is that I don't know the security
  space well enough to be asking "what can the attacker do?" as a reflex.
- **Set 1 vs here:** every Set 1 challenge put me in the same chair. Someone hands
  you a ciphertext, you work on it, you are an eavesdropper. The whole set trained
  a habit I then applied blindly. Set 2 changes the seat and doesn't announce it.
- **Habit I'm adopting:** before writing any code for a challenge, answer four
  questions in `notes.md`. Who holds the key? Who chooses the plaintext? What do I
  get to see? How many times can I ask? If I can't answer all four from the text,
  that's the thing to resolve first, not the code.
- **Blog hook (the one worth writing):** threat model vs attack, for people who
  write software but don't do security. The same cipher is fine in one seat and
  broken in another, and nothing about the cipher changed. Concrete scenarios to
  build it around, all cases where you never see the key but you chose part of the
  plaintext: the encrypted session cookie that contains the username you picked;
  the job payload on a queue holding the email address you typed; the file you
  uploaded to a service that encrypts it server-side; the "notes" column encrypted
  in a database whose backup later leaks.
- **Artifact:** `interactive/threat-models.html` — "What can the attacker do?". Three
  parts: the two definitions side by side; an attack-model table you flip between
  three attackers (ciphertext only with one message, ciphertext only with many,
  chosen plaintext) showing who can see and choose the key, plaintext and ciphertext; and
  a live AES-128 panel with ECB and CBC block tiles. In the ciphertext-only models the
  input box is **locked** and pre-filled with prose, and ECB shows five distinct
  blocks, so there is nothing to detect. Switching to chosen plaintext
  **unlocks the box**, and that unlocking is the whole lesson. An "encrypt again"
  button shows ECB never changing while CBC does. Four real scenarios at the
  bottom, including one (a job on a queue) that deliberately *fails*, to make the
  point that a chosen-plaintext attack needs both halves: choosing the input and seeing the
  ciphertext. The random-prefix wrinkle from Challenge 11 is deliberately absent,
  since I haven't solved that yet.
- **Where the tutoring broke down (worth keeping — this is the limits-of-AI thread):**
  - *My gaps.* I read "encrypts data under an unknown key" as arbitrary data handed
    to me, because all of Set 1 worked that way. I don't know the security space
    well enough to have "what can the attacker actually do?" as a reflex, so I went
    looking for a cleverer detector instead of asking who supplies the input. I also
    dismissed my own Challenge 8 tool as useless when it was the right tool all along.
  - *My frustration.* Two separate things, and it's worth splitting them. One is that
    the challenge text is genuinely unclear about the attack model. The other is the
    worry underneath it: how many more of these will I misread, and does a hint that
    reframes an entire challenge mean I didn't solve it? I felt like I'd cheated.
  - *Where Claude failed me.* Three, in descending order of damage.
    1. It wrote `strip_pkcs7` with full padding validation as routine Challenge 10
       plumbing. Padding validation is its own challenge later in Set 2. The
       implementation, the edge cases and the tests are now done for me. Neither of us
       noticed until I read ahead. Still open: whether to roll it back to the minimum
       Challenge 10 needed.
    2. I asked a clarifying question about Challenge 11 and got the answer to the
       challenge rather than the smallest nudge that would unstick me. Claude's own
       words afterwards: it could have said "re-read the oracle's signature and tell me
       what you notice" and then stopped.
    3. It wrote a summary claiming I'd "inferred it correctly, then didn't believe
       myself." I hadn't inferred anything. It made a better story out of what
       happened, which is exactly the sentence to distrust from an AI tutor. I pushed
       back and it conceded immediately, which is the point: I only caught it because
       I happened to remember what I'd actually asked.
  - *And one from the same session that cuts the other way.* While building the
    artifact, Claude hand-rolled AES-128 in JavaScript. It passed the FIPS-197 vector
    and the SP 800-38A vector, and was still wrong: one entry of the S-box, index 1,
    because `pow[255 - log[1]]` reads off the end of a 255-long table instead of
    wrapping. Two official test vectors, both green, real bug. Only diffing all 256
    entries against a known table found it. That is the Challenge 9 lesson again,
    from the other side of the table, and a decent argument for never trusting
    generated crypto code that "passes the vector."
- **Resolutions we came to:**
  - Before any code on a challenge, answer the four questions in `notes.md`: who holds
    the key, who chooses the plaintext, what do I see, how many times can I ask.
  - Orientation questions ("what is this challenge really asking?") get a question
    back, not an answer. Claude only explains after I've tried and failed.
  - Helpers that look like plumbing get checked against the rest of the set first.
- **Was it productive?** I didn't solve Challenge 11 and I'm carrying a hint I didn't
  earn. But the thing I actually took away transfers past Cryptopals: work out the
  seating plan before reaching for a trick.

#### The solve (12 Oct 2026)

- **First approach:** I answered the four questions in my head rather than in
  `notes.md`, and honestly I already knew from the orientation session what the
  solution needed, so the solve itself was short. Feed the oracle
  `"repeat" * 200`, call it ECB if any 16-byte ciphertext block repeats. All five
  runs matched the mode the oracle printed.
- **Critique → change** (all from Claude):
  - *Not self-checking.* The true mode only exists as a `print` inside the
    oracle, so correctness is checked by eye. Return the mode from the oracle
    and assert over a thousand runs.
  - *`random` for keys.* Python's `random` is reproducible by design, and
    `random.seed(1)` at import means every run uses the same "random" keys.
    Keys and IVs should come from `secrets`, `os.urandom` or
    `Crypto.Random.get_random_bytes`. Seed inside tests only.
  - *Why does the input work?* Open questions from Claude: why "repeat" (6
    bytes) still produces identical 16-byte blocks, and what the shortest input
    is that always works with a 5–10 byte random prefix.
  - *Second use of the Challenge 8 detector.* The repeated-block check is
    `has_repeated_block` from Challenge 8 written again inline. Second use, so it
    moves to `cryptolib`. The detector I'd dismissed as useless during
    orientation was the whole detection step.
  - *Smaller:* pass the oracle into `detect_mode`, `random.choice` over
    indexing, no `notes.md` with the four questions yet.
- **What I changed:** I added the self-check (the oracle returns its mode, and
  `__main__` asserts over 1000 runs). Then I had Claude make the rest: the
  detector moved to `cryptolib.has_repeated_block` (Challenge 8 now imports it),
  `detect_mode` takes the oracle as an argument, and keys, IVs, prefix lengths and
  the mode choice all come from `secrets`. Taking the oracle as a
  `bytes -> bytes` function means the detector only ever sees ciphertext, which
  is the attack model written into the type signature. My first version handed
  the true mode back to the detector function, so the detector had the answer
  as an input. Added `test_challenge11.py`.
- **My answers to the open questions:** the shortest input is 43 bytes of one
  value. The prefix is 5 to 10 bytes, and I need two whole aligned blocks of my
  bytes, so I need to reach byte 48. Claude's correction to my reasoning: only the
  prefix matters, not the suffix, and the *shortest* prefix (5) is the worst case,
  since 48 - 5 = 43. "repeat" works for a more specific reason than "lots of
  repetition": a 6-byte pattern lines up with 16-byte blocks every 48 bytes (the
  least common multiple), so blocks three apart are identical. There's a test for
  the 43-byte bound now.
- **Still open:** why `random` is wrong for keys. I thought no random number
  generator is perfect anyway. Parked to go deeper later.
- **stdlib vs scratch:** stdlib only so far. Open question for a later session:
  whether a scratch version using my Challenge 10 CBC adds anything.

---

### Challenge 12 — Byte-at-a-time ECB decryption (Simple) · [link](https://cryptopals.com/sets/2/challenges/12)

- **Concept it teaches:** if I can put my own bytes in front of a secret before
  ECB encrypts it, I can line the secret up so that one unknown byte at a time
  sits at the end of a block, and then guess that byte by comparing blocks.
- **First approach:** written on 17 Oct after thinking about it for a while.
  Find the block size from where the ciphertext length jumps, check for ECB,
  then recover the secret one byte at a time with a dictionary of the 256
  possible last bytes.
- **Wrong turns / bugs:** the first attempt kept recovering the first byte and
  nothing after it. I worked out the fix myself: when building the dictionary,
  the filler has to be followed by the bytes I've already recovered, not only
  the filler. The second attempt recovered 16 bytes ("Rollin' in my 5.") and then
  output `\xff`. My fix: the loop asked for one byte more than there was (I
  removed a `+ 1`). Then it stopped at "I just", which I put down to padding. I
  switched to a `while` loop that stops once I have as many bytes as the secret.
  It works, and it prints the whole lyric, but I'm not happy with it: the attack
  reads `len(UNKNOWN_DECODED)`, the secret's length, which an attacker wouldn't
  have. I'm also unhappy with my filler-length formula,
  `((i + 1) // block_size + 1) * block_size - (i + 1) % block_size`.
- **Critique → change (Claude, 17 Oct, on the unfinished code):**
  - The ECB check on `stdlib.py:60` passes `b'a' * 32` (my own input) to
    `has_repeated_block`, not the ciphertext the oracle returns. It always prints
    True, even if the oracle used CBC. Right answer, wrong reason.
  - `PREFIX_STRING` / `PREFIX_DECODED` is the secret, and the oracle appends it
    *after* my input, so the name says the opposite of what the code does. And
    `prefix` in `get_unknown_string` means something else (my filler bytes).
  - `build_dict` and `get_byte` call the global `oracle` directly. Challenge 11's
    lesson (pass the oracle in as an argument, so the attack only gets what the
    attacker is allowed) hasn't carried over yet.
  - The script isn't self-checking: no assert that the recovered bytes equal the
    secret.
  - Leftover debug print (`stdlib.py:39-40`) and commented-out code (`:61-63`).
  - What I changed after that (my fixes): the ECB check now tests
    `oracle(b'a' * 32)`, the secret is renamed `UNKNOWN_STRING`, and the helpers
    take the oracle as an argument.
- **Second critique (Claude, 17 Oct, on the working version):**
  - The oracle argument defaults to the global `oracle`, and `get_unknown_string`
    doesn't take one at all, so the attack can still reach the real oracle and the
    secret. The `len(UNKNOWN_DECODED)` stop condition is the same mistake as my
    Challenge 11 detector: the attack holds part of the answer. I spotted that one
    myself.
  - Claude printed my filler lengths for the first bytes: 15 down to 1, then
    32 down to 17, then 48. The filler grows by a whole block every 16 bytes, and
    that growth is what makes the formula hard to read.
  - Without the `break`, the loop recovers 139 bytes, the last one `\x01`, and
    then raises `KeyError`. The secret is 138 bytes.
- **stdlib vs scratch:** —
- **Artifact:** —
- **Blog hook:** —
- **Clean-up (26 Oct, done by Claude):** I came back a week later, tired after
  a long day, and asked Claude to do the clean-up list and commit so I could
  move on to the next challenge. What changed:
  - The attack works out the secret's length itself. `find_sizes` adds bytes
    until the ciphertext grows. At that point my `n` bytes plus the secret fill
    whole blocks exactly, so the secret is `len(oracle(b'')) - n` bytes long.
    The same loop gives the block size, so the stop condition no longer reads
    `UNKNOWN_DECODED`.
  - The filler is `block_size - 1 - i % block_size` bytes: 15, 14, ..., 0, then
    15 again. It never grows past one block. My version added a block every 16
    bytes, and that growth was what made my formula hard to read. Filler plus
    known bytes plus the guess always fill whole blocks, so comparing
    `ct[:compare]` still works, with `compare` calculated once in the loop.
  - `get_unknown_string(oracle_)` takes the oracle and nothing else, with no
    defaults, and does the block-size and ECB checks itself.
  - The script asserts its answer. `test_challenge12.py` checks the official
    secret, random secrets of lengths around the block boundaries (0, 1, 15,
    16, 17, 31, 32, 33, 50), and `find_sizes` on its own.
  - Removed `blocks = 1` and the commented-out code.
- **Status:** solved and cleaned up. The two clean-up items with something to
  learn (the length from the size jump, and why the filler never needs more
  than 15 bytes) were Claude's code, so worth a look before Challenge 13.
