# Realm Hell Mechanics

> **Category:** game-systems
> **Model used:** claude-sonnet-4-6
> **Project area:** World design and difficulty progression
> **Status:** production
> **Last updated:** 2025-11-29

## What this prompt does

Makes the Hell realm genuinely dangerous with stat drain, rapid void damage, and progressive realm barriers — turning passive world zones into active gameplay stakes.

## The prompt

```
Points slowly diminish while in the hell realm layer next to black area.
If player touches outer black area they burn in never ending torture &
points diminish rapidly making it impossible to get out. Point requirement
to enter each realm increases the nearer it is to the Triple Gem. Ash needs
to be in the Hell realm layer next to black area because he is the only way
player can get out of hell.
```

## Inputs

No variables — this is a self-contained mechanic specification.

## Expected output

Updated `player.py` and `main.py` with: slow stat drain (-0.1/sec) throughout Hell realm, rapid void drain (-2.0/sec) when touching the outer black boundary, progressive realm entry requirements that scale from simple (Hungry Ghost) to demanding (Temple), and Ash repositioned to the edge of Hell near the void boundary with zero stat requirements on his first dialogue.

## Related files

- Reasoning: [`REASONING.md`](./REASONING.md)
- Evaluation rubric: [`rubric.yaml`](./rubric.yaml)
