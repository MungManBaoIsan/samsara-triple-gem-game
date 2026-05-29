"""
Audio System for Samsara
Generates sound effects and ambient tones using pure Python/pygame arrays.
No numpy required. Degrades gracefully if audio device is unavailable.
"""

import sys
import pygame
import math
import array

IS_WEB = sys.platform == 'emscripten'


class AudioManager:
    """Manages all game audio: sound effects and ambient drones."""

    def __init__(self, verbose=False):
        self.enabled = False
        self.muted = False
        self.sounds = {}
        self.current_ambient = None
        self.ambient_channel = None
        self.sample_rate = 44100
        self._verbose = verbose

        if IS_WEB:
            return

        # Mixer should already be pre_init'd by Game.__init__.
        # Try to ensure it is ready, then generate sounds.
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(self.sample_rate, -16, 2, 512)

            init_info = pygame.mixer.get_init()
            if not init_info:
                if verbose:
                    print("[Audio] Mixer could not initialise - no audio device found.")
                return

            if verbose:
                print(f"[Audio] Mixer ready: {init_info}")

            self._generate_all_sounds()
            pygame.mixer.set_num_channels(16)
            self.ambient_channel = pygame.mixer.Channel(0)
            self.enabled = True

            if verbose:
                print(f"[Audio] {len(self.sounds)} sounds generated. Audio ON.")

        except Exception as e:
            if verbose:
                print(f"[Audio] Failed to start: {e}")
            self.enabled = False

    # ------------------------------------------------------------------ #
    # Sound generation  (pure Python - no numpy needed)                   #
    # ------------------------------------------------------------------ #

    def _make_sound(self, samples_left, samples_right):
        """
        Build a pygame Sound from two lists of int16 samples (left, right).
        Uses Python's array module so numpy is not required.
        """
        buf = array.array('h')          # signed short = int16
        for l, r in zip(samples_left, samples_right):
            buf.append(max(-32767, min(32767, int(l))))
            buf.append(max(-32767, min(32767, int(r))))
        return pygame.sndarray.make_sound(
            pygame.sndarray.make_sound.__doc__ and  # False, just a guard
            None or
            pygame.mixer.Sound(buffer=buf.tobytes())
        )

    def _build_sound(self, samples_left, samples_right):
        """Build a pygame.mixer.Sound from two Python lists of int16 values."""
        buf = array.array('h')
        for l, r in zip(samples_left, samples_right):
            buf.append(max(-32767, min(32767, int(l))))
            buf.append(max(-32767, min(32767, int(r))))
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _tone(self, frequency, duration, volume=0.3, harmonics=None):
        """
        Generate a simple tone with optional harmonics and fade envelope.
        harmonics: list of (freq_multiplier, amplitude) e.g. [(2, 0.3)]
        """
        n = int(self.sample_rate * duration)
        samples = []
        fade_len = max(1, int(n * 0.15))

        for i in range(n):
            t = i / self.sample_rate
            val = math.sin(2 * math.pi * frequency * t)
            if harmonics:
                for mult, amp in harmonics:
                    val += amp * math.sin(2 * math.pi * frequency * mult * t)

            # Normalise roughly (harmonics can push beyond 1.0)
            scale = 1.0 / (1 + sum(a for _, a in harmonics)) if harmonics else 1.0
            val *= scale

            # Fade in / out
            if i < fade_len:
                val *= i / fade_len
            elif i > n - fade_len:
                val *= (n - i) / fade_len

            samples.append(int(val * volume * 32767))

        return self._build_sound(samples, samples)

    def _sweep(self, f_start, f_end, duration, volume=0.3):
        """Frequency sweep from f_start to f_end - good for destruction sounds."""
        n = int(self.sample_rate * duration)
        samples = []
        phase = 0.0
        fade_len = max(1, int(n * 0.2))

        for i in range(n):
            progress = i / n
            freq = f_start + (f_end - f_start) * progress
            phase += 2 * math.pi * freq / self.sample_rate
            val = math.sin(phase)

            if i < fade_len:
                val *= i / fade_len
            elif i > n - fade_len:
                val *= (n - i) / fade_len

            samples.append(int(val * volume * 32767))

        return self._build_sound(samples, samples)

    def _noise(self, duration, volume=0.2):
        """Short noise burst for hit sound."""
        import random
        n = int(self.sample_rate * duration)
        fade_len = max(1, int(n * 0.3))
        samples = []
        prev = 0.0
        for i in range(n):
            raw = random.uniform(-1, 1)
            # Simple low-pass smoothing
            val = prev * 0.6 + raw * 0.4
            prev = val
            env = 1.0
            if i > n - fade_len:
                env = (n - i) / fade_len
            samples.append(int(val * env * volume * 32767))
        return self._build_sound(samples, samples)

    def _generate_all_sounds(self):
        """Pre-generate all sound effects at startup."""
        # Stat gain chimes — pentatonic C-E-G
        self.sounds['merit']   = self._tone(523.25, 0.45, 0.28,
                                            [(2, 0.25), (3, 0.12)])    # C5
        self.sounds['karma']   = self._tone(659.25, 0.45, 0.28,
                                            [(2, 0.25), (3, 0.12)])    # E5
        self.sounds['wisdom']  = self._tone(783.99, 0.55, 0.28,
                                            [(2, 0.30), (3, 0.15)])    # G5

        # Negative consequence
        self.sounds['negative'] = self._tone(155.56, 0.50, 0.30,
                                             [(1.059, 0.5)])           # dissonant

        # Obstacle combat
        self.sounds['hit']     = self._noise(0.15, 0.25)
        self.sounds['destroy'] = self._sweep(700, 120, 0.55, 0.30)

        # UI
        self.sounds['select']       = self._tone(440,    0.08, 0.18)
        self.sounds['confirm']      = self._tone(880,    0.18, 0.22, [(1.5, 0.25)])
        self.sounds['dialogue_open']= self._tone(329.63, 0.22, 0.20, [(2, 0.2)])

        # Realm transition
        self.sounds['transition']   = self._sweep(200, 900, 0.55, 0.22)

        # Clarity shimmer
        self.sounds['clarity']      = self._tone(1046.5, 0.65, 0.20,
                                                 [(2, 0.35), (3, 0.18), (4, 0.10)])

        # Sacred bell — long decay
        self.sounds['bell']         = self._tone(261.63, 1.8, 0.28,
                                                 [(2.0, 0.35), (3.0, 0.18),
                                                  (4.2, 0.12), (5.4, 0.08)])

        # Ambient drones — 4-second looping tones per realm
        realms = {
            'hell':         (73.42,  [(1.059, 0.40), (2, 0.18)]),
            'hungry_ghost': (98.0,   [(1.5,   0.28), (2, 0.12)]),
            'animal':       (110.0,  [(2,     0.22), (3, 0.10)]),
            'human':        (130.81, [(2,     0.28), (3, 0.14)]),
            'asura':        (123.47, [(1.059, 0.28), (2, 0.18)]),
            'deva':         (196.0,  [(2,     0.38), (3, 0.20), (4, 0.10)]),
            'temple':       (261.63, [(2,     0.38), (3, 0.24), (5, 0.10)]),
        }
        for realm, (freq, harmonics) in realms.items():
            self.sounds[f'ambient_{realm}'] = self._tone(
                freq, 4.0, volume=0.12, harmonics=harmonics)

    # ------------------------------------------------------------------ #
    # Public playback API                                                  #
    # ------------------------------------------------------------------ #

    def play(self, sound_name):
        """Play a one-shot sound by name."""
        if not self.enabled or self.muted:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    def play_stat_sound(self, stat_type, amount):
        """Play the appropriate sound for a stat change."""
        if amount < 0:
            self.play('negative')
        elif stat_type in ('merit', 'karma', 'wisdom'):
            self.play(stat_type)
        else:
            self.play('confirm')

    def set_ambient(self, realm):
        """Switch the looping ambient drone to match the current realm."""
        if not self.enabled or self.muted:
            return
        if realm == self.current_ambient:
            return
        sound = self.sounds.get(f'ambient_{realm}')
        if sound and self.ambient_channel:
            try:
                self.ambient_channel.play(sound, loops=-1, fade_ms=1000)
                self.current_ambient = realm
            except Exception:
                pass

    def stop_ambient(self):
        """Fade out the current ambient drone."""
        if self.ambient_channel:
            try:
                self.ambient_channel.fadeout(500)
            except Exception:
                pass
        self.current_ambient = None

    def toggle_mute(self):
        """Toggle mute. Returns True if now muted."""
        self.muted = not self.muted
        if self.muted:
            self.stop_ambient()
        return self.muted
