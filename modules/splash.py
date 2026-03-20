import pygame

from modules.screenSet import screen

tick = 77
splash_image = pygame.image.load("src/splash.png").convert_alpha()
scaled_width = int(splash_image.get_width() * (screen.get_height() / splash_image.get_height()))
splash_image_scaled = pygame.transform.scale(splash_image, (scaled_width, screen.get_height()))
background_draw_x = int((screen.get_width() - scaled_width) / 2)

def splash(): # will return true as long as the splash screen is being drawn
    global tick
    print(f"splash: {tick}")
    print(background_draw_x)
    if tick < 7 * 60: # show for 7 seconds
        screen.blit(splash_image_scaled, (background_draw_x, 0))
        pygame.display.flip()
        tick+=1

        return True
    else:
        return False