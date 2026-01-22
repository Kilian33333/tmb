import pygame
import sys
from modules.movement import *
from modules.ai import *
from modules. import *

# --------------------
# Setup
# --------------------
pygame.init()
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Knight Fighter - Story Mode")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

FLOOR_Y = 380
MAX_FIGHTS = 20

# --------------------
# Assets
# --------------------
try:
    background_img = pygame.image.load("assets/background.png").convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except:
    background_img = None

# --------------------
# Classes
# --------------------

class Fighter:
    def __init__(self, x, color, strength=10, is_player=False):
        self.rect = pygame.Rect(x, FLOOR_Y - 80, 50, 80)
        self.color = color
        self.health = 100
        self.strength = strength
        self.speed = 4
        self.is_player = is_player
        self.attack_cooldown = 0

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

    def move(self, keys):
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed

    def ai_move(self, target):
        if target.rect.centerx < self.rect.centerx:
            self.rect.x -= self.speed - 1
        else:
            self.rect.x += self.speed - 1

    def attack(self, target):
        if self.attack_cooldown == 0:
            if self.rect.colliderect(target.rect.inflate(20, 0)):
                target.health -= self.strength
            self.attack_cooldown = 30

    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1


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
    strength = 8 + fight_number * 2
    color = (200, 50 + fight_number * 5 % 200, 50)

    if fight_number == MAX_FIGHTS:
        strength *= 2
        color = (120, 0, 120)

    return Fighter(650, color, strength)


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
        player.move(keys)
        if keys[pygame.K_SPACE]:
            player.attack(enemy)

        # Enemy AI
        enemy.ai_move(player)
        enemy.attack(player)

        player.update()
        enemy.update()

        player.draw()
        enemy.draw()

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

    player = Fighter(150, (50, 100, 255), strength=12, is_player=True)

    for fight_number in range(1, MAX_FIGHTS + 1):

        enemy = create_enemy(fight_number)

        if fight_number == MAX_FIGHTS:
            show_cutscene("The Dark Knight awaits...\n\nFinal Battle")

        win = fight_loop(player, enemy, fight_number)

        if not win:
            show_cutscene("You have fallen...\n\nGame Over")
            pygame.quit()
            sys.exit()

        player.health = min(100, player.health + 30)

        if fight_number % 5 == 0 and fight_number != MAX_FIGHTS:
            show_cutscene(f"You defeated 5 enemies!\n\nYour legend grows...")

    show_cutscene("The kingdom is safe.\n\nYou are a true Knight.\n\nThe End")

    pygame.quit()


if __name__ == "__main__":
    main()
