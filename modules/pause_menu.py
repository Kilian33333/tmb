"""Pause menu for the fight"""
import pygame
from modules.screenSet import screen, WHITE, GRAY, BLACK
from modules.settings_ui import settings_menu
from modules.settings_manager import load_settings

WIDTH = screen.get_width()
HEIGHT = screen.get_height()

# Fonts will be initialized on first use
_fonts_initialized = False
pause_menu_font = None
pause_item_font = None

def _init_fonts():
    """Initialize fonts (called on first use)"""
    global _fonts_initialized, pause_menu_font, pause_item_font
    if not _fonts_initialized:
        pause_menu_font = pygame.font.Font("src/Jacquard24-Regular.ttf", 60)
        pause_item_font = pygame.font.Font("src/OleoScript-Regular.ttf", 40)
        _fonts_initialized = True

PAUSE_OPTIONS = [
    {"text": "Resume", "action": "resume"},
    {"text": "Settings", "action": "settings"},
    {"text": "Back to Menu", "action": "menu"}
]

def pause_menu():
    """Pause menu - returns 'resume', 'settings', or 'menu'"""
    _init_fonts()
    clock = pygame.time.Clock()
    selected_index = 0
    
    while True:
        clock.tick(60)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw title
        title_text = pause_menu_font.render("PAUSED", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Draw options
        y_offset = 250
        for i, option in enumerate(PAUSE_OPTIONS):
            is_selected = (i == selected_index)
            color = WHITE if is_selected else GRAY
            
            option_text = pause_item_font.render(option["text"], True, color)
            option_rect = option_text.get_rect(center=(WIDTH // 2, y_offset))
            screen.blit(option_text, option_rect)
            
            if is_selected:
                # Draw selection indicator
                pygame.draw.rect(screen, WHITE, (option_rect.x - 30, option_rect.y, option_rect.width + 60, option_rect.height), 3)
            
            y_offset += 100
        
        # Instructions
        inst_font = pygame.font.Font("src/OleoScript-Regular.ttf", 24)
        inst_text = inst_font.render("UP/DOWN - Select  |  ENTER - Confirm  |  ESC - Resume", True, GRAY)
        screen.blit(inst_text, (WIDTH // 2 - inst_text.get_width() // 2, HEIGHT - 50))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(PAUSE_OPTIONS)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(PAUSE_OPTIONS)
                elif event.key == pygame.K_RETURN:
                    action = PAUSE_OPTIONS[selected_index]["action"]
                    if action == "settings":
                        settings_menu()
                        load_settings()  # Reload in case user changed them
                        selected_index = 0  # Reset selection after settings
                    else:
                        return action
        
        pygame.display.flip()
