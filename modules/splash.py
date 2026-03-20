import pygame
import glob

from modules.screenSet import screen

tick = 0
loading_complete = False
fade_started = False
splash_image = pygame.image.load("src/splash.png").convert_alpha()
scaled_width = int(splash_image.get_width() * (screen.get_height() / splash_image.get_height()))
splash_image_scaled = pygame.transform.scale(splash_image, (scaled_width, screen.get_height()))
background_draw_x = int((screen.get_width() - scaled_width) / 2)

fade_duration = 45  # frames for fade animation

loading_font = pygame.font.Font("src/Jacquard24-Regular.ttf", 30)
prompt_font = pygame.font.Font("src/Jacquard24-Regular.ttf", 25)
bar_width = 300
bar_height = 20
bar_x = (screen.get_width() - bar_width) // 2
bar_y = screen.get_height() // 2 + 200

# Collect all files to "load"
def collect_files():
    """Collect all .py files and assets to display during loading"""
    files = []

    # Get all python scripts & asset files
    py_files = glob.glob("**/*.py", recursive=True)
    files.extend([f"Loading {f}" for f in py_files])
    asset_patterns = ["**/*.png", "**/*.ttf", "**/*.wav"]
    for pattern in asset_patterns:
        asset_files = glob.glob(pattern, recursive=True)
        files.extend([f"Loading {f}" for f in asset_files])

    files.extend([""]) # hi kilian if you leave this empty the progress text will
                       # disappear when loading is complete, if you want you can put
                       # something like "waiting for player" here :)
    return files

loading_files = collect_files()
frames_per_file = 17

# returns the current loading file and progress percentage
def get_loading_info(current_tick, display_duration):
    if not loading_files:
        return "Loading...", 0.0

    file_index = min(current_tick // frames_per_file, len(loading_files) - 1)
    progress = min((current_tick / frames_per_file) / len(loading_files), 1.0)

    return loading_files[file_index], progress

def splash(): # will return true as long as the splash screen is being drawn
    global tick, loading_complete, fade_started
    loading_duration = len(loading_files) * frames_per_file

    # fade out if any key is pressed (and loading is complete)
    if loading_complete and not fade_started:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                fade_started = True
                tick = 0  # Reset tick for fade animation

    # fade out animation
    if fade_started:
        if tick < fade_duration:
            screen.blit(splash_image_scaled, (background_draw_x, 0))

            # Calculate alpha for fade out
            fade_progress = tick / fade_duration
            alpha = int(255 * (1 - fade_progress))

            # apply alpha as last
            fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
            fade_surface.fill((0,0,0))
            fade_surface.set_alpha(255 - alpha)
            screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            tick += 1
            return True
        else:
            return False

    # Normal loading screen
    screen.blit(splash_image_scaled, (background_draw_x, 0))

    # Draw loading information
    loading_text, progress = get_loading_info(tick, loading_duration)
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
    fill_width = int(bar_width * progress) # loading bar fill
    pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, fill_width, bar_height))
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

    text_surface = loading_font.render(loading_text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, bar_y + bar_height + 25))
    screen.blit(text_surface, text_rect)

    # Check if loading is complete
    if tick >= loading_duration:
        loading_complete = True
        prompt_text = prompt_font.render("Press any key to continue", True, (255, 255, 255))
        prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 60))
        screen.blit(prompt_text, prompt_rect)

    pygame.display.flip()
    tick += 1

    return True