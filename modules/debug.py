import pygame
from modules.screenSet import screen
keys = pygame.key.get_pressed()
debug_mode = False


def draw_debug_info(player, enemy):
    """Draw organized debug information on screen (Minecraft F3 style)"""
    font = pygame.font.SysFont("consolas", 12)  # Consolas monospace font
    line_height = 14
    green = (0, 255, 0)  # Bright green
    
    # Screen dimensions for positioning
    width = screen.get_width()
    height = screen.get_height()
    
    # --- TOP LEFT: PLAYER INFO ---
    player_info = [
        "=== PLAYER ===",
        f"Health: {player.health}/{player.max_health}",
        f"Pos: ({player.rect.x}, {player.rect.y})",
        f"Speed: {player.speed}",
        f"Attack CD: {player.attack_cooldown}",
        f"Block: {player.block_active}",
        f"Is Jumping: {player.is_jumping}",
        f"Attack Type: {player.current_attack_type}",
    ]
    y_offset = 50
    for i, line in enumerate(player_info):
        surf = font.render(line, True, green)
        screen.blit(surf, (10, y_offset + i * line_height))
    
    # --- TOP RIGHT: ENEMY INFO ---
    enemy_info = [
        "=== ENEMY ===",
        f"Health: {enemy.health}/{enemy.max_health}",
        f"Pos: ({enemy.rect.x}, {enemy.rect.y})",
        f"Speed: {enemy.speed}",
        f"Attack CD: {enemy.attack_cooldown}",
        f"Telegraph CD: {enemy.telegraph_cooldown}",
        f"Incoming: {enemy.incoming_attack}",
        f"Decision: {enemy.decision_timer}",
    ]
    y_offset = 50
    for i, line in enumerate(enemy_info):
        surf = font.render(line, True, green)
        right_x = width - len(line) * 7 - 15
        screen.blit(surf, (right_x, y_offset + i * line_height))
    
    # --- BOTTOM LEFT: COORDINATES ---
    coords_info = [
        "=== COORDINATES ===",
        f"Player: ({player.rect.centerx}, {player.rect.centery})",
        f"Enemy: ({enemy.rect.centerx}, {enemy.rect.centery})",
        f"Distance: {abs(enemy.rect.centerx - player.rect.centerx)}",
    ]
    y_offset = height - 80
    for i, line in enumerate(coords_info):
        surf = font.render(line, True, green)
        screen.blit(surf, (10, y_offset + i * line_height))
    
    # --- BOTTOM RIGHT: GAME STATE ---
    game_info = [
        "=== GAME ===",
        f"FPS: 60",
        f"Screen: {width}x{height}",
        f"P Damage: {getattr(player, 'damage_dealt', False)}",
    ]
    y_offset = height - 70
    for i, line in enumerate(game_info):
        surf = font.render(line, True, green)
        right_x = width - len(line) * 7 - 15
        screen.blit(surf, (right_x, y_offset + i * line_height))