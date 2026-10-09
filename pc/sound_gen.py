"""
=============================================================================
🔊 1990s Arcade FM/Synth Sound Generator
=============================================================================
Synthesizes 1990s arcade cabinet sound effects: Engine roar, tire screech,
turbo blow-off, Doppler near-miss whooshes, and crash explosions.
"""

import math
import numpy as np
import pygame


class SoundEngine:
    """Real-time 1990s arcade sound generator."""

    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.enabled = True
        self.sounds = {}
        self.channels = {}

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(16)
        except Exception as e:
            print(f"Audio init warning: {e}")
            self.enabled = False
            return

        self._generate_all_sfx()

    def _make_sound(self, audio_data: np.ndarray) -> pygame.mixer.Sound:
        audio_data = np.clip(audio_data, -1.0, 1.0)
        int16_data = (audio_data * 32767).astype(np.int16)
        if int16_data.ndim == 1:
            stereo = np.column_stack((int16_data, int16_data))
        else:
            stereo = int16_data
        stereo = np.ascontiguousarray(stereo)
        return pygame.sndarray.make_sound(stereo)

    def _generate_all_sfx(self):
        sr = self.sample_rate

        # 1. 1990s Arcade Engine Roar (FM Harmonic Synthesis)
        t_eng = np.linspace(0, 0.8, int(sr * 0.8), endpoint=False)
        base_f = 56.0
        # Sawtooth harmonic blend
        engine_wave = (
            0.50 * np.sin(2 * np.pi * base_f * t_eng)
            + 0.28 * np.sin(2 * np.pi * base_f * 2 * t_eng)
            + 0.16 * np.sin(2 * np.pi * base_f * 3 * t_eng)
            + 0.10 * np.sin(2 * np.pi * base_f * 4 * t_eng)
            + 0.04 * np.random.uniform(-1, 1, len(t_eng))
        )
        self.sounds["engine"] = self._make_sound(engine_wave * 0.40)

        # 2. Turbo Boost Whoosh
        t_nitro = np.linspace(0, 1.2, int(sr * 1.2), endpoint=False)
        noise = np.random.uniform(-0.8, 0.8, len(t_nitro))
        sweep = np.sin(2 * np.pi * (220 + 350 * t_nitro) * t_nitro)
        env = np.exp(-t_nitro * 1.5)
        self.sounds["nitro"] = self._make_sound((noise * 0.6 + sweep * 0.4) * env * 0.5)

        # 3. Arcade Tire Screech
        t_skid = np.linspace(0, 0.35, int(sr * 0.35), endpoint=False)
        skid_mod = np.sin(2 * np.pi * 920 * t_skid) * np.sin(2 * np.pi * 1350 * t_skid)
        skid_noise = np.random.uniform(-0.4, 0.4, len(t_skid))
        skid_env = np.sin(np.pi * (t_skid / 0.35))
        self.sounds["skid"] = self._make_sound((skid_mod * 0.7 + skid_noise * 0.3) * skid_env * 0.45)

        # 4. Near-Miss Doppler Whoosh (Close Call)
        t_whoosh = np.linspace(0, 0.30, int(sr * 0.30), endpoint=False)
        freq = 720 - 500 * (t_whoosh / 0.30)
        whoosh_tone = np.sin(2 * np.pi * freq * t_whoosh)
        whoosh_env = np.sin(np.pi * (t_whoosh / 0.30)) ** 2
        self.sounds["near_miss"] = self._make_sound(whoosh_tone * whoosh_env * 0.55)

        # 5. Crash Metal Crunch & Impact
        t_crash = np.linspace(0, 0.85, int(sr * 0.85), endpoint=False)
        c_noise = np.random.uniform(-1, 1, len(t_crash)) * np.exp(-t_crash * 4.0)
        c_boom = np.sin(2 * np.pi * (95 * np.exp(-t_crash * 3.5)) * t_crash) * np.exp(-t_crash * 3.5)
        self.sounds["crash"] = self._make_sound((c_noise * 0.6 + c_boom * 0.6) * 0.75)

        # 6. Item / Coin Collect Chime
        t_coin = np.linspace(0, 0.22, int(sr * 0.22), endpoint=False)
        p1 = np.sin(2 * np.pi * 784.0 * t_coin) * (t_coin < 0.08)
        p2 = np.sin(2 * np.pi * 1046.5 * t_coin) * (t_coin >= 0.08)
        self.sounds["pickup"] = self._make_sound((p1 + p2) * np.exp(-t_coin * 6.0) * 0.5)

        # 7. UI Click / Switch
        t_click = np.linspace(0, 0.06, int(sr * 0.06), endpoint=False)
        self.sounds["click"] = self._make_sound(np.sin(2 * np.pi * 1400 * t_click) * np.exp(-t_click * 60) * 0.4)

    def start_engine_loop(self):
        if not self.enabled or "engine" not in self.sounds:
            return
        self.channels["engine"] = pygame.mixer.Channel(0)
        self.channels["engine"].play(self.sounds["engine"], loops=-1)
        self.channels["engine"].set_volume(0.28)

    def update_engine_pitch(self, speed_ratio: float, is_nitro: bool = False):
        if not self.enabled or "engine" not in self.channels:
            return
        vol = 0.22 + 0.38 * min(1.0, speed_ratio)
        if is_nitro:
            vol = min(0.7, vol + 0.15)
        self.channels["engine"].set_volume(vol)

    def play(self, sfx_name: str, volume: float = 0.5):
        if not self.enabled or sfx_name not in self.sounds:
            return
        snd = self.sounds[sfx_name]
        snd.set_volume(volume)
        snd.play()
