import pygame
import os
from modules.settings_manager import get_setting

current_music = None
play_music = None

def get_music_volume(base_volume):
    """Calculate music volume with settings multiplier"""
    music_mult = get_setting("music_volume") / 100.0
    adjusted_volume = base_volume * music_mult
    return min(1.0, max(0.0, adjusted_volume))  # Clamp to 0-1

def init_mixer():
    """Initialize pygame mixer"""
    pygame.mixer.pre_init(44100, -16, 2, 4096)  # 4096 or 8192
    pygame.mixer.init()

def play_menu_music():
    global current_music
    try:
        path = os.path.join("src", "menu_music.wav")
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(get_music_volume(0.45))
        pygame.mixer.music.play(-1)
        current_music = "menu"
        print(f"Playing menu music: {path}")
    except Exception as e:
        print(f"Normal music error: {e}")

def play_boss_music():
    global current_music
    try:
        path = os.path.join("src", "BossFightTheme.wav")
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(get_music_volume(0.5))
        pygame.mixer.music.play(-1)
        current_music = "boss"
        print(f"Playing boss music: {path}")
    except Exception as e:
        print(f"Boss music error: {e}")

def play_mid_fight_music():
    global current_music
    try:
        path = os.path.join("src", "mid_fight_music.wav")
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(get_music_volume(0.35))
        pygame.mixer.music.play(-1)
        current_music = "mid_fight"
        print(f"Playing mid fight music: {path}")
    except Exception as e:
        print(f"Mid fight music error: {e}")

def stop_music():
    pygame.mixer.music.stop()
    current_music = None

def update_music_volume():
    """Update the currently playing music's volume based on current settings"""
    if not pygame.mixer.music.get_busy():
        return
    
    # Determine base volume based on current music
    base_volume = 0.45 if current_music == "menu" else 0.35 if current_music == "mid_fight" else 0.5
    pygame.mixer.music.set_volume(get_music_volume(base_volume))

def update_music(fight_number, max_fights):
    global current_music
    global play_music
    if fight_number == max_fights:
        play_music = "boss"
    
    if play_music == "boss" and current_music != "boss":
        play_boss_music()
