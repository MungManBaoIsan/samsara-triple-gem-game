# Audio Debug Iteration

> **Category:** debugging
> **Model used:** claude-sonnet-4-6
> **Project area:** Audio system and Python environment
> **Status:** production
> **Last updated:** 2025-05-25

## What this prompt does

Diagnoses and fixes a completely silent audio system through three debugging rounds, ultimately removing a hidden numpy dependency and rewriting audio generation in pure Python.

## The prompts (three rounds)

### Round 1 — Initial report

```
Change 1. and 2. are good but for 3. I still can't hear any sound.
How can I activate sound in game?
```

### Round 2 — Diagnostic output (after test_audio.py ran)

```
[FAIL] pygame is not installed.
Fix: pip install pygame

python: can't open file 'test_audio.py': [Errno 2] No such file or directory
```

### Round 3 — Root cause revealed (Python version mismatch)

```
C:\Users\joshk>py -3.12 test_audio.py
[FAIL] pygame is not installed.
```

*(followed by sharing pip output showing Python 3.14 was the active interpreter — pygame has no 3.14 wheel yet)*

## Inputs

Error messages and terminal output shared verbatim as the debugging context.

## Expected output

A diagnosis identifying all three root causes (pre_init timing, numpy dependency, Python version mismatch), a rewritten `audio.py` using only `math` and `array` from the Python standard library, a standalone `test_audio.py` diagnostic script, clear terminal feedback on startup (`[Audio] Mixer ready: ...`), and instructions for switching to Python 3.12 which has a stable pygame wheel.

## Related files

- Reasoning: [`REASONING.md`](./REASONING.md)
- Evaluation rubric: [`rubric.yaml`](./rubric.yaml)
- Version history: [`versions/`](./versions/)
