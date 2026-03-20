import pygame

from modules.screenSet import screen

tick = 0
splash_image = pygame.image.load("src/splash.png").convert_alpha()
scaled_width = int(splash_image.get_width() * (screen.get_height() / splash_image.get_height()))
splash_image_scaled = pygame.transform.scale(splash_image, (scaled_width, screen.get_height()))
background_draw_x = int((screen.get_width() - scaled_width) / 2)

fade_duration = 45  # frames for fade animation

def splash(): # will return true as long as the splash screen is being drawn
    global tick
    print(f"splash: {tick}")
    print(background_draw_x)

    display_duration = 7 * 60  # 5 seconds at 60 fps
    total_duration = display_duration + fade_duration

    if tick < total_duration:
        # Calculate alpha for fade out
        if tick >= display_duration:
            fade_progress = (tick - display_duration) / fade_duration
            alpha = int(255 * (1 - fade_progress))
        else:
            alpha = 255

        # apply alpha
        splash_surface = splash_image_scaled.copy()
        splash_surface.set_alpha(alpha)

        screen.blit(splash_surface, (background_draw_x, 0))
        pygame.display.flip()
        tick += 1

        return True
    else:
        return False