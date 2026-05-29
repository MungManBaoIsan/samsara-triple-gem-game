"""
Samsara Audio Test
Run this script BEFORE launching the game to check if sound works on your machine.

    python test_audio.py

It will play a short bell tone and tell you exactly what's working or not.
"""

import sys

# ── 1. Check pygame ────────────────────────────────────────────────────
try:
    import pygame
    print(f"[OK]  pygame {pygame.version.ver} found")
except ImportError:
    print("[FAIL] pygame is not installed.")
    print("       Fix: pip install pygame")
    sys.exit(1)

# ── 2. Initialise mixer ───────────────────────────────────────────────
print("      Initialising mixer...")
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

init_info = pygame.mixer.get_init()
if not init_info:
    print("[FAIL] Mixer could not start.  Possible causes:")
    print("       - No audio output device connected (headphones / speakers)")
    print("       - On Linux: PulseAudio or ALSA not running")
    print("       - On macOS: System audio permissions blocked")
    print("       - On Windows: Default audio device disabled")
    print()
    print("       Try these fixes:")
    print("       Linux  : sudo apt install pulseaudio && pulseaudio --start")
    print("       macOS  : System Preferences > Sound > Output — pick a device")
    print("       Windows: Right-click speaker icon > Open Sound settings")
    pygame.quit()
    sys.exit(1)

print(f"[OK]  Mixer started: rate={init_info[0]}Hz  bits={abs(init_info[1])}  "
      f"{'stereo' if init_info[2]==2 else 'mono'}")

# ── 3. numpy check (optional) ─────────────────────────────────────────
try:
    import numpy as np
    print(f"[OK]  numpy {np.__version__} found (optional, not required)")
except ImportError:
    print("[OK]  numpy not installed (that's fine - game uses pure Python audio)")

# ── 4. Generate and play a test tone ─────────────────────────────────
import math, array

print("      Generating test tone...")
sample_rate = 44100
duration    = 0.8
frequency   = 523.25   # C5 — same as the Merit chime
n = int(sample_rate * duration)
fade = max(1, int(n * 0.15))
buf = array.array('h')

for i in range(n):
    t   = i / sample_rate
    val = math.sin(2 * math.pi * frequency * t)
    val += 0.3 * math.sin(2 * math.pi * frequency * 2 * t)   # harmonic
    val *= 0.5                                                  # scale
    if i < fade:
        val *= i / fade
    elif i > n - fade:
        val *= (n - i) / fade
    s = max(-32767, min(32767, int(val * 32767)))
    buf.append(s)
    buf.append(s)   # stereo

sound = pygame.mixer.Sound(buffer=buf.tobytes())
print(f"[OK]  Sound generated ({duration}s)")

print("      Playing bell tone... (you should hear a C note)")
channel = sound.play()

if channel is None:
    print("[FAIL] play() returned None — mixer has no free channels or device issue.")
    pygame.quit()
    sys.exit(1)

pygame.time.wait(int(duration * 1000) + 200)

if not channel.get_busy():
    print("[OK]  Sound played and finished cleanly")
else:
    print("[OK]  Sound is still playing (may be slightly long)")

# ── 5. Summary ────────────────────────────────────────────────────────
print()
print("=" * 55)
print("  AUDIO TEST PASSED — sound should work in the game!")
print("  Launch the game:  python main.py")
print("  In-game controls: P = mute/unmute")
print("=" * 55)

pygame.quit()
