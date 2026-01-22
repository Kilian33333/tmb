import pygame
import sys
from modules.story import *
from modules.enemy import Enemy
from modules.player import Player
from modules.screenSet import *


# --------------------
# Setup
# --------------------
pygame.init()
pygame.display.set_caption("Knight Fighter - Story Mode")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

WIDTH = screen.get_width()
HEIGHT = screen.get_height()

FLOOR_Y = 400
MAX_FIGHTS = 20

# --------------------
# Assets
# --------------------
active_background = ["src\\old_forest.png", "src\\swapped_hills.png", "src\\wished_bridge.png", "src\\big_castle.png"]

try:
    background_img = pygame.image.load(active_background[0]).convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except:
    background_img = None

# --------------------
# Classes
# --------------------
# Fighter classes are now in modules: Player and Enemy


# --------------------
# Story / Cutscene
# --------------------

def show_cutscene(text):
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

        screen.fill((0, 0, 0))
        render_text_center(text)
        pygame.display.update()
        clock.tick(60)


def render_text_center(text):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        surf = font.render(line, True, (255, 255, 255))
        rect = surf.get_rect(center=(WIDTH//2, HEIGHT//2 + i * 30))
        screen.blit(surf, rect)


# --------------------
# Fight System
# --------------------

def create_enemy(fight_number):
    strength = 8 + fight_number * 1
    color = (200, 50 + fight_number * 3 % 150, 50)

    if fight_number == MAX_FIGHTS:
        strength = int(strength * 2.5)
        color = (120, 0, 120)

    return Enemy(650, color, health=100, strength=strength, fight_number=fight_number)


def draw_ui(player, enemy, fight_number):
    pygame.draw.rect(screen, (255,0,0), (50, 20, player.health * 2, 20))
    pygame.draw.rect(screen, (255,0,0), (600, 20, enemy.health * 2, 20))

    txt = font.render(f"Fight {fight_number}/{MAX_FIGHTS}", True, (255,255,255))
    screen.blit(txt, (400, 20))


def fight_loop(player, enemy, fight_number):
    running = True

    while running:
        clock.tick(60)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Background
        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill((60, 120, 180))

        # Floor
        pygame.draw.rect(screen, (80, 60, 40), (0, FLOOR_Y, WIDTH, HEIGHT - FLOOR_Y))

        # Player
        player.move(keys, WIDTH, FLOOR_Y)
        player.apply_gravity(FLOOR_Y)
        player.block(keys)
        
        # Player attacks - Q for slash, E for thrust, R for spin
        if keys[pygame.K_q]:
            player.attack(enemy, "slash")
        if keys[pygame.K_e]:
            player.attack(enemy, "thrust")
        if keys[pygame.K_r]:
            player.attack(enemy, "spin")

        # Enemy AI
        enemy.ai_move(player, WIDTH)
        enemy.ai_attack(player)

        player.update()
        enemy.update()

        player.draw(screen)
        enemy.draw(screen)

        draw_ui(player, enemy, fight_number)

        pygame.display.update()

        if enemy.health <= 0:
            return True
        if player.health <= 0:
            return False


# --------------------
# Main Game
# --------------------

def main():
    show_cutscene("Knight of the North\n\nPress any key to begin your journey...")

    player = Player(150, health=120, strength=12)

    for fight_number in range(1, MAX_FIGHTS + 1):

        enemy = create_enemy(fight_number)

        if fight_number == MAX_FIGHTS:
            show_cutscene("The Dark Knight awaits...\n\nFinal Battle")

        win = fight_loop(player, enemy, fight_number)

        if not win:
            show_cutscene("You have fallen...\n\nGame Over")
            pygame.quit()
            sys.exit()

        player.health = min(player.max_health, player.health + 35)

        if fight_number % 5 == 0 and fight_number != MAX_FIGHTS:
            show_cutscene(f"You defeated {fight_number} enemies!\n\nYour legend grows...")

    show_cutscene("The kingdom is safe.\n\nYou are a true Knight.\n\nThe End")

    pygame.quit()


if __name__ == "__main__":
    main()
