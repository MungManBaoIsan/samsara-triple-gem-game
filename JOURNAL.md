# Development Journal — Samsara: Journey to the Triple Gem
A chronological log of key developments, decisions and learnings throughout this project.

---

## 2026-05-29 — Getting Samsara into the browser: the full story

**TL;DR:**
- Ported the game to run in the browser using Pygbag (WebAssembly)
- Hit and fixed four separate blockers before it would even load
- Then found and removed 70+ per-frame surface allocations that were making it unplayable
- Final result: smooth browser play, larger text, working pause screen

**Type:** Feature / Milestone / Bug Fix

**What I built or did**

Made the game playable directly in the browser on Itch.io — no download, no Python install, no setup needed.

It sounds simple, but it took two full rounds of fixing. The first round was just getting the game to load at all. The second was making it actually smooth to play once it did.

**Why I did it this way**

Pygbag was the right tool — it converts Pygame games to WebAssembly (the technology that lets Python run inside a browser) with minimal code changes. The hard part wasn't the conversion itself. It was the chain of unexpected blockers that only appear in a browser environment: audio rules, security headers, memory limits, and rendering costs that desktop never exposes.

**How We Did It**

*Round 1 — Getting it to load:*

1. Made the game loop `async` and added `await asyncio.sleep(0)` each frame — required for Pygbag so the browser can breathe between updates
2. Made saves and audio silently do nothing on web — file I/O and audio don't work in the browser environment
3. Fixed the MEDIA USER ACTION REQUIRED loop that was blocking Python from loading — solved by calling `pygame.mixer.quit()` immediately after `pygame.init()` on web
4. Fixed a browser security setting (SharedArrayBuffer) that was blocking the Pygbag CDN — turned it off since audio was already disabled
5. Scaled output to 960×540 for consistent screen fit, rendering internally at 1280×720 so no layout code needed changing
6. Fixed the `i`→`I` font bug by switching from `pygame.font.Font(None)` to `pygame.font.SysFont('freesansbold')` across all screens
7. Fixed NPC dialogue heading overlap caused by `get_display_name()` returning a `\n` string that split across two lines in the browser

*Round 2 — Making it smooth:*

8. Identified 70+ transparent surfaces (SRCALPHA) being created every single frame across six files — invisible on desktop, crippling in WebAssembly
9. Pre-created Mara's aura (5 surfaces), Buddha's aura (7), warning overlay, and victory glow in `__init__`; cleared and redrew each frame instead of allocating new ones
10. Fixed 15 mini-Mara obstacles — each was creating 3 aura surfaces and a new font every frame; pre-created in `__init__` instead
11. Removed the transparent spoke surface in `world.py` entirely and drew the lines directly
12. Rebuilt the fog cache — base surface stored per clarity level; particle layer only rebuilt every 20 frames instead of every frame
13. Bumped font sizes (small: 16→22, medium: 24→30, large: 36→44) and resized the stats panel and dialogue box to fit
14. Fixed the pause state — pressing ESC had no handler or renderer, so it silently froze the game with no way out

**What this means for the app**

Anyone can play Samsara at https://mungmanbaoisan.itch.io/samsara-triple-gem-game — no Python, no zip file, no setup.

The text is now large enough to read comfortably, the fog and NPC auras all still appear, and pressing ESC actually pauses the game properly.

**What I learned**

Browser environments are strict about audio, file I/O, and cross-origin security in ways desktop never is. Each blocker had to be diagnosed from console error messages and fixed one at a time — there was no single solution.

The bigger lesson from Round 2: it wasn't one big problem. It was dozens of small allocations spread across six files, all adding up to 70+ new surfaces every frame. In WebAssembly, the rule is — never allocate inside the draw loop if you can help it.

**References / Conversations**

Built with Claude Code — two sessions covering Pygbag setup, browser debugging, performance diagnosis, surface caching, UI scaling, and bug fixing.

---
