# Reasoning: Realm Hell Mechanics

This document captures the thinking behind the prompt. It exists so a reader can understand not just *what* the prompt is, but *why* it ended up this way.

## Goal

Make the Hell realm genuinely dangerous and consequential — not just a dark-coloured zone but a place that actively punishes the player for staying too long. The prompt introduced three mechanics working together: slow stat drain while anywhere in Hell, rapid stat drain when touching the outer void boundary, and Ash (an NPC positioned at the very edge near the void) as the only means of escape. The realm entry requirements were also made progressive so that each barrier is harder than the last as the player moves toward the Triple Gem.

## Iteration history

This was a single, precise prompt that arrived fully formed — a mix of Buddhist cosmological understanding (hell as a realm of ongoing suffering) and game design instinct (danger zones with a specific lifeline create tension and urgency). The imagination behind it came from thinking about what the hell realm should *feel* like rather than just look like. No major rework was needed after this prompt; the mechanics landed correctly on the first delivery.

The only refinement was Ash's positioning: he needed to be at coordinates near the void boundary (X: 3050, Y: 1600) — close enough to the danger that the player is forced toward the edge to find him, reinforcing the teaching that wisdom comes from confronting the deepest suffering, not avoiding it.

## Failure modes the final version handles

- **Stuck state:** Earlier versions had no consequence for staying in Hell. A player spawning there with negative starting karma could walk straight to the centre without urgency. The drain mechanic closes this gap.
- **No guaranteed escape:** Without Ash at the edge with zero requirements, a player who missed Kara (the other Hell NPC) had no way to gain stats. Ash's position and zero-requirement first dialogue guarantee a path out.
- **Uniform difficulty:** Realm requirements used to be flat — the same threshold for every realm. The progressive system (Hungry Ghost: 5/5/5 → Temple: 200/150/120) mirrors the Buddhist teaching that the path becomes more demanding as wisdom deepens.

## Outcome

Hell drains all stats at 0.1 points/second; touching the void drains at 2.0 points/second (20× faster). The six realm barriers scale from trivially easy (Hungry Ghost: Wisdom 5) to genuinely demanding (Temple: Wisdom 200/Merit 150/Karma 120). Players starting in Hell must find Ash quickly — typically within the first minute of play — or their stats will go negative, making the already-difficult escape even harder.

## What I'd change next

Drain rates were set by instinct rather than playtesting. 0.1 points/second means roughly 50 seconds before stats hit zero from a fresh start — this may be too tight for younger players or first-time players unfamiliar with the world layout. Future versions would expose these as named config values (`HELL_DRAIN_RATE`, `VOID_DRAIN_RATE`) with documented guidance on how to tune them for different difficulty preferences.

## Tags

`game-systems` `game-design` `buddhist-concepts` `difficulty-tuning` `player-experience`
