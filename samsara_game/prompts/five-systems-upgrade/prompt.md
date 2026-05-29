# Five Systems Upgrade

> **Category:** game-systems
> **Model used:** claude-sonnet-4-6
> **Project area:** Game infrastructure and player experience
> **Status:** production
> **Last updated:** 2025-05-25

## What this prompt does

Adds five major game systems in a single delivery: Save/Load, Sound & Music, Tutorial & Help, Buddhist Terms Glossary, and a Journal & Achievements tracker.

## The prompt

```
Comprehensive Improvement Suggestions — I've created a detailed document
with 20+ suggestions organized by priority.

TOP 5 RECOMMENDATIONS:
1. Save/Load System (9/10 impact) — Essential for serious gameplay. Players
   can continue their journey. Auto-save + manual save.
2. Sound & Music (10/10 impact) — Transforms immersion completely.
   Realm-specific ambient sounds. Buddhist meditation music. Sound effects
   for everything.
3. Tutorial/Help System (8/10 impact) — Optional tutorial for beginners.
   In-game help (H key). Contextual hints. Buddhist terms glossary.
4. Buddhist Terms Glossary (8/10 impact) — Educational mission. Define all
   Pali terms. Pronunciation guide. Real-world context.
5. Quest/Progress Journal (8/10 impact) — Track NPCs talked to. Show
   obstacles destroyed. Clear goals and requirements. Achievements system.

Could we go ahead and add these to the game then?
```

## Inputs

No variables — the five systems are fully described in the prompt.

## Expected output

Five new Python modules (`save_system.py`, `audio.py`, `glossary.py`, `progress.py`, `screens.py`) plus an updated `main.py` that integrates them. Save system: 3 slots with autosave every 2 minutes. Audio: procedurally generated (no external files), per-realm ambient drones, stat-gain chimes. Glossary: 22 Pali terms with pronunciation and in-game context. Journal: 13 achievements with notification system. All systems accessible via keyboard shortcuts (S, M, H, G, J, P).

## Related files

- Reasoning: [`REASONING.md`](./REASONING.md)
- Evaluation rubric: [`rubric.yaml`](./rubric.yaml)
