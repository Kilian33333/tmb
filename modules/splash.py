import pygame

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

# Credits configuration
credits = [
    ["Main-Development:", "Kilian D."],
    ["Programming:", "Kilian D.", "Co.Programming:", "Jannis S."],
    ["Music by:", "Kilian D.","Mixing:", "Alen K."],
    ["Main-Artwork:", "Kilian D.", "Background and Character Art:", "Jannis S.", "Kilian D.", "Moritz G."],
    ["Special Thanks:", "Alen K.", "Moritz G."]
]
credit_display_duration = 330  # frames to show each credit
credit_fade_duration = 30  # frames for fade in/out
credit_cycle_tick = 0

# Collect all asset files and python scripts
def collect_files():
    files = []

    files.extend(["load Pictures", "Adjusting Gravity", "Forge armor", "Recruiting Knights", "Draw Menu and Starting..."])
    return files

loading_files = collect_files()
frames_per_file = 35

# returns the current loading file and progress percentage
def get_loading_info(current_tick, display_duration):
    if not loading_files:
        return "Loading...", 0.0

    file_index = min(current_tick // frames_per_file, len(loading_files) - 1)
    progress = min((current_tick / frames_per_file) / len(loading_files), 1.0)

    return loading_files[file_index], progress

def get_current_credit_alpha(cycle_tick, total_duration, fade_duration):
    if cycle_tick < fade_duration:
        # Fade in
        return int(255 * (cycle_tick / fade_duration))
    elif cycle_tick < total_duration - fade_duration:
        # Full opacity
        return 255
    else:
        # Fade out
        fade_out_progress = (cycle_tick - (total_duration - fade_duration)) / fade_duration
        return int(255 * (1 - fade_out_progress))

def draw_credits():
    global credit_cycle_tick
    total_cycle_duration = credit_display_duration + credit_fade_duration
    credit_index = (credit_cycle_tick // total_cycle_duration) % len(credits)
    cycle_position = credit_cycle_tick % total_cycle_duration
    current_credit = credits[credit_index]
    alpha = get_current_credit_alpha(cycle_position, credit_display_duration, credit_fade_duration)

    # right side
    credit_x = screen.get_width() - 370
    credit_y = screen.get_height() // 2 - 50
    title_surface = prompt_font.render(current_credit[0], True, (255, 255, 255))
    title_surface.set_alpha(alpha)
    screen.blit(title_surface, (credit_x, credit_y))

    # Render credit names
    for i, name in enumerate(current_credit[1:], 1):
        name_surface = prompt_font.render(name, True, (200, 200, 200))
        name_surface.set_alpha(alpha)
        screen.blit(name_surface, (credit_x, credit_y + 30 * i))

    credit_cycle_tick += 1

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

    # Draw cycling credits
    draw_credits()

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