# Prompt Library — Samsara: Journey to the Triple Gem

[![Prompt Eval](https://github.com/MungManBaoIsan/samsara-triple-gem-game/actions/workflows/prompt-eval.yml/badge.svg)](https://github.com/MungManBaoIsan/samsara-triple-gem-game/actions/workflows/prompt-eval.yml)

This folder documents the prompts used to build *Samsara: Journey to the Triple Gem* — a 2D Buddhist educational game built entirely through AI-assisted development using Claude. It exists as portfolio evidence of prompt engineering, iterative design, and collaborative problem-solving — not as runtime configuration.

Each prompt directory contains the original prompt (quoted verbatim), the reasoning behind the design decisions, an executable evaluation rubric, and version history where prompts were refined over multiple rounds. Every rubric runs on every push via GitHub Actions.

## Index

| Prompt | Category | What it does | Iterated? |
|---|---|---|---|
| [`initial-game-concept`](./initial-game-concept/) | game-design | Describes the complete samsara world and three-currency progression system | Yes — v1 concept + v2 clarification |
| [`npc-system-design`](./npc-system-design/) | game-systems | Adds visible, wisdom-gated NPCs with transformation arcs | Yes — grew from 3 to 14 NPCs across sessions |
| [`realm-hell-mechanics`](./realm-hell-mechanics/) | game-systems | Makes Hell genuinely dangerous with drain, void damage, and progressive barriers | No — single precise prompt |
| [`mara-buddha-finale`](./mara-buddha-finale/) | narrative-design | Creates the mandatory Mara→Buddha finale sequence mirroring the Buddha's enlightenment story | Yes — 3 versions (add, enforce, polish) |
| [`five-precepts-stories`](./five-precepts-stories/) | content-design | Adds five NPCs teaching Buddhist ethics through age-appropriate emotionally immersive stories | No — single prompt |
| [`five-systems-upgrade`](./five-systems-upgrade/) | game-systems | Delivers Save/Load, Audio, Tutorial, Glossary, and Journal in one cohesive build | No — single prompt, one large delivery |
| [`audio-debug-iteration`](./audio-debug-iteration/) | debugging | Diagnoses and fixes a completely silent audio system through three debugging rounds | Yes — 3 rounds (pre-init, numpy, Python version) |

## Featured iterations

Prompts where the v1 → final journey shows the most learning:

### [`mara-buddha-finale`](./mara-buddha-finale/)

The finale went through three distinct prompts over the same session. v1 added the NPCs but left a gap: high-stat players could bypass Mara entirely. v2 enforced the sequence in code — Buddha's interaction handler checks Mara's state before allowing conversation. v3 raised the reflection timers (15s for Mara, 20s for Buddha) and added the victory message "leaving the cruel world of suffering behind." The iteration shows how a clear narrative intention (shadow before light, trial before teaching) gradually became a technical enforcement. See [`versions/`](./mara-buddha-finale/versions/).

### [`audio-debug-iteration`](./audio-debug-iteration/)

Three rounds of debugging that each addressed a real problem — but none of which was the root cause until round 3. The journey: wrong `pre_init` timing → hidden numpy dependency → wrong Python version (3.14 has no pygame wheel). The key lesson: `except Exception: pass` was masking every failure throughout. The fix involved removing numpy entirely, rewriting audio in pure Python, and adding explicit terminal diagnostics. This iteration demonstrates systematic debugging under uncertainty. See [`versions/`](./audio-debug-iteration/versions/).

### [`initial-game-concept`](./initial-game-concept/)

The v1 concept prompt described a world full of suffering with the Triple Gem as the goal — powerful theme, but no age range, no educational framing, and a "multiplayer race" mechanic that conflicted with Buddhist teaching. v2 locked in the key constraints that shaped everything afterwards: educational purpose over entertainment, wisdom-based progression (not achievement-based), and the depiction-vs-glorification distinction that guided every NPC story written after it. See [`versions/`](./initial-game-concept/versions/).

## Skills demonstrated

- [x] **Prompt design** — every prompt has a documented goal and structure
- [x] **Iteration** — see `versions/` subdirectories for prompts that were refined
- [x] **Evaluation** — every prompt has a rubric with executable pass conditions
- [x] **Automated testing** — rubrics run on every push via [`prompt-eval.yml`](../.github/workflows/prompt-eval.yml)
- [x] **Regression prevention** — `--fail-under 0.8` blocks merges that drop score below threshold
- [x] **Documentation** — every prompt has a REASONING.md explaining the *why*
- [x] **Domain knowledge** — Buddhist cosmology, ethics, and practice woven authentically into design decisions
- [x] **Debugging** — systematic diagnosis of layered technical failures

## How to read this folder

- **90 seconds:** Read this index and skim one featured iteration.
- **5 minutes:** Read two REASONING.md files — `mara-buddha-finale` and `audio-debug-iteration` are the most instructive.
- **Longer:** Read the [CHANGELOG](./CHANGELOG.md) for the full chronological story, then run the eval runner.

## Running the evaluations locally

```bash
pip install pyyaml
python scripts/eval_runner.py --provider mock
```

This validates every prompt against its rubric using deterministic fixtures (no API costs). See [`results-summary.md`](./results-summary.md) for the latest run.

To run against the real API:

```bash
pip install anthropic
export ANTHROPIC_API_KEY=your_key_here
python scripts/eval_runner.py --provider anthropic
```

## Changelog

See [`CHANGELOG.md`](./CHANGELOG.md) for a chronological view of prompt evolution.
