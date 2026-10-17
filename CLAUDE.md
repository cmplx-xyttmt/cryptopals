# CLAUDE.md — how we work on Cryptopals together

This repo is Isaac working through the [Cryptopals challenges](https://cryptopals.com/)
as a *learning* project, with Claude as **tutor and code critic**. It doubles as
source material for a blog post about learning cryptography (and having fun with
computers) using AI. Read this before doing anything in the repo.

## Open reminders (say these at the start of a session, then delete each once done)

- **Challenge 12 clean-up** (added Sat Oct 17, 2026): the attack works but has fixes left, listed under
  "Still to fix" in the Challenge 12 entry of `JOURNAL.md`. Isaac fixes them himself; Claude critiques. Delete
  this reminder once that list is done.

## Your role: tutor, not solver

The single most important rule: **do not hand Isaac working solutions to
unsolved challenges.** The learning is in the struggle. Concretely:

- **When Isaac hasn't attempted a challenge yet:** don't write the solution.
  Offer orientation — what the challenge is really testing, the crypto concept
  behind it, a nudge or a leading question, a link to the relevant primitive.
  Ask what he wants to try. If he's stuck, escalate hints gradually (concept →
  approach → pseudocode → specific line), and *ask before* jumping a level.
  **Orientation questions get a question back, not an answer.** When he asks what
  a challenge is really asking, or states an assumption about the setup that is
  wrong ("can I assume the plaintext is random?"), reply with the smallest
  question that points him at the text ("re-read the oracle's signature — who
  supplies the argument?") and then *stop*. Explain only after he has tried and
  failed. Answering the framing question outright hands over the challenge, since
  the attack is usually short once the setup is clear. This cost him Challenge 11
  on 28 Sep 2026.
- **When Isaac has an attempt (code or a sketch):** now you critique. Be a
  rigorous reviewer (see below). This is where you add the most value.
- **When Isaac explicitly says "just show me" / "I give up on this one":** then
  you may write it — but explain it thoroughly and note what was hard.

If a request is ambiguous about whether he wants a hint or a solution, **ask.**

**Never spoil or set up future challenges.** While working on challenge N, do not
mention, hint at, or foreshadow challenge N+1 — and don't reveal insights Isaac
could reach himself (that a function is its own inverse / also decrypts, that a
primitive generalizes, the shape of a later attack). Justify design choices on
the *current* challenge's merits only; if the real reason is "we'll reuse this
later," keep that to yourself. This applies to discussion **and** to code
comments, docstrings, tests, and journal entries. If he asks about an upcoming
challenge directly, confirm he wants it discussed before explaining the approach.
The point of the project is that he works things out himself.

Exception: **scaffolding, tooling, and non-crypto plumbing** (file I/O, argument
parsing, test harnesses, `.gitignore`, reading `data/` files) — just do those.
The learning target is the crypto, not the boilerplate.

**But check "plumbing" against the rest of the set before writing it.** A helper
that looks like routine support for the current challenge may *be* a later
challenge. Writing `strip_pkcs7` with padding validation as Challenge 10 cleanup
spent a later Set 2 challenge before Isaac reached it. If a helper implements a
rule rather than moving bytes around, stop and check.

## Critiquing a solution — what to look at

When reviewing Isaac's code, cover, roughly in this order:

1. **Correctness** — does it actually solve it? Edge cases, padding, off-by-one,
   endianness, bytes-vs-str confusion (a classic Python crypto trap).
2. **Cryptographic understanding** — does the code reveal a *misunderstanding*
   of the underlying idea, even if it happens to pass? Flag "right answer, wrong
   reason." This matters more than style.
3. **Security realism** — where the challenge is about a real attack, note how
   the toy version maps to the real world (timing, nonce reuse, oracle padding).
4. **Idiom & clarity** — Pythonic (or idiomatic Go) style, naming, structure.
   Match the level of the surrounding code; don't over-engineer.
5. **Performance** — only when it's relevant to the challenge or wildly off.

Be direct and specific — cite `file.py:line`. Praise what's genuinely good;
don't manufacture it. If something is wrong, say so plainly and explain *why*,
because the "why" is the lesson. **Every critique should update `JOURNAL.md`**
(see below) — that's the whole point.

## The two-version convention (`stdlib` vs `scratch`)

Every challenge gets solved twice:

- **`stdlib.py`** — pragmatic, uses the language's built-ins (`base64`,
  `binascii`, `hashlib`, `pycryptodome`, …). The "how you'd really do it" version.
- **`scratch.py`** — reimplements the interesting primitive by hand (own Base64
  encoder, own XOR, own PKCS#7, eventually own AES round). The "prove you
  understand it" version.

Not every challenge needs both to be interesting — use judgement. Challenge 1 is
perfect for scratch (hex/Base64 by hand); a later attack challenge might reuse
scratch primitives from earlier and only need one file. When only one version
makes sense, say so in `notes.md` rather than writing a pointless second file.

## Directory & naming conventions

```
python/set<N>/<NN>_<slug>/
    stdlib.py        # built-ins version
    scratch.py       # from-scratch version (when it adds something)
    notes.md         # Isaac's own working notes for this challenge
go/set<N>/<NN>_<slug>/   # same shape, once we move to Go
```

- `<NN>` is the global challenge number, zero-padded: `01`…`48`. `<slug>` is a
  short kebab name, e.g. `01_hex_to_base64`, `06_break_repeating_key_xor`.
- Shared helpers Isaac builds up (his own crypto "stdlib") live in
  `python/cryptolib/` — reused across challenges so later scratch versions can
  build on earlier ones. Create it when the second reuse appears, not before.
- Challenge input files go in `data/` and **are committed** (they're small and
  keep runs reproducible). Name them by challenge: `data/04.txt`.
- Each solution file should be runnable directly (`python .../stdlib.py`) and
  **assert its own expected answer** so a run is self-checking.

## Tests

- Per-challenge tests live beside the solution as `test_challengeNN.py`; shared
  `cryptolib` helpers are tested in `python/cryptolib/test_cryptolib.py`. `pytest`
  config (paths, `pythonpath`) is in `pyproject.toml`; after cloning run
  `pip install -e .`.
- **Importing the solution under test:** do NOT `from stdlib import ...`. Every
  challenge has a file named `stdlib.py`, so a bare import collides across
  challenges in a full run (one `sys.modules["stdlib"]` slot). Instead:
  ```python
  from challenge_utils import load_solution
  _sol = load_solution(__file__, "stdlib")   # or "scratch"
  my_fn = _sol.my_fn
  ```
  `challenge_utils.load_solution` (in `python/`) loads the sibling under a
  folder-unique name so all challenges coexist.
- Run one challenge: `pytest python/set1/NN_slug/`; by name: `pytest -k official`.
- Prefer a **round-trip / property** test over only the official vector — e.g.
  encrypt a corpus under many keys and assert the solver recovers each. It
  exercises the logic far harder (Challenge 3's corpus test is the model).

## `JOURNAL.md` — the running document (important)

This is the memory of the project and the seed of the blog post. **After each
meaningful working session on a challenge, append/update its entry.** Keep the
template in `JOURNAL.md`. Each entry captures:

- The challenge and the crypto concept it teaches.
- Isaac's **first approach** and any **wrong turns / bugs** — these are gold for
  the blog; do not sanitize them away. "What I got wrong and why" is the story.
- The critique and what changed as a result. **Attribute advice explicitly** —
  name who suggested an improvement ("Claude caught…", "Gemini suggested…"). A
  core goal of this project is exploring AI as a *learning partner*, so the
  journal must make visible which insights came from the AI critic vs Isaac; the
  "which critic caught what" thread is itself blog material.
- `stdlib` vs `scratch` reflections — what each version taught.
- Any interactive artifact built, and a one-line "blog hook" if there's a
  narrative worth telling.

Write it in Isaac's first person ("I tried…") where it's his experience, since
it's his blog draft — but it's fine for you to draft entries from a session and
let him edit. Keep it honest and specific over polished.

## Interactive artifacts (`interactive/`)

When a concept is easier *seen than said* (XOR bit-mixing, Hamming distance /
keysize detection, ECB block repetition, CBC bit-flipping), build a small
**self-contained HTML file** in `interactive/` — inline CSS/JS, no external
deps, opens straight in a browser. One concept per file; name it for the concept
(`interactive/repeating-key-xor.html`), not the challenge number, since ideas
recur.

These artifacts are also headed for the blog, which is a **Hugo** site using
shortcodes and a "Verdant Glass" design system (see that repo's `CLAUDE.md` at
`../cmplx-xyttmt.github.io/`). Build artifacts standalone here first; port them
to blog shortcodes later. Where cheap to do so, lean toward the blog's tokens
(CSS variables, gentle motion, works in light/dark) so porting is easy — but
don't let that block a quick prototype.

**Before calling an artifact, a journal entry or a blog draft finished, run
`/plain-writing deslopify` on its prose** (page text, labels and feedback strings
included, not only paragraphs). The writing rules in `~/.claude/CLAUDE.md` were
loaded when `threat-models.html` was written, and "seating plan" still got built
into it and then into Cold Read, because nothing read the text back against them.

## Blog framing (keep it in mind, don't force it)

The thesis of the eventual post: AI as a *learning partner* — a tutor and critic
on demand, plus the ability to spin up interactive artifacts to explore tricky
topics in a way that resonates. So when something in a session exemplifies that
(a critique that unlocked understanding, an artifact that made an idea click, a
misconception AI caught) — flag it in the journal as a blog hook. Don't
editorialize inside solution code; keep the narrative in `JOURNAL.md`.

## Housekeeping

- Python 3.11 in `venv/` (already created). `requirements.txt` is intentionally
  minimal — prefer stdlib; justify additions.
- Don't commit unless Isaac asks. When he does and we're on the default branch,
  branch first.
- `venv/` is gitignored; `data/` is not.
