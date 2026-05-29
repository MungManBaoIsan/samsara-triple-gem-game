# Prompt Changelog

Chronological record of prompt creation and refinement. Newest entries at the top.

---

## audio-debug-iteration

### 2025-05-25 — v3 (pure Python rewrite)
**Change:** Rewrote audio.py using `math` and `array` from the standard library; removed numpy entirely; added `test_audio.py` standalone diagnostic; switched to Python 3.12.
**Reason:** Root cause identified: Python 3.14 has no pre-built pygame wheel, so pip was silently failing to install pygame at all.
**Impact:** Audio works correctly. 19 sounds generated procedurally, no external files, graceful degradation if mixer unavailable.

### 2025-05-25 — v2 (numpy removal attempt)
**Change:** Added numpy to requirements; exposed error messages by replacing silent exception handlers.
**Reason:** audio.py imported numpy which wasn't in requirements.txt; `except Exception: pass` swallowed the import failure silently.
**Impact:** Error messages visible but install still failing due to Python version — led to v3 diagnosis.

### 2025-05-25 — v1 (pre-init fix attempt)
**Change:** Moved `pygame.mixer.pre_init()` call to before `pygame.init()` in `Game.__init__()`.
**Reason:** Diagnosis showed pre_init was being called after pygame had already initialised the mixer with default settings.
**Impact:** Addressed a real problem but not the root cause. Audio still silent.

---

## five-systems-upgrade

### 2025-05-25 — v1
**Change:** Added Save/Load, Audio, Tutorial/Help, Glossary, and Journal/Achievements as five integrated modules.
**Reason:** Game needed persistent progress, immersive audio, onboarding for new players, Buddhist term definitions, and achievement tracking to be shareable and portfolio-quality.
**Impact:** Full feature set enabling itch.io publication. Game autosaves every 2 minutes, ambient audio per realm, 22 Pali terms in glossary, 13 achievements.

---

## five-precepts-stories

### 2025-11-30 — v1
**Change:** Added five new NPCs (Jamie, Riley, Sam, Alex, Taylor) each teaching one of the Five Buddhist Precepts through emotionally immersive stories.
**Reason:** Game needed to cover the Five Precepts as the core ethical foundation of Buddhist practice, in a way appropriate for both children and adults.
**Impact:** 5 new NPCs with 15 new dialogues and 45 new player choices. Game now covers Three Poisons + Five Precepts.

---

## mara-buddha-finale

### 2025-11-29 — v3 (timing and visibility)
**Change:** Enlarged Mara to 120px, Buddha to 140px; raised reflection timers to 15s/20s; personalised victory message.
**Reason:** Earlier NPC sizes were too easy to miss; short reflection times didn't allow reading full dharma teachings; victory message needed emotional resonance.
**Impact:** Both special NPCs unmissable. Players can read and absorb every teaching. Victory feels genuinely meaningful.

### 2025-11-29 — v2 (enforce sequence)
**Change:** Added state-check on Buddha interaction: checks Mara's dialogue state is "enlightened" before allowing conversation.
**Reason:** v1 allowed high-stat players to bypass Mara entirely and reach Buddha directly, removing the trial-before-teaching narrative.
**Impact:** Sequence is mandatory. Shadow (Mara) must be faced before light (Buddha) — the game now mirrors the Buddha's actual enlightenment story.

### 2025-11-29 — v1 (add NPCs)
**Change:** Added Mara and Buddha as special final NPCs at the temple.
**Reason:** Game needed a climactic finale that taught the core dharma (Four Noble Truths, Eightfold Path, meditation) and a win condition that required understanding rather than just stats.
**Impact:** Two visually distinct final characters. Win condition gated behind Buddha dialogue completion.

---

## realm-hell-mechanics

### 2025-11-29 — v1
**Change:** Added stat drain in Hell (0.1/sec), rapid void drain (2.0/sec), progressive realm requirements, and repositioned Ash to the void edge with zero requirements.
**Reason:** Hell realm felt too safe — no consequence for staying there. Players starting in Hell had no guaranteed path out.
**Impact:** Hell is genuinely dangerous. Urgency created from the first second. No player can get stuck without a path to Ash.

---

## npc-system-design

### 2025-11-29 — v1 (initial NPC system)
**Change:** Added visible on-map NPCs with proximity detection, multiple dialogue stages, stat-based unlocking, and both suffering/teacher types.
**Reason:** Game world felt empty and static — needed characters to carry Buddhist teachings through personal stories rather than abstract text.
**Impact:** 3 initial NPCs (Kara, Maya, Elder Song). NPC system became the primary teaching vehicle. Later expanded to 14 total.

---

## initial-game-concept

### 2025-11-28 — v2 (clarification)
**Change:** Added educational purpose, target audience (children/adults), depiction-vs-glorification distinction, emotional safety requirement, three-currency system confirmation.
**Reason:** v1 left gameplay mechanics, target audience, and educational stance undefined. Claude's clarifying questions revealed the gaps.
**Impact:** Complete game design foundation. All subsequent decisions (NPC tone, visual design, difficulty balance) flow from these constraints.

### 2025-11-28 — v1 (concept brief)
**Change:** Initial game pitch describing samsara world and Triple Gem goal.
**Reason:** First articulation of the game concept to an AI collaborator.
**Impact:** Established the core Buddhist theme and world structure. Prompted Claude to ask design questions that shaped the full GDD.
