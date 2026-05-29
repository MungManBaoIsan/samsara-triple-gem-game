# Reasoning: Audio Debug Iteration

This document captures the thinking behind the prompt. It exists so a reader can understand not just *what* the prompt is, but *why* it ended up this way.

## Goal

Fix a game where sound and music produced no output at all, despite the code appearing correct. The debugging journey spanned multiple sessions and required diagnosing three separate layered problems before audio worked.

## Iteration history

This was a multi-step debugging process, not a single prompt. The conversation went through three distinct phases:

**Round 1 — Wrong pre_init timing:** Claude identified that `pygame.mixer.pre_init()` was being called inside `AudioManager.__init__()` — after `pygame.init()` had already run and set up the mixer with its own defaults. Moving `pre_init` to before `pygame.init()` was the proposed fix, but audio still didn't work. The fix addressed a real problem but wasn't the root cause.

**Round 2 — Hidden numpy dependency:** The audio implementation used numpy to generate sounds procedurally. Numpy was not listed in requirements.txt, so on machines without it installed the import failed silently — with no error message because a bare `except Exception: pass` was swallowing the failure entirely. The game ran fine, just without any sound and with no indication of why.

**Round 3 — Python version mismatch:** Python 3.14 (newly released at the time) had no pre-built pygame wheel. Running `pip install pygame` on Python 3.14 was failing to compile from source, meaning pygame wasn't installed at all in the active interpreter — which is why `test_audio.py` kept reporting `[FAIL] pygame is not installed` even after seemingly installing it.

The actual fix required three changes together: rewriting audio.py to use pure Python (`math` and `array` modules, no numpy), adding a standalone `test_audio.py` diagnostic script with clear pass/fail output, and switching the active interpreter to Python 3.12 which has a stable pygame wheel.

## Failure modes the final version handles

- **Silent error handling:** `except Exception: pass` blocks were hiding every failure. The rewritten audio system prints `[Audio] Mixer ready: (44100, -16, 2)` or `[Audio] Failed to start: <reason>` to the terminal on launch. The F1 key also prints a live diagnostic during gameplay.
- **Missing dependency:** No external files or non-standard libraries are required. Only pygame is needed, and the game degrades gracefully (silent but fully playable) if the mixer can't initialise.
- **Version confusion:** The standalone `test_audio.py` runs in isolation from the main game and immediately shows whether pygame is installed in *this* Python interpreter — making Python version issues obvious rather than hidden.

## Outcome

Audio works correctly on Python 3.12 with pygame installed. Per-realm ambient drones change as the player moves between realms. Stat-gain chimes (distinct sounds for Merit, Karma, Wisdom), obstacle effects, and a sacred bell for achievements all play as intended.

**The lesson from this experience:** When debugging with AI assistance, silent error handling (`except Exception: pass`) is almost always the first place to look when something fails with no visible message. It hides the real cause and makes every layer of diagnosis harder than it needs to be. The pattern to ask for immediately is: *"Can you add explicit diagnostic output before every exception handler so we can see what's actually failing?"*

## Tags

`debugging` `audio` `dependency-management` `python-environment` `iterative-fix`
