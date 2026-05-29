# Mara & Buddha Finale

> **Category:** narrative-design
> **Model used:** claude-sonnet-4-6
> **Project area:** End-game sequence and victory condition
> **Status:** production
> **Last updated:** 2025-11-29

## What this prompt does

Creates the mandatory two-part finale: defeating Mara (the demon of illusion) unlocks access to the Buddha, who delivers the core teachings and triggers the win condition.

## The prompt — v1 (add the NPCs)

```
Right before you are able to enter the Triple Gem, add NPC Evil Mara who
tries to stop you. If player overcomes this final challenge, add Buddha NPC
which player finally interacts with. Buddha NPC lights the path to nibbana
giving insight into the four noble truths & eightfold path, urging you to
do samadhi & vipassana meditation. Once interaction with Buddha is complete,
you win the game! Make Buddha & Evil Mara NPC look distinct & special.
```

## The prompt — v2 (enforce the sequence)

```
Make it a requirement to interact with both Evil Mara NPC & The Buddha NPC
before being allowed to win the game.
```

## The prompt — v3 (timing, visibility, victory message)

```
Make evil Mara NPC & Buddha NPC clearly visible. Increase Mara interactions
to 15 seconds each. Increase Buddha interactions to 20 seconds each. Make
the Triple Gem at centre of the world clearly visible like a sacred temple.
When player completes interaction with Buddha, win game is unlocked & player
is welcomed into the Triple Gem, leaving the cruel world of suffering behind
to realize the right path to nibbana awaits.
```

## Inputs

No variables — this is a complete narrative and mechanic specification.

## Expected output

Two special NPCs with dramatically enlarged visual representations (Mara: pulsing red diamond; Buddha: golden octagon with dharma wheel). A sequence enforcement system that blocks access to Buddha until Mara's dialogue state is "enlightened". Reflection timers of 15 seconds (Mara) and 20 seconds (Buddha). Victory message: "Welcome to the Triple Gem. You have left the cruel world of suffering behind. The right path to Nibbana awaits."

## Related files

- Reasoning: [`REASONING.md`](./REASONING.md)
- Evaluation rubric: [`rubric.yaml`](./rubric.yaml)
- Version history: [`versions/`](./versions/)
