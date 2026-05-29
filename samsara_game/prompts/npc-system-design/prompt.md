# NPC System Design

> **Category:** game-systems
> **Model used:** claude-sonnet-4-6
> **Project area:** NPC architecture and dialogue system
> **Status:** production
> **Last updated:** 2025-11-29

## What this prompt does

Adds a fully interactive NPC system to the game world — visible characters the player can see on the map, approach, and converse with across multiple wisdom-gated dialogue stages.

## The prompt

```
Can we add NPCs to the game? Player has to interact with them & make the
right choices.
```

## Clarification prompt (v1 design decisions)

```
Option A [visible on map]
Option D [different responses based on player wisdom/stats]
All of the above [NPC characteristics]
Option C [mix of suffering and teacher NPCs]

Before I Build:
1. Yes [like this design approach]
2. NPCs should be visible on the map
3. Multiple dialogues that unlock
4. Yes [different responses based on player wisdom]
5. Both [suffering NPCs who need help AND teacher NPCs who give wisdom]
```

## Inputs

No variables — design decisions were made interactively through a multi-choice Q&A before implementation.

## Expected output

A working NPC module (`npc.py`) with: visible on-map representation, proximity detection, multiple dialogue stages unlocked by wisdom/stat thresholds, state tracking (initial → helped_once → transformed → enlightened), both suffering and teacher character archetypes, and JSON-driven content so dialogue can be edited without touching code.

## Related files

- Reasoning: [`REASONING.md`](./REASONING.md)
- Evaluation rubric: [`rubric.yaml`](./rubric.yaml)
- Version history: [`versions/`](./versions/)
