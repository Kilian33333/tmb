import pygame
import os

current_music = None
play_music = None

def init_mixer():
    pygame.mixer.init()

def play_boss_music():
    global current_music
    try:
        path = os.path.join("src", "BossFightTheme.wav")
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)
        current_music = "boss"
        print(f"Playing boss music: {path}")
    except Exception as e:
        print(f"Boss music error: {e}")

def play_menu_music():
    global current_music
    try:
        path = os.path.join("src", "menu_music.wav")
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        current_music = "menu"
        print(f"Playing menu music: {path}")
    except Exception as e:
        print(f"Normal music error: {e}")

def stop_music():
    pygame.mixer.music.stop()
    current_music = None

def update_music(fight_number, max_fights):
    global current_music
    global play_music
    if fight_number == max_fights:
        play_music = "boss"
    
    if play_music == "boss" and current_music != "boss":
        play_boss_music()

