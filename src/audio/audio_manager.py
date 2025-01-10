from utils.settings import *

class AudioManager:
    def __init__(self, default_volume=0.5):
        """Initialize the audio manager and load sounds."""
        pygame.mixer.init()
        self.default_volume = default_volume
        self.sounds = {
            'jump': pygame.mixer.Sound(join('..', 'assets', 'sounds', 'player-jump.ogg')),
            'next_level': pygame.mixer.Sound(join('..', 'assets', 'sounds', 'portal-jump.wav')),
            'dash': pygame.mixer.Sound(join('..', 'assets', 'sounds', 'dash.wav')),
            'death': pygame.mixer.Sound(join('..', 'assets', 'sounds', 'death.ogg')),
            'respawn': pygame.mixer.Sound(join('..', 'assets', 'sounds', 'respawn.ogg')),
            'bg_music': pygame.mixer.Sound(join('..', 'assets', 'sounds', 'bg_music.mp3')),
        }
        self.volumes = {key: self.default_volume for key in self.sounds}
        self.apply_volumes()

    def apply_volumes(self):
        """Apply the current volume settings to all sounds."""
        for sound_name, sound in self.sounds.items():
            sound.set_volume(self.volumes[sound_name])

    def set_sound_volume(self, sound_name, volume):
        """
        Set the volume for a specific sound.
        sound_name: Name of the sound
        volume: Float value between 0.0 (muted) and 1.0 (max).
        """
        if sound_name in self.sounds:
            # Clamp volume between 0 and 1
            self.volumes[sound_name] = max(0.0, min(volume, 1.0))
            self.sounds[sound_name].set_volume(self.volumes[sound_name])
        else:
            print(f"Sound '{sound_name}' not found.")

    def set_global_volume(self, volume):
        """
        Set the volume for all sounds globally.
        volume: Float value between 0.0 (muted) and 1.0 (max).
        """
        self.default_volume = max(0.0, min(volume, 1.0))
        for sound_name in self.volumes:
            self.volumes[sound_name] = self.default_volume
        self.apply_volumes()

    def play(self, sound_name, loop=0):
        """Play a sound by name. Optionally loop."""
        if sound_name in self.sounds:
            self.sounds[sound_name].play(loops=loop)
        else:
            print(f"Sound '{sound_name}' not found.")

    def stop(self, sound_name):
        """Stop a sound by name."""
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()
        else:
            print(f"Sound '{sound_name}' not found.")
