# Cryptopals

My solutions to the [Cryptopals crypto challenges](https://cryptopals.com/),
worked through as a learning project — first in **Python**, later in **Go**.

This is also a writing project: I'm using it to explore *how AI changes the way
I learn*. Claude acts as a tutor and code critic, and along the way we build
small interactive HTML artifacts to make the trickier ideas click. The
[`JOURNAL.md`](JOURNAL.md) is the running log of that journey and the raw
material for a blog post (or series) on [my site](https://cmplx.xyz).

## Two solutions per challenge

For each challenge I write it twice:

- **`stdlib`** — the pragmatic version, leaning on the language's batteries
  (`base64`, `binascii`, `hashlib`, `Crypto`, …). *How you'd actually do it.*
- **`scratch`** — key primitives reimplemented by hand (my own Base64 encoder,
  my own XOR, eventually my own AES round). *How you understand it.*

## Layout

```
cryptopals/
├── CLAUDE.md          # how Claude tutors/critiques in this repo — read first
├── JOURNAL.md         # running log: attempts, critiques, what I got wrong
├── data/              # challenge input files (committed, for reproducibility)
├── interactive/       # self-contained HTML artifacts for tricky topics
├── python/
│   └── setN/
│       └── NN_slug/
│           ├── stdlib.py
│           ├── scratch.py
│           └── notes.md
└── go/                # same shape as python/, added when I start Go
```

## Running things

```sh
# Python (3.11, venv already present)
source venv/bin/activate
pip install -r requirements.txt
python python/set1/01_hex_to_base64/stdlib.py

# Tests (once we add them)
pytest

# Interactive artifacts — just open in a browser
open interactive/<name>.html
```
