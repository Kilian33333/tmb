"""Settings menu interface"""
import pygame
from modules.screenSet import screen, WHITE, GRAY, BLACK
from modules.settings_manager import get_settings, set_setting
from modules.music import update_music_volume

WIDTH = screen.get_width()
HEIGHT = screen.get_height()

# Fonts will be initialized on first use
_fonts_initialized = False
settings_menu_font = None
settings_content_font = None
settings_small_font = None

def _init_fonts():
    """Initialize fonts (called on first use)"""
    global _fonts_initialized, settings_menu_font, settings_content_font, settings_small_font
    if not _fonts_initialized:
        settings_menu_font = pygame.font.Font("src/OleoScript-Regular.ttf", 40)
        settings_content_font = pygame.font.Font("src/OleoScript-Regular.ttf", 28)
        settings_small_font = pygame.font.Font("src/OleoScript-Regular.ttf", 16)
        _fonts_initialized = True

SETTINGS_ITEMS = [
    {"name": "music_volume", "label": "Music Volume", "min": 0, "max": 120, "step": 10, "display": "%"},
    {"name": "sound_effects_volume", "label": "Sound Effects", "min": 0, "max": 120, "step": 10, "display": "%"},
    {"name": "particle_intensity", "label": "Particle Effects", "min": 0, "max": 100, "step": 10, "display": "%"},
    {"name": "screen_type", "label": "Screen Type", "type": "enum", "options": ["Fullscreen", "Window"]},
]

def draw_slider(y_pos, label, value, min_val, max_val, is_selected, is_editing, display_suffix=""):
    """Draw a slider with label"""
    _init_fonts()
    label_text = settings_content_font.render(label, True, WHITE if is_selected else GRAY)
    screen.blit(label_text, (50, y_pos))
    
    # Slider bar
    slider_x = 400
    slider_width = 300
    slider_y = y_pos + 10
    
    # Background bar
    pygame.draw.rect(screen, (100, 100, 100), (slider_x, slider_y, slider_width, 30))
    
    # Filled bar
    fill_width = (value - min_val) / (max_val - min_val) * slider_width if max_val > min_val else 0
    pygame.draw.rect(screen, (0, 150, 255) if is_editing else (100, 200, 255), (slider_x, slider_y, fill_width, 30))
    
    # Border
    border_color = WHITE if is_selected else GRAY
    border_width = 3 if is_editing else 1
    pygame.draw.rect(screen, border_color, (slider_x, slider_y, slider_width, 30), border_width)
    
    # Value text
    value_text = settings_content_font.render(f"{value}{display_suffix}", True, WHITE)
    screen.blit(value_text, (slider_x + slider_width + 20, y_pos))

def draw_enum(y_pos, label, options, selected_idx, is_selected, is_editing):
    """Draw an enum selector"""
    _init_fonts()
    label_text = settings_content_font.render(label, True, WHITE if is_selected else GRAY)
    screen.blit(label_text, (50, y_pos))
    
    # Options display with selection highlighting
    options_text = " | ".join([f"[{opt}]" if i == selected_idx else opt for i, opt in enumerate(options)])
    text_color = (0, 150, 255) if is_editing else (150, 200, 255) if is_selected else GRAY
    value_text = settings_content_font.render(options_text, True, text_color)
    screen.blit(value_text, (400, y_pos))
    
    # Draw border when editing
    if is_editing:
        border_rect = pygame.Rect(395, y_pos - 5, value_text.get_width() + 10, value_text.get_height() + 10)
        pygame.draw.rect(screen, WHITE, border_rect, 3)

def settings_menu():
    """Settings menu loop - returns when ESC is pressed"""
    _init_fonts()
    clock = pygame.time.Clock()
    running = True
    selected_index = 0
    editing_index = -1  # Which slider is being edited
    
    current_settings = get_settings()
    
    # Map setting names to current values
    setting_values = {item["name"]: current_settings[item["name"]] for item in SETTINGS_ITEMS}
    
    while running:
        clock.tick(60)
        
        # Load background
        try:
            settings_background = pygame.image.load("src/guides_background.png").convert_alpha()
            settings_background = pygame.transform.scale(settings_background, (WIDTH, HEIGHT))
            screen.blit(settings_background, (0, 0))
        except:
            screen.fill(BLACK)
        
        # Draw title
        title_font = pygame.font.Font("src/Jacquard24-Regular.ttf", 60)
        title_text = title_font.render("SETTINGS", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 30))
        
        # Draw each setting
        y_offset = 150
        for i, item in enumerate(SETTINGS_ITEMS):
            is_selected = (i == selected_index)
            is_editing = (i == editing_index)
            
            if item.get("type") == "enum":
                current_value = setting_values[item["name"]]
                draw_enum(y_offset, item["label"], item["options"], current_value, is_selected, is_editing)
            else:
                current_value = setting_values[item["name"]]
                display_suffix = item.get("display", "")
                draw_slider(y_offset, item["label"], current_value, item["min"], item["max"], is_selected, is_editing, display_suffix)
            
            y_offset += 100
        
        # Draw instructions
        inst_y = HEIGHT - 120
        inst_font = pygame.font.Font("src/OleoScript-Regular.ttf", 20)
        
        instructions = [
            "UP/DOWN ARROW - Select setting",
            "ENTER - Edit selected slider/toggle enum",
            "LEFT/RIGHT ARROW - Adjust value (10 step)",
            "ESC - Exit and save settings"
        ]
        
        for idx, inst in enumerate(instructions):
            inst_text = inst_font.render(inst, True, GRAY)
            screen.blit(inst_text, (50, inst_y + idx * 25))
        
        # Handle input
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Save settings
                    for key, value in setting_values.items():
                        set_setting(key, value)
                    # Apply volume changes immediately
                    update_music_volume()
                    return True
                
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(SETTINGS_ITEMS)
                    editing_index = -1
                
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(SETTINGS_ITEMS)
                    editing_index = -1
                
                elif event.key == pygame.K_RETURN:
                    if editing_index == selected_index:
                        # Stop editing
                        editing_index = -1
                    else:
                        # Start editing
                        editing_index = selected_index
                
                elif event.key == pygame.K_LEFT and editing_index == selected_index:
                    item = SETTINGS_ITEMS[selected_index]
                    if item.get("type") == "enum":
                        current_value = setting_values[item["name"]]
                        setting_values[item["name"]] = (current_value - 1) % len(item["options"])
                    else:
                        step = item.get("step", 1)
                        current_value = setting_values[item["name"]]
                        new_value = max(item["min"], current_value - step)
                        setting_values[item["name"]] = new_value
                
                elif event.key == pygame.K_RIGHT and editing_index == selected_index:
                    item = SETTINGS_ITEMS[selected_index]
                    if item.get("type") == "enum":
                        current_value = setting_values[item["name"]]
                        setting_values[item["name"]] = (current_value + 1) % len(item["options"])
                    else:
                        step = item.get("step", 1)
                        current_value = setting_values[item["name"]]
                        new_value = min(item["max"], current_value + step)
                        setting_values[item["name"]] = new_value
        
        pygame.display.flip()
    
    return True
