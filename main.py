import pygame
import sys
from modules.player import *
from modules.enemy import *
from modules.story import CutsceneManager
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

# Initialize cutscene manager
CutsceneManager.init(screen, clock, font)

WIDTH = screen.get_width()
HEIGHT = screen.get_height()

FLOOR_Y = 500
MAX_FIGHTS = 20

# --------------------
# Assets
# --------------------
active_background = ["src\\old_forest.png", "src\\swapped_hills.png", "src\\wished_bridge.png", "src\\big_castle.png"]

ult_ui = pygame.image.load("src\\ult_ui.png").convert_alpha()
ult_ui = pygame.transform.scale(ult_ui, (170, 170))

try:
    background_img = pygame.image.load(active_background[0]).convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except:
    background_img = None
    print("Background image not found, using solid color instead.")

# --------------------
# Story / Cutscene
# --------------------




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
    #health bars
    pygame.draw.rect(screen, (255,0,0), (310, 725, player.health * 4, 60))
    pygame.draw.rect(screen, (255,0,0), (WIDTH - 310 - enemy.health * 4, 725, enemy.health * 4, 60))
    #cooldown bars
    if player.max_attack_cooldown > 0:
        pygame.draw.rect(screen, (0,255,255), (310, 625, (player.attack_cooldown/(player.max_attack_cooldown)*100) * 4, 60))
    if enemy.max_attack_cooldown > 0:
        pygame.draw.rect(screen, (0,255,255), (WIDTH - 310 -  (enemy.attack_cooldown/(enemy.max_attack_cooldown)*100) * 4, 625, (enemy.attack_cooldown/(enemy.max_attack_cooldown+0.0001)*100) * 4, 60))

    #circle with ult ui image
    ult_color = (255, 0, 0) 
    if player.ultimate_charge == 100:
        ult_color = 255
    else:
        ult_color = 0
    pygame.draw.circle(screen, (0, 0, 0), (175, 700), 125)
    pygame.draw.rect(screen, (255, 0, 0), (100, -player.ultimate_charge * 1.37 + 775, 150, player.ultimate_charge * 1.37))
    screen.blit(ult_ui, (175 - ult_ui.get_width()//2, 700 - ult_ui.get_height()//2))
    pygame.draw.circle(screen, (ult_color, 0, 0), (175, 700), 125, 40)

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
        
        # Import for accessing flag
        from modules import debug
        if debug.show_hitboxes:
            debug.draw_hitboxes(player, enemy)
          

        #--------------------
        # Player Attacks
        #--------------------

        #Devmode - F5 + Ctrl to activate
        from modules import debug
        global devmode, last_f5_ctrl_state
        
        if keys[pygame.K_F5] and keys[pygame.K_LCTRL]:
            devmode = True
        
        # Devmode commands with F5 + Number
        if devmode:
            print("Dev mode command activated")
            if debug_mode:
                debug.toggle_hitboxes(True)
                print("Hitboxes shown")
            elif keys[pygame.K_1]:
                enemy.take_damage(666)
            elif keys[pygame.K_2]:
                player.take_damage(666)
            elif keys[pygame.K_3]:
                player.health = player.max_health
            elif keys[pygame.K_4]:
                enemy.health = enemy.max_health
            elif keys[pygame.K_5]:
                player.attack_cooldown = 0
            elif keys[pygame.K_6]:
                enemy.attack_cooldown = 0
            elif keys[pygame.K_7]:
                player.speed = 10
            elif keys[pygame.K_8]:
                player.ultimate_charge = 100
            elif keys[pygame.K_9]:
                enemy.fight_number = 20
            elif not debug_mode: 
                debug.toggle_hitboxes(False)


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
            if keys[pygame.K_f] and player.ultimate_charge == 100:
                player.attack(enemy, "Ultimate")
            

        def knockback( given_to, knockback_strength, shockwave):
            """Apply knockback once per-hit by setting a flag on the target.
            Subsequent calls while the flag is set will do nothing.
            """
            if given_to == "enemy":
                if getattr(enemy, 'knockback_applied', False):
                    return None
                
                # Change knockback Direction based on position difference if shockwave:
                if shockwave:
                    if enemy.damage_rect.centerx < player.damage_rect.centerx:
                        enemy.damage_rect.x = max(0, enemy.damage_rect.x - knockback_strength*1)
                        enemy.damage_rect.y = max(0, enemy.damage_rect.y - knockback_strength/3)
                        enemy.attack_rect.x = max(0, enemy.attack_rect.x - knockback_strength*1)
                        enemy.attack_rect.y = max(0, enemy.attack_rect.y - knockback_strength/3)
                        enemy.take_damage(50)
                    else:
                        enemy.damage_rect.x = max(0, enemy.damage_rect.x - knockback_strength*-1)
                        enemy.damage_rect.y = max(0, enemy.damage_rect.y - knockback_strength/3)
                        enemy.attack_rect.x = max(0, enemy.attack_rect.x - knockback_strength*-1)
                        enemy.attack_rect.y = max(0, enemy.attack_rect.y - knockback_strength/3)
                else:
                    enemy.damage_rect.x = max(0, enemy.damage_rect.x - knockback_strength*player.facing)
                    enemy.damage_rect.y = max(0, enemy.damage_rect.y - knockback_strength/3)
                    enemy.attack_rect.x = max(0, enemy.attack_rect.x - knockback_strength*player.facing)
                    enemy.attack_rect.y = max(0, enemy.attack_rect.y - knockback_strength/3)

                enemy.knockback_applied = True
            elif given_to == "player":
                if getattr(player, 'knockback_applied', False):
                    return None
                player.damage_rect.x = max(0, player.damage_rect.x + knockback_strength*enemy.facing)
                player.damage_rect.y = max(0, player.damage_rect.y - knockback_strength/3)
                player.attack_rect.x = max(0, player.attack_rect.x + knockback_strength*enemy.facing)
                player.attack_rect.y = max(0, player.attack_rect.y - knockback_strength/3)
                player.knockback_applied = True
            return None
        #Ultimate Shockwave
        if player.current_attack_type == "Ultimate" and round(player.max_attack_cooldown*0.65) - 15 <= player.attack_cooldown <= round(player.max_attack_cooldown*0.65):
            knockback("enemy", 500, True)
            #Draw shockwave effect
            shockwave_max_radius = 1000
            progress = 1 - (player.attack_cooldown - (round(player.max_attack_cooldown*0.65) - 15)) / 15
            shockwave_radius = int(50 + progress * 750)
            shockwave_surface = pygame.Surface((shockwave_max_radius*2, shockwave_max_radius*2), pygame.SRCALPHA)
            shockwave_color = (235, 235, 255, int(200 * (1 - progress)))
            player.ultimate_charge = 0 
            
            # Draw expanding shockwave circles with fading effect, cut it at the bottom
            pygame.draw.circle(shockwave_surface, shockwave_color, (shockwave_max_radius, shockwave_max_radius), shockwave_radius, 70)
            screen.blit(shockwave_surface, (player.damage_rect.centerx - shockwave_max_radius, player.damage_rect.centery - shockwave_max_radius))
            pygame.draw.circle(shockwave_surface, shockwave_color, (shockwave_max_radius, shockwave_max_radius), shockwave_radius*0.66, 50)
            screen.blit(shockwave_surface, (player.damage_rect.centerx - shockwave_max_radius, player.damage_rect.centery - shockwave_max_radius))
            pygame.draw.circle(shockwave_surface, shockwave_color, (shockwave_max_radius, shockwave_max_radius), shockwave_radius*0.33, 30)
            screen.blit(shockwave_surface, (player.damage_rect.centerx - shockwave_max_radius, player.damage_rect.centery - shockwave_max_radius))
        
        if player.current_attack_type == "Ultimate" and round(player.attack_cooldown) > 0:
            player.resist = True
        else:
            player.resist = False

        if player.attack_cooldown == 1:
            if getattr(enemy, 'knockback_applied', False):
                enemy.knockback_applied = False
            if getattr(player, 'knockback_applied', False):
                player.knockback_applied = False

        if player.attack_cooldown != 0:
            if player.current_attack_type == "Rush Kick" and player.is_jumping == True:
                player.damage_rect.x = max(0, player.damage_rect.x - 30)
                player.damage_rect.y = 150
                player.attack_rect.x = max(0, player.attack_rect.x - 30)
                player.attack_rect.y = 150
            elif player.current_attack_type == "High Kick" and enemy.damage_rect.colliderect(player.attack_rect) and player.attack_cooldown == round(player.max_attack_cooldown*0.65):
                knockback("enemy", 300, False)
            elif player.current_attack_type == "Upward swing" and enemy.damage_rect.colliderect(player.attack_rect) and player.attack_cooldown == round(player.max_attack_cooldown*0.65):
                knockback("enemy", 700, False)
            
        #charge Ultimate if Player hits Enemy with different attack types
        if player.attack_cooldown == round(player.max_attack_cooldown*0.68) and (player.current_attack_type != "Direct Punch" or player.current_attack_type != "Ultimate"):
            if player.attack_rect.colliderect(enemy.damage_rect):
                player.ultimate_charge = min(100, player.ultimate_charge + (player.ATTACKS[player.current_attack_type]["damage"] // 7))                

        # Deal player damage if flag is set during cooldown
        if hasattr(player, 'damage_dealt') and player.damage_dealt and player.attack_cooldown > 0:
            if player.attack_rect.colliderect(enemy.damage_rect):
                damage = player.ATTACKS[player.current_attack_type]["damage"]
                enemy.take_damage(damage)
            else:
                pass
            player.damage_dealt = False

        if debug_mode:
            draw_debug_info(player, enemy)
        # Floor
        pygame.draw.rect(screen, (80, 60, 40), (0, FLOOR_Y, WIDTH, HEIGHT - FLOOR_Y))

        # Enemy AI
        enemy.ai(player, WIDTH)

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
    CutsceneManager.show(1)

    player = Player(150)
    global devmode, last_f5_ctrl_state

    for fight_number in range(1, MAX_FIGHTS + 1):
        enemy = create_enemy(fight_number)
        
        if fight_number == 6:
            CutsceneManager.show(3)
        elif fight_number == 11:
            CutsceneManager.show(4)
        elif fight_number == 16:
            CutsceneManager.show(5)

        win = fight_loop(player, enemy, fight_number)
        
        # Reset devmode state for next fight
        devmode = False
        last_f5_ctrl_state = False

        if not win:
            CutsceneManager.show(2)
            pygame.quit()
            sys.exit()

        player.health = min(player.max_health, player.health + 35)

    CutsceneManager.show(6)

    pygame.quit()



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Exception occurred. Press Ctrl+C to exit.")
