import pygame

# Read screen type setting (avoiding circular imports by importing here)
def _get_screen_type():
    """Get screen type setting, with fallback to fullscreen if setting not available"""
    try:
        from modules.settings_manager import get_setting
        screen_type = get_setting("screen_type")
        return screen_type  # 0 = fullscreen, 1 = arcade, 2 = window
    except:
        return 0  # Default to fullscreen

# Initialize screen based on setting
screen_type = _get_screen_type()

# Arcade mode: render at 1920x1080 but display as 1280x720 fullscreen
ARCADE_WIDTH = 1280
ARCADE_HEIGHT = 720
GAME_WIDTH = 1920
GAME_HEIGHT = 1080

if screen_type == 0:
    # Native fullscreen
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    _arcade_mode = False
    fullscreen_display = None
elif screen_type == 1:
    # Arcade mode: game renders at 1920x1080, displayed as 1280x720 on fullscreen
    fullscreen_display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    _arcade_mode = True
else:  # screen_type == 2
    # Window mode - 1920x1080 windowed
    screen = pygame.display.set_mode((1920, 1080))
    _arcade_mode = False
    fullscreen_display = None

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)

def update_display():
    """Update the display - handles arcade mode scaling and presentation"""
    global _arcade_mode, screen, fullscreen_display
    
    if _arcade_mode and fullscreen_display:
        # Get fullscreen dimensions
        display_width = fullscreen_display.get_width()
        display_height = fullscreen_display.get_height()
        
        # Calculate scaling to fit 1920x1080 into 1280x720 box while maintaining aspect ratio
        scale_x = ARCADE_WIDTH / GAME_WIDTH
        scale_y = ARCADE_HEIGHT / GAME_HEIGHT
        scale = min(scale_x, scale_y)
        
        # Calculate scaled dimensions
        scaled_width = int(GAME_WIDTH * scale)
        scaled_height = int(GAME_HEIGHT * scale)
        
        # Center the scaled content
        x_offset = (display_width - scaled_width) // 2
        y_offset = (display_height - scaled_height) // 2
        
        # Fill display with black background
        fullscreen_display.fill(BLACK)
        
        # Scale the game surface to 1280x720 and blit to fullscreen
        if scaled_width != GAME_WIDTH or scaled_height != GAME_HEIGHT:
            scaled_surface = pygame.transform.scale(screen, (scaled_width, scaled_height))
            fullscreen_display.blit(scaled_surface, (x_offset, y_offset))
        else:
            fullscreen_display.blit(screen, (x_offset, y_offset))
        
        pygame.display.flip()
    else:
        pygame.display.flip()