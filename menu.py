import pygame
import sys
from main import main
from modules.screenSet import *
from modules.music import play_menu_music

pygame.init()

pygame.display.set_caption("Main Menu")

menu_button_font = pygame.font.Font("src\\Jacquard24-Regular.ttf", 60)

start_button_rect = pygame.Rect(screen.get_width() / 2 - 160, screen.get_height() / 2 + 160, 200, 70)
guides_button_rect = pygame.Rect(screen.get_width() / 2 + 40, screen.get_height() / 2 + 160, 200, 70)
quit_button_rect = pygame.Rect(screen.get_width() / 2 + 240, screen.get_height() / 2 + 160, 200, 70)

play_menu_music()
background_image_original = pygame.image.load("src\\knight_loading_screen.png").convert_alpha()
bg_original_width = background_image_original.get_width()
bg_original_height = background_image_original.get_height()
screen_height = screen.get_height()
screen_width = screen.get_width()
bg_scaled_width = int(bg_original_width * (screen_height / bg_original_height))
bg_scaled_height = screen_height
background_image_scaled = pygame.transform.scale(background_image_original, (bg_scaled_width, bg_scaled_height))
background_draw_x = int((screen_width - bg_scaled_width) / 2)

underline_image = pygame.image.load("src\\underline_hover.png").convert_alpha()
 
menu_guides = [
    {"rect": start_button_rect, "text": "Start", "blink": True, "action": "start"},
    {"rect": guides_button_rect, "text": "Guides", "blink": False, "action": "guides"},
    {"rect": quit_button_rect, "text": "Quit", "blink": False, "action": "quit"}
]
selected_index = 0

clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()
fade_duration = 2000

def get_fade_color():
    """Smooth fading animation using sine wave for seamless color transitions"""
    import math
    current_time = pygame.time.get_ticks() - start_time
    cycle_position = (current_time % fade_duration) / fade_duration
    fade_value = (math.sin(cycle_position * 2 * math.pi) + 1) / 2
    color_value = int(fade_value * 150)
    
    return (255 - color_value, 255 - color_value, 255 - color_value)

def draw_button(rect, text, is_selected=False, default_color=GRAY, hover_color=WHITE, button_font=menu_button_font, blink=False):
    """Draw button with optional selection highlight"""
    color = hover_color if is_selected else default_color

    if blink and not is_selected:
        color = get_fade_color()

    label = button_font.render(text, True, color)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)

    if is_selected:
        underline_rect = underline_image.get_rect()
        underline_rect.centerx = label_rect.centerx
        underline_rect.top = label_rect.bottom - 5
        screen.blit(underline_image, underline_rect)

running = True
while running:
    dt = clock.tick(60)
    screen.fill(BLACK)
    screen.blit(background_image_scaled, (background_draw_x, 0))

    # Draw buttons with selection highlight
    for i, option in enumerate(menu_guides):
        is_selected = (i == selected_index)
        draw_button(option["rect"], option["text"], is_selected=is_selected, blink=option["blink"])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                selected_index = (selected_index - 1) % len(menu_guides)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN:
                selected_index = (selected_index + 1) % len(menu_guides)
            elif event.key == pygame.K_RETURN:
                action = menu_guides[selected_index]["action"]
                if action == "start":
                    pygame.mixer.music.stop()
                    main()
                    running = False
                elif action == "quit":
                    running = False

    pygame.display.flip()

pygame.quit()
sys.exit()
