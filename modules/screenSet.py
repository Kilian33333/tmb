import pygame

# Read screen type setting (avoiding circular imports by importing here)
def _get_screen_type():
    """Get screen type setting, with fallback to fullscreen if setting not available"""
    try:
        from modules.settings_manager import get_setting
        screen_type = get_setting("screen_type")
        return screen_type  # 0 = fullscreen, 1 = window, 2 = arcade
    except:
        return 0  # Default to fullscreen

# Initialize screen based on setting
screen_type = _get_screen_type()
if screen_type == 0 or screen_type == 2:  # Fullscreen or Arcade mode
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((1920, 1080))

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)