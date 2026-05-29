# Development Journal — Samsara: Journey to the Triple Gem
A chronological log of key developments, decisions and learnings throughout this project.

---

## 2026-05-29 — Shipped Samsara to Itch.io and Archived the Prompt Engineering Behind It

**Type:** Milestone

**What I built or did**

Shipped *Samsara: Journey to the Triple Gem* — a complete 2D Buddhist educational game built entirely with AI assistance — to [mungmanbaoisan.itch.io/samsara-triple-gem-game](https://mungmanbaoisan.itch.io/samsara-triple-gem-game). Then used the `prompt-archivist` skill to document the 7 key prompts behind the build, each with a verbatim quote, reasoning doc, version history, executable rubric, and test fixtures. All 7 pass a GitHub Actions CI workflow at 100%.

**How We Did It**

Started with a single concept prompt in November 2025 describing samsara as a world of suffering with the Triple Gem at the centre. Built the game iteratively over many sessions: six realms as concentric circles, three-currency progression (Merit, Karma, Wisdom), 14 NPCs with transformation arcs, a hell drain mechanic, the Mara→Buddha mandatory finale, five-precepts stories, and a five-system upgrade (save/load, audio, tutorial, glossary, journal). Fixed a multi-layer audio bug — silent exception handlers masked a numpy dependency masking a Python version mismatch. Shipped a Windows executable via PyInstaller to Itch.io. Then ran `prompt-archivist`: interviewed myself about each prompt's reasoning, got approval on each REASONING.md before writing anything to disk, generated rubrics with executable pass conditions, created deterministic fixtures, and wired everything into CI.

**What I learned**

`except Exception: pass` is the first place to look when something fails silently — it hid three separate audio bugs in sequence. And documenting *why* you wrote a prompt (not just what it says) is what turns AI-assisted work into real portfolio evidence.

**References / Conversations**

Built with Claude Code (claude-sonnet-4-6). Game: [mungmanbaoisan.itch.io/samsara-triple-gem-game](https://mungmanbaoisan.itch.io/samsara-triple-gem-game). Repo: [github.com/MungManBaoIsan/samsara-triple-gem-game](https://github.com/MungManBaoIsan/samsara-triple-gem-game).

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

## 2026-05-29 — Building a standalone Windows exe (v2.0)

**TL;DR:** Fixed two PyInstaller path bugs, rebuilt using the right Python version, and shipped two download options — a ready-to-play exe and a source code zip.

**Type:** Bug Fix / Build / Release

**What I built or did**

Packaged the full feature version of Samsara into a double-click Windows exe. The previous v1.0 build was an older, stripped-down version — this one includes save/load, the meditation mini-game, visual effects, and the glossary.

Decided to offer two downloads on itch.io: the compiled exe for regular players, and the raw source code zip for developers or anyone who wants to read and run the Python files directly.

**Why I did it this way**

The source code version required players to install Python and run from the command line — a real barrier for most people. Packaging it with PyInstaller (a tool that bundles Python and all dependencies into a single folder) means anyone can unzip and play.

Keeping the source code version available alongside it means the project stays open for anyone learning Python or Pygame who wants to see how it's built.

**How We Did It**

1. Compared two existing folders — found the v1.0 exe was outdated and the source code folder had a full feature set it didn't include
2. Fixed `config.py` — it was loading `content/encounters.json` with a hardcoded relative path that breaks inside a compiled exe; added a `resource_path()` helper that points to the right place whether running as a script or bundled exe
3. Fixed `save_system.py` — saves were pointing to `__file__`, which inside a compiled exe points to a temp folder that gets deleted on close; redirected saves to sit next to the exe instead
4. Ran PyInstaller — first build used Python 3.14 by default; pygame isn't installed there and the game crashed immediately with "No module named 'pygame'"
5. Rebuilt explicitly with Python 3.12 (where pygame 2.6.1 lives) — clean build, game launched and played correctly
6. Zipped the source code separately (excluding build folders) for developers
7. Uploaded both to itch.io and GitHub Releases

**What I learned**

PyInstaller uses whatever Python version is set as the system default — if that's not the one your game actually runs on, it silently builds an exe that crashes. Always check which Python you're calling before you build.

The two path fixes are easy to miss but critical: data files need `sys._MEIPASS` to find them inside the bundle, and save files need `sys.executable` so they don't vanish when the temp folder clears.

**References / Conversations**

Built with Claude Code — one session covering version comparison, path bug fixes, PyInstaller rebuild, and itch.io upload.

---
