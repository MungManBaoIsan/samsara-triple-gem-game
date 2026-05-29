# Development Journal — Samsara: Journey to the Triple Gem
A chronological log of key developments, decisions and learnings throughout this project.

---

## 2026-05-29 — Added browser play via Pygbag; performance and visual overhaul

**Type:** Feature / Milestone

**What I built or did**
Made the game playable directly in the browser on itch.io — no download needed. Also fixed lag, font bugs, and restored all visual effects without sacrificing performance.

**Why I did it this way**
Pygbag (a tool that converts Pygame games to WebAssembly so they run in the browser) was the right choice because it requires minimal code changes. The main challenge wasn't getting it running — it was fixing everything that broke along the way: audio blocking the loader, the browser refusing to load Python from a CDN due to security headers, and per-frame surface creation causing the game to lag badly.

**How We Did It**
1. Installed Pygbag and made the game loop `async` (required for browser execution)
2. Made saves and audio silently do nothing on web — file I/O and audio don't work in the browser
3. Discovered the MEDIA USER ACTION REQUIRED loop was blocking Python from loading — fixed by calling `pygame.mixer.quit()` immediately after `pygame.init()` on web
4. Discovered SharedArrayBuffer (a browser security setting) was blocking the Pygbag CDN — fixed by turning it off, since audio was already disabled
5. Scaled the output to 960×540 for consistent screen fit, rendering internally at 1280×720 so no layout code needed changing
6. Fixed the `i`→`I` font bug by switching from `pygame.font.Font(None)` to `pygame.font.SysFont('freesansbold')` across all screens
7. Fixed NPC dialogue heading overlap caused by `get_display_name()` returning a `\n` string that split into two lines in the browser
8. Eliminated lag by removing per-frame SRCALPHA surface creation (288 chain-link circles, fog particles, NPC auras)
9. Restored all visuals using caching: fog rebuilt every 8 frames, NPC aura surfaces pre-allocated once and reused

**What this means for the app**
Anyone can now play Samsara in their browser at https://mungmanbaoisan.itch.io/samsara-triple-gem-game — no Python, no zip file, no setup.

**What I learned**
Browser environments are strict about audio, file I/O, and cross-origin security in ways desktop apps never are. The real skill was diagnosing each blocker from console error messages and fixing them one at a time. Caching expensive surfaces instead of recreating them every frame is the single biggest performance win in Pygame web builds.

**References / Conversations**
Built with Claude Code — full session covered Pygbag setup, browser debugging, and performance optimisation.

---
