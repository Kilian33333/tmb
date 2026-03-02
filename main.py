import pygame
import sys
from modules import enemy
from modules import player
from modules.story import *
from modules.enemy import Enemy
from modules.player import Player
from modules.screenSet import *
from modules.debug import draw_debug_info, debug_mode
from modules.music import *



# --------------------
# Setup
# --------------------

devmode = False

pygame.init()
pygame.display.set_caption("Knight Fighter - Story Mode")
init_mixer()
clock = pygame.time.Clock()
font = pygame.font.Font("src\\Jacquard24-Regular.ttf", 24)
bigger_font = pygame.font.Font("src\\Jacquard24-Regular.ttf", 48)

WIDTH = screen.get_width()
HEIGHT = screen.get_height()

FLOOR_Y = 500
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
    strength = 9
    color = (200, 50 + fight_number * 3 % 150, 50)

    if fight_number == MAX_FIGHTS:
        strength = int(strength * 2.5)
        color = (120, 0, 120)

    return Enemy(650, color, health=100, strength=strength, fight_number=fight_number)


def draw_ui(player, enemy, fight_number):
    pygame.draw.rect(screen, (255,0,0), (25, 25, player.health * 5, 40))
    pygame.draw.rect(screen, (255,0,0), (WIDTH - 25 - enemy.health * 5, 25, enemy.health * 5, 40))

    txt = bigger_font.render(f"Fight {fight_number}/{MAX_FIGHTS}", True, (255,255,255))
    screen.blit(txt, (WIDTH/2-txt.get_width()/2, 20))


def fight_loop(player, enemy, fight_number):
    running = True

    while running:
        
        clock.tick(60)
        keys = pygame.key.get_pressed()
        
        update_music(fight_number, MAX_FIGHTS)

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

        # Enemy
        enemy.apply_gravity(FLOOR_Y)
        
        global debug_mode

        "f3 - open debug menu, f2 - close debug menu"
        if keys[pygame.K_F3]:
            print("F3 pressed")
            debug_mode = True
        if keys[pygame.K_F2]:
            print("F2 pressed")
            debug_mode = False

        if debug_mode:
          draw_debug_info(player, enemy)
          

        #--------------------
        # Player Attacks
        #--------------------

        #Devmode
        if keys[pygame.K_F5]:
            global devmode
            devmode = True
        elif keys[pygame.K_1] and devmode:
            enemy.take_damage(666)
        elif keys[pygame.K_2] and devmode:
            player.take_damage(666)
        elif keys[pygame.K_3] and devmode:
            player.health = player.max_health
        elif keys[pygame.K_4] and devmode:
            enemy.health = enemy.max_health
        elif keys[pygame.K_5] and devmode:
            player.attack_cooldown = 0
        elif keys[pygame.K_6] and devmode:
            enemy.attack_cooldown = 0
        elif keys[pygame.K_7] and devmode:
            player.speed = 10
        else:
            pass

        if player.block_active == False:
            if keys[pygame.K_q] and not player.is_jumping:
                player.attack(enemy, "Front Kick")
            if keys[pygame.K_q] and player.is_jumping:
                player.attack(enemy, "Rush Kick")
            if keys[pygame.K_e]:
                player.attack(enemy, "High Kick") and not player.is_jumping
            if keys[pygame.K_r]:
                player.attack(enemy, "Upward swing")
            if keys[pygame.K_c]:
                player.attack(enemy, "Side head strike")
            if keys[pygame.K_x]:
                player.attack(enemy, "Direct Punch")        
            if keys[pygame.K_f]:
                player.attack(enemy, "Ultimate")
            

        def knockback( given_to, knockback_strength):
            """Apply knockback once per-hit by setting a flag on the target.
            Subsequent calls while the flag is set will do nothing.
            """
            if given_to == "enemy":
                if getattr(enemy, 'knockback_applied', False):
                    return None
                enemy.rect.x = max(0, enemy.rect.x - knockback_strength*player.facing)
                enemy.rect.y = max(0, enemy.rect.y - knockback_strength/3)

                enemy.knockback_applied = True
            elif given_to == "player":
                if getattr(player, 'knockback_applied', False):
                    return None
                player.rect.x = max(0, player.rect.x + knockback_strength*enemy.facing)
                player.rect.y = max(0, player.rect.y - knockback_strength/3)
                player.knockback_applied = True
            return None

        if player.attack_cooldown == 1:
            if getattr(enemy, 'knockback_applied', False):
                enemy.knockback_applied = False
            if getattr(player, 'knockback_applied', False):
                player.knockback_applied = False

        if player.attack_cooldown != 0:
            if player.current_attack_type == "Rush Kick" and player.is_jumping == True:
                player.rect.x = max(0, player.rect.x - 30)
                player.rect.y = 150
            elif player.current_attack_type == "High Kick" and enemy.rect.colliderect(player.rect.inflate(20, 0)) and player.attack_cooldown == round(player.max_attack_cooldown*0.65):
                knockback("enemy", 300)
            elif player.current_attack_type == "Upward swing" and enemy.rect.colliderect(player.rect.inflate(20, 0)) and player.attack_cooldown == round(player.max_attack_cooldown*0.65):
                knockback("enemy", 700)
                

        # Deal player damage if flag is set during cooldown
        if hasattr(player, 'damage_dealt') and player.damage_dealt and player.attack_cooldown > 0:
            if player.rect.colliderect(enemy.rect.inflate(20, 0)):
                damage = player.ATTACKS[player.current_attack_type]["damage"]
                enemy.take_damage(damage)
            player.damage_dealt = False

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
        # Debug Mode
        # --------------------
    

# --------------------
# Main Game
# --------------------

def main():
    show_cutscene("Knight of the North\n\nPress any key to begin your journey...")

    player = Player(150)

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
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Exception occurred. Press Ctrl+C to exit.")
