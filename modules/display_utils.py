"""Display utilities for visual effects like brightness and particle intensity"""
import pygame
from modules.settings_manager import get_setting

def apply_brightness(screen):
    """Apply brightness adjustment to the screen using an overlay"""
    brightness = get_setting("brightness")
    
    # Brightness is 0-200 where 100 is normal
    if brightness == 100:
        return
    
    if brightness < 100:
        # Darken by blitting a semi-transparent black overlay
        darkness = (100 - brightness) / 100.0
        overlay = pygame.Surface(screen.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(int(255 * darkness))
        screen.blit(overlay, (0, 0))
    else:
        # Brighten by blitting a semi-transparent white overlay
        brightness_amount = (brightness - 100) / 100.0
        overlay = pygame.Surface(screen.get_size())
        overlay.fill((255, 255, 255))
        overlay.set_alpha(int(255 * brightness_amount))
        screen.blit(overlay, (0, 0))

def get_particle_intensity():
    """Get the particle effect intensity (0-1)"""
    return get_setting("particle_intensity") / 100.0

def should_show_particles(base_chance=1.0):
    """Determine if particles should be shown based on intensity setting"""
    intensity = get_particle_intensity()
    return base_chance <= intensity
