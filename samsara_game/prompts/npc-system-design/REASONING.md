# Reasoning: NPC System Design

This document captures the thinking behind the prompt. It exists so a reader can understand not just *what* the prompt is, but *why* it ended up this way.

## Goal

Add visible, interactive NPCs to the game world — characters the player can see on the map, walk up to, and talk with. Each NPC needed multiple dialogues that unlock progressively as the player gains wisdom, with responses that change based on the player's stats. The mix needed to include both NPCs who are suffering (and need help) and NPCs who are wise teachers. The aim was to make the world feel alive and to teach specific Buddhist concepts through individual character stories.

## Iteration history

The initial prompt was deliberately short — "Can we add NPCs to the game?" — because I didn't yet have a clear picture of the technical options. Claude responded with a detailed design question set covering visibility, persistence, characteristics, and teaching approach. By answering each option explicitly (A, D, C, both), I got a design that precisely matched my vision without having to invent the vocabulary for it myself.

The NPC system then grew organically through successive prompts:
- v1: 3 NPCs (Kara, Maya, Elder Song) covering Hell, Hungry Ghost, Human realms
- v2: Expanded to all 6 realms (added Dev, Rin, Marcus)
- v3: Added Mara and Buddha as special temple NPCs (see `mara-buddha-finale`)
- v4: Added 5 Five Precepts NPCs (see `five-precepts-stories`)
- Final: 14 NPCs total, 27 dialogues, 72+ player choices

A critical bug appeared in the first build: a lambda function couldn't handle method calls when the encounter system tried to treat NPC dialogue like a regular encounter object. This was fixed by replacing the lambda approach with a proper `NPCEncounter` class. A separate fix disabled the E key for generic encounters, limiting interaction to NPC proximity only.

## Failure modes the final version handles

- **Lambda crash:** The first NPC build crashed when `get_choice_count()` was called on a lambda-based encounter object. Fixed by proper class inheritance.
- **Generic encounter pollution:** Pressing E anywhere in the world triggered abstract encounters unrelated to nearby NPCs. Fixed by removing the fallback trigger and limiting E to proximity detection.
- **Stuck players:** Early builds had no guaranteed NPC near the player's spawn in Hell realm. Fixed by adding Ash with zero stat requirements.

## Outcome

14 NPCs across 6 realms plus Mara and Buddha at the temple — each with 3 progressive dialogues (27 total conversations, 72+ player choices). Characters transform visibly across conversations: Kara moves from rage to peace, Maya from craving to freedom. The NPC system became the primary vehicle for teaching Buddhist content in the game.

## What I'd change next

NPCs were placed using raw coordinate guesses (X: 2800, Y: 1600) without a visual map editor, requiring trial-and-error to position them correctly relative to realm boundaries. A future version would specify positions based on realm descriptions rather than raw numbers, or use a visual level editor. The initial prompt could also have specified "keep content editable in JSON without touching code" — that became clear only after the first delivery.

## Tags

`game-systems` `npc-design` `agent-workflow` `iterative-design` `bug-fix`
