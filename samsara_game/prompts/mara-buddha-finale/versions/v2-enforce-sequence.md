# v2 — Enforce the Sequence (2025-11-29)

Closed the gap from v1 by making the Mara → Buddha order a hard requirement in code.

```
Make it a requirement to interact with both Evil Mara NPC & The Buddha NPC
before being allowed to win the game.
```

**What changed:** Buddha's interaction handler now checks Mara's dialogue state before allowing conversation to begin. A "Defeat Mara First" indicator appears when approaching Buddha too early. No shortcuts possible regardless of stats.
