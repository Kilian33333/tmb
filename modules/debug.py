import pygame
from modules.screenSet import screen
keys = pygame.key.get_pressed()
debug_mode = False


def draw_debug_info(player, enemy):
    """Draw debug information on screen"""
    print("Debug Mode Active")
    font = pygame.font.Font("src\\Jacquard24-Regular.ttf", 20)
    debug_lines = [
        f"Player Health: {player.health}/{player.max_health}",
        f"Player Attack Cooldown: {player.attack_cooldown}",
        f"Enemy Health: {enemy.health}/{enemy.max_health}",
        f"Enemy Attack Cooldown: {enemy.attack_cooldown}",
        f"Enemy Incoming Attack: {enemy.incoming_attack}",
        f"Enemy Telegraph Cooldown: {enemy.telegraph_cooldown}",
    ]
    
    for i, line in enumerate(debug_lines):
        debug_surf = font.render(line, True, (255, 255, 0))
        screen.blit(debug_surf, (10, 10 + i * 25))