# v3 — Pure Python Rewrite (2025-05-25)

Root cause identified: Python 3.14 was the active interpreter. pygame has no pre-built wheel for 3.14 yet. pip was silently failing to compile from source, so pygame was never actually installed.

**Fix:** Rewrote audio.py using only `math` and `array` from the standard library (no numpy). Added `test_audio.py` standalone diagnostic. Added `[Audio] Mixer ready:` print on startup. Switched to `py -3.12` for all game commands.

**Result:** Audio works. 19 sounds generated procedurally. No external dependencies beyond pygame.
