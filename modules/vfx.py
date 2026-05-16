import pygame

from modules.screenSet import screen

ememy_got_hit_picture = pygame.image.load("src/vfx/EnemyGotHit.png").convert_alpha()
enemy_got_destroyed_picture = pygame.image.load("src/vfx/EnemyDestroyed.png").convert_alpha()
you_got_hit_picture = pygame.image.load("src/vfx/YouGotHit.png").convert_alpha()

ememy_got_hit_picture = pygame.transform.scale(ememy_got_hit_picture, (400, 125))
enemy_got_destroyed_picture = pygame.transform.scale(enemy_got_destroyed_picture, (400, 125))
you_got_hit_picture = pygame.transform.scale(you_got_hit_picture, (400, 125))

# Store originals (unmodified)
ememy_got_hit_original = ememy_got_hit_picture.copy()
enemy_got_destroyed_original = enemy_got_destroyed_picture.copy()
you_got_hit_original = you_got_hit_picture.copy()

# Tracking variables
active_status_picture = None
active_status_original = None
status_tick_start = 0

def draw_status_pictures(given_status=None):
    """Draw status effects with fade out. Call with status name to trigger, or with None to draw active effect."""
    global active_status_picture, active_status_original, status_tick_start
    
    # If given_status is provided, trigger a new effect
    if given_status is not None:
        if given_status == "player_hit":
            active_status_original = you_got_hit_original
        elif given_status == "enemy_destroyed":
            active_status_original = enemy_got_destroyed_original
        elif given_status == "enemy_hit":
            active_status_original = ememy_got_hit_original
        status_tick_start = pygame.time.get_ticks()
        return
    
    # Draw active effect if exists
    if active_status_original is not None:
        elapsed_ticks = pygame.time.get_ticks() - status_tick_start
        
        # Fade out after 600 ticks
        if elapsed_ticks < 600:
            alpha = int(255 * (1 - elapsed_ticks / 600))
            # Create a fresh copy with correct alpha
            active_status_picture = active_status_original.copy()
            active_status_picture.set_alpha(alpha)
            status_center = (screen.get_width() // 2 - active_status_picture.get_width() // 2, 100)
            screen.blit(active_status_picture, status_center)
        else:
            # Clear when fully faded
            active_status_original = None