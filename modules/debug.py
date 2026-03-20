import pygame
from modules.screenSet import screen
keys = pygame.key.get_pressed()
debug_mode = False
show_hitboxes = False


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
        f"Pos: ({player.damage_rect.x}, {player.damage_rect.y})",
        f"Speed: {player.speed}",
        f"Attack CD: {player.attack_cooldown}",
        f"Block: {player.block_active}",
        f"Is Jumping: {player.is_jumping}",
        f"Attack Type: {player.current_attack_type}",
        f"Facing: {player.facing}",
        f"max_Attack_CD: {player.max_attack_cooldown}",
        f"Ult Charge: {player.ultimate_charge}",
        f"Is Enemy Hit: {getattr(player, 'damage_dealt', False)}",
    ]
    y_offset = 50
    for i, line in enumerate(player_info):
        surf = font.render(line, True, green)
        screen.blit(surf, (10, y_offset + i * line_height))
    
    # --- TOP RIGHT: ENEMY INFO ---
    enemy_info = [
        "=== ENEMY ===",
        f"Health: {enemy.health}/{enemy.max_health}",
        f"Pos: ({enemy.damage_rect.x}, {enemy.damage_rect.y})",
        f"Speed: {enemy.speed}",
        f"Attack CD: {enemy.attack_cooldown}",
        f"Telegraph CD: {enemy.telegraph_cooldown}",
        f"Incoming: {enemy.incoming_attack}",
        f"Decision: {enemy.decision_timer}",
        f"Stage: {enemy.stage_name}",
        f"Dmg Mult: {enemy.damage_multiplier}",
        f"Resist: {enemy.resistance}",
        f"Strength: {enemy.strength}",
        f"Crit Chance: {enemy.crit_chance}%",
        f"Crit Add: {enemy.crit_addition}",
    ]
    y_offset = 50
    for i, line in enumerate(enemy_info):
        surf = font.render(line, True, green)
        right_x = width - len(line) * 7 - 15
        screen.blit(surf, (right_x, y_offset + i * line_height))
    
    # --- BOTTOM LEFT: COORDINATES ---
    coords_info = [
        "=== COORDINATES ===",
        f"Player: ({player.damage_rect.centerx}, {player.damage_rect.centery})",
        f"Enemy: ({enemy.damage_rect.centerx}, {enemy.damage_rect.centery})",
        f"Distance: {abs(enemy.damage_rect.centerx - player.damage_rect.centerx)}",
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


def draw_hitboxes(player, enemy):
    """Draw damage and attack hitboxes for both player and enemy"""
    # Player damage hitbox (red)
    pygame.draw.rect(screen, (255, 0, 0), player.damage_rect, 2)
    # Player attack hitbox (orange, dashed effect)
    pygame.draw.rect(screen, (255, 165, 0), player.attack_rect, 1)
    
    # Enemy damage hitbox (red)
    pygame.draw.rect(screen, (255, 0, 0), enemy.damage_rect, 2)
    # Enemy attack hitbox (orange, dashed effect)
    pygame.draw.rect(screen, (255, 165, 0), enemy.attack_rect, 1)
    
    # Draw labels
    font = pygame.font.SysFont("consolas", 10)
    
    # Player labels
    p_damage_label = font.render("P_DMG", True, (255, 0, 0))
    p_attack_label = font.render("P_ATK", True, (255, 165, 0))
    screen.blit(p_damage_label, (player.damage_rect.x + 2, player.damage_rect.y - 15))
    screen.blit(p_attack_label, (player.attack_rect.x + 2, player.attack_rect.y + player.attack_rect.height + 2))
    
    # Enemy labels
    e_damage_label = font.render("E_DMG", True, (255, 0, 0))
    e_attack_label = font.render("E_ATK", True, (255, 165, 0))
    screen.blit(e_damage_label, (enemy.damage_rect.x + 2, enemy.damage_rect.y - 15))
    screen.blit(e_attack_label, (enemy.attack_rect.x + 2, enemy.attack_rect.y + enemy.attack_rect.height + 2))


def toggle_hitboxes(shown=False):
    """Toggle hitbox display"""
    global show_hitboxes
    show_hitboxes = shown
    return show_hitboxes