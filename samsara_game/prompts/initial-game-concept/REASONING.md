# Reasoning: Initial Game Concept

This document captures the thinking behind the prompt. It exists so a reader can understand not just *what* the prompt is, but *why* it ended up this way.

## Goal

Design a complete 2D educational game set in the Buddhist concept of samsara — a world of suffering — where the player navigates six realms of existence and must reach the Triple Gem (Buddha, Dhamma, Sangha) at the centre. The game needed to teach Buddhist concepts authentically to children, teenagers, and adults, showing how mental states like anger, craving, and ignorance cause suffering, and how wisdom, merit, and karma lead to liberation.

## Iteration history

This was the first time I put the idea into words for AI — a completely fresh concept with no prior drafts. The idea didn't arrive fully formed; Claude's clarifying questions (about visual style, multiplayer vs single-player, combat vs narrative, the cosmological ordering of realms) pulled out the details. One important correction happened early: I caught that Claude had placed Hell as a middle ring rather than the outermost, which contradicted Buddhist cosmology — I corrected it and Claude updated the design. That back-and-forth shaped the Game Design Document that became the foundation for everything built afterwards.

The second prompt (the clarification) locked in the most important design constraints: educational purpose over entertainment, single-player, hybrid action/narrative gameplay, wisdom-based progression (not gatekeeping), and depiction of suffering without glorification.

## Failure modes the final version handles

The initial prompt was intentionally open-ended because I didn't know exactly what game mechanics would work — I had a clear *theme* but not a clear *system*. By letting Claude ask questions and then answering in detail, the prompt evolved into a collaborative spec. The main risk in early prompts like this is getting generic output; the specificity of Buddhist cosmology (six realms, Three Poisons, Triple Gem as refuge) grounded Claude's output in authentic teaching rather than generic "good vs evil" game tropes.

The clarification prompt also established tone guard-rails: the game should make players feel "comfortable and supported" rather than punished, and must not "trivialize real struggles." This framing guided all subsequent NPC dialogue and scenario design.

## Outcome

Produced a complete Game Design Document and Phase 1 Python/Pygame codebase: six realms as concentric circles, three-currency progression (Merit, Karma, Wisdom), fog-of-ignorance visual system, hybrid exploration/dialogue gameplay, and a past-life selection mechanic that determines spawn realm. Shipped as a playable game on itch.io at mungmanbaoisan.itch.io/samsara-triple-gem-game.

## What I'd change next

The first prompt could have included a target age range and the distinction between depicting suffering vs glorifying it — those constraints had to be added explicitly in the second prompt. Including them upfront would have saved one round of clarification. A stronger v1 would read: *"Educational game for ages 10+, depicting Buddhist samsara as a world of suffering. The goal is not to shock but to teach..."*

## Tags

`game-design` `agent-workflow` `educational-content` `buddhist-concepts` `iterative-design`
