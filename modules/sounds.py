import os
import pygame
import math
from modules.settings_manager import get_setting

pygame.mixer.pre_init(44100, -16, 2, 4096)  # 4096 or 8192
pygame.mixer.init()

# Sounds einmal laden
sounds = {
    "hover": pygame.mixer.Sound(os.path.join("src", "hover.wav")),
    "click": pygame.mixer.Sound(os.path.join("src", "click.wav")),
    "turn_page": pygame.mixer.Sound(os.path.join("src", "turn_page.wav")),
    "ultimate": pygame.mixer.Sound(os.path.join("src", "ultimate.wav")),
}

def play_sound(name, pan=0.0, volume=1.0):
    """
    name: "hover", "click", etc.
    pan: -100 (links) bis +100 (rechts)
    volume: 0.0 bis 1.0
    """
    
    sound = sounds.get(name)
    if not sound:
        print(f"Sound '{name}' nicht gefunden")
        return

    # Apply sound effects multiplicator from settings
    sound_mult = get_setting("sound_effects_volume") / 100.0
    adjusted_volume = volume * sound_mult
    adjusted_volume = min(1.0, max(0.0, adjusted_volume))  # Clamp to 0-1

    channel = sound.play()
    if not channel:
        return

    # Equal Power Panning
    angle = (pan/100 + 1) * math.pi / 4
    left = math.cos(angle) * adjusted_volume
    right = math.sin(angle) * adjusted_volume

    channel.set_volume(left, right)