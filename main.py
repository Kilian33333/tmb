import math
import json
import pygame
import sys
from datetime import datetime
from modules.player import *
from modules.enemy import *
from modules.story import CutsceneManager
from modules.screenSet import *
from modules.debug import draw_debug_info, debug_mode
from modules.music import *
from modules.sounds import *
from modules.pause_menu import pause_menu
from modules.settings_manager import load_settings
from modules.vfx import draw_status_pictures


# --------------------
# Setup
# --------------------
player_sound_pan = 0.0

devmode = False

pygame.init()
pygame.display.set_caption("Knight Fighter - Story Mode")
init_mixer()
clock = pygame.time.Clock()
font = pygame.font.Font("src/Jacquard24-Regular.ttf", 24)
bigger_font = pygame.font.Font("src/Jacquard24-Regular.ttf", 48)
background_img = None

# Initialize cutscene manager
CutsceneManager.init(screen, clock, font)

# Load settings
load_settings()

WIDTH = screen.get_width()
HEIGHT = screen.get_height()

FLOOR_Y = 500
MAX_FIGHTS = 20

# --------------------
# Assets
# --------------------
active_background = ["src/old_forest.png", "src/swapped_hills.jpeg", "src/wished_bridge.jpeg", "src/big_castle.jpg"]

ult_ui = pygame.image.load("src/ult_ui.png").convert_alpha()
ult_ui = pygame.transform.scale(ult_ui, (170, 170))

player_health_bar_under = pygame.image.load("src/healthbar_under.png")
player_health_bar_under = pygame.transform.scale(player_health_bar_under,(450,90))

enemy_health_bar_under = pygame.image.load("src/healthbar_under.png")
enemy_health_bar_under = pygame.transform.scale(enemy_health_bar_under,(450,90))

player_cooldownbar_under = pygame.image.load("src/cooldownbar_under.png")
player_cooldownbar_under = pygame.transform.scale(player_cooldownbar_under,(450,90))

enemy_cooldownbar_under = pygame.image.load("src/cooldownbar_under.png")
enemy_cooldownbar_under = pygame.transform.scale(enemy_cooldownbar_under,(450,90))

def change_background(i):
        global background_img
        print(f"Changing background to index {i}")
        try:
            background_img = pygame.image.load(active_background[i]).convert()
            background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
        except:
            background_img = None
            print(f"Background image (index {i}) not found, using solid color instead.")

change_background(0)  # Start with first background

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


class DamageIndicator:
    """Floating damage number that fades and moves up"""
    def __init__(self, x, y, damage, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.alpha = 255
        self.lifetime = 60  # frames
        self.age = 0
    
    def update(self):
        self.age += 1
        self.y -= 2  # Move up
        self.alpha = int(255 * (1 - self.age / self.lifetime))
    
    def draw(self, surface, font):
        if self.alpha > 0:
            damage_text = font.render(str(int(self.damage)), True, self.color)
            # Create a surface with alpha for fading effect
            text_surface = pygame.Surface(damage_text.get_size(), pygame.SRCALPHA)
            text_surface.blit(damage_text, (0, 0))
            text_surface.set_alpha(self.alpha)
            surface.blit(text_surface, (int(self.x), int(self.y)))
    
    def is_alive(self):
        return self.age < self.lifetime


def draw_ui(player, enemy, fight_number, damage_indicators):
    #health bars
    screen.blit(player_health_bar_under, (285, 710))
    screen.blit(enemy_health_bar_under, (WIDTH - 735, 710))

    screen.blit(player_cooldownbar_under, (285, 610))
    screen.blit(enemy_cooldownbar_under, (WIDTH - 735, 610))

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

    # Damage taken in this moment, calculated from enemys damage, checking if player has taken damage recently and detecting and calculating if shield is used in enemys case
    #player_active_taken_damage = enemy.current_attack_damage if enemy.current_attack_type and enemy.attack_cooldown > round(enemy.max_attack_cooldown*0.65) and enemy.attack_rect.colliderect(player.damage_rect) and not player.resist else 0
    #if enemy.current_attack_type and enemy.attack_cooldown > round(enemy.max_attack_cooldown*0.65) and enemy.attack_rect.colliderect(player.damage_rect) and player.resist:
    #    player_active_taken_damage = int(enemy.current_attack_damage * 0.3) # shield reduces damage to 30%

    # Add damage indicator when player takes damage
    #if player_active_taken_damage > 0 and not hasattr(player, '_damage_indicator_shown') or not player._damage_indicator_shown:
    #    damage_indicators.append(DamageIndicator(player.damage_rect.centerx, player.damage_rect.centery - 50, player_active_taken_damage, color=(255, 100, 100)))
    #    player._damage_indicator_shown = True
    #elif player_active_taken_damage == 0:
    #    player._damage_indicator_shown = False

    #player_damage_label = font.render(f"Damage Taken: {player_active_taken_damage}", True, (255, 100, 100))
    #screen.blit(player_damage_label, (20, 20))


def fight_loop(player, enemy, fight_number):
    running = True
    damage_indicators = []  # List to store active damage indicators

    while running:
        
        clock.tick(60)
        keys = pygame.key.get_pressed()
        

        #pan value based on player position, -100 (left) to +100 (right)
        player_sound_pan = ((player.damage_rect.centerx / WIDTH) - 0.5) * 200

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_result = pause_menu()
                    if pause_result == "menu":
                        return None  # Break fight loop and go to menu
                    elif pause_result == "quit":
                        return None  # Break and quit
                    # resume does nothing, fight continues

        # Background
        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill((60, 120, 180))

        # Player
        player.move(keys, WIDTH, FLOOR_Y)
        player.apply_gravity(FLOOR_Y)

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
                enemy.take_damage(100)
            elif keys[pygame.K_2]:
                player.take_damage(666) # 👹
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
                    else:
                        enemy.damage_rect.x = max(0, enemy.damage_rect.x - knockback_strength*-1)
                        enemy.damage_rect.y = max(0, enemy.damage_rect.y - knockback_strength/3)
                        enemy.attack_rect.x = max(0, enemy.attack_rect.x - knockback_strength*-1)
                        enemy.attack_rect.y = max(0, enemy.attack_rect.y - knockback_strength/3)
                    enemy.take_damage(int(480 / math.log((abs(player.x - enemy.x)/3) + 2)))
                else:
                    if not enemy.shield_active:
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
                player.damage_rect.x = max(0, player.damage_rect.x - 30 / player.facing)
                player.damage_rect.y = 150
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
                draw_status_pictures("enemy_hit")
                # Add damage indicator for enemy
                damage_indicators.append(DamageIndicator(enemy.damage_rect.centerx, enemy.damage_rect.centery, f"-{damage}", color=(255, 0, 0)))
            else:
                pass
            player.damage_dealt = False

        if player.is_jumping and player.current_attack_type == "Rush Kick" and player.attack_cooldown > 0 and enemy.damage_rect.colliderect(player.attack_rect) and enemy.shield_active:
            player.velocity_y = 30
            player.take_damage(0.1)
        
        # Update and draw damage indicators
        for indicator in damage_indicators[:]:
            indicator.update()
            if not indicator.is_alive():
                damage_indicators.remove(indicator)
        
        # Floor
        pygame.draw.rect(screen, (80, 60, 40), (0, FLOOR_Y, WIDTH, HEIGHT - FLOOR_Y))

        # Enemy AI
        enemy.ai(player, WIDTH)

        player.update()
        enemy.update()

        player.draw(screen)
        enemy.draw(screen)

        # Draw damage indicators
        for indicator in damage_indicators:
            indicator.draw(screen, bigger_font)
        if debug_mode:
            draw_debug_info(player, enemy)

        draw_ui(player, enemy, fight_number, damage_indicators)
        draw_status_pictures()

        pygame.display.update()

        if enemy.health <= 0:
            player.damage_freeze_timer = 20  # Freeze damage for 20 ticks after enemy dies
            draw_status_pictures("enemy_destroyed")
            return True
        if player.health <= 0:
            return False
        
        # --------------------
        # Sound Effects
        # --------------------
        if player.current_attack_type == "Ultimate" and player.attack_cooldown == round(player.max_attack_cooldown*0.99):
            play_sound("ultimate", pan=player_sound_pan, volume=1.0)

        # --------------------
        # Debug Mode
        # --------------------
    

# --------------------
# Results Screen
# --------------------

def save_results(player_name, total_time, total_damage):
    """Save game results to JSON file"""
    results = {
        "player_name": player_name,
        "time_seconds": total_time,
        "damage_taken": total_damage,
        "timestamp": datetime.now().isoformat()
    }
    
    # Load existing results if file exists
    try:
        with open("game_results.json", "r") as f:
            all_results = json.load(f)
    except:
        all_results = []
    
    # Add new result
    all_results.append(results)
    
    # Save back to file
    with open("game_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"Results saved: {player_name}, Time: {total_time}s, Damage: {total_damage}")


def results_screen(player, total_time):
    """Display results screen with name input and submit button"""
    total_damage = player.max_health - player.health
    player_name = ""
    font_small = pygame.font.Font("src/Jacquard24-Regular.ttf", 32)
    font_large = pygame.font.Font("src/Jacquard24-Regular.ttf", 48)
    
    # Button properties
    button_rect = pygame.Rect(WIDTH // 2 - 100, 500, 200, 60)
    button_hover = False
    
    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_RETURN and len(player_name) > 0:
                    # Submit
                    save_results(player_name, int(total_time), int(total_damage))
                    running = False
                elif len(player_name) < 15 and event.unicode.isalnum():
                    player_name += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos) and len(player_name) > 0:
                    save_results(player_name, int(total_time), int(total_damage))
                    running = False
        
        # Check button hover
        mouse_pos = pygame.mouse.get_pos()
        button_hover = button_rect.collidepoint(mouse_pos)
        
        # Draw
        screen.fill((30, 30, 50))
        
        # Title
        title = font_large.render("Victory!", True, (255, 215, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        
        # Stats
        time_text = font_small.render(f"Time: {int(total_time)}s", True, (100, 200, 255))
        damage_text = font_small.render(f"Damage Taken: {int(total_damage)}", True, (255, 100, 100))
        screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 150))
        screen.blit(damage_text, (WIDTH // 2 - damage_text.get_width() // 2, 220))
        
        # Name input label
        label = font_small.render("Enter Name (max 15 chars):", True, (255, 255, 255))
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 320))
        
        # Name input box
        input_box = pygame.Rect(WIDTH // 2 - 150, 380, 300, 50)
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)
        
        # Display name with cursor
        name_display = font_small.render(player_name + "|", True, (255, 255, 255))
        screen.blit(name_display, (input_box.x + 10, input_box.y + 10))
        
        # Submit button
        button_color = (100, 150, 255) if button_hover else (70, 100, 200)
        pygame.draw.rect(screen, button_color, button_rect)
        button_text = font_small.render("Submit", True, (255, 255, 255))
        screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2, button_rect.centery - button_text.get_height() // 2))
        
        # Instructions
        instruction = pygame.font.Font("src/Jacquard24-Regular.ttf", 24).render("Press ENTER or click Submit", True, (200, 200, 200))
        screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 600))
        
        pygame.display.update()


# --------------------
# Main Game
# --------------------

def main():
    CutsceneManager.show(1)  # Story intro (not counted)

    player = Player(150)
    global devmode, last_f5_ctrl_state
    
    # Track stats - only count fight time, not cutscenes
    total_time = 0

    for fight_number in range(1, MAX_FIGHTS + 1):
        # Cutscenes happen BEFORE timing starts
        if fight_number == 6:
            CutsceneManager.show(3)
            change_background(1)
            play_mid_fight_music()
        elif fight_number == 11:
            CutsceneManager.show(4)
            change_background(2)
        elif fight_number == 16:
            CutsceneManager.show(5)
            change_background(3)
            play_boss_music()

        # NOW start timing the fight
        enemy = create_enemy(fight_number)
        fight_start_time = pygame.time.get_ticks() / 1000.0
        
        win = fight_loop(player, enemy, fight_number)
        
        # End timing after fight completes
        fight_end_time = pygame.time.get_ticks() / 1000.0
        total_time += (fight_end_time - fight_start_time)
        
        # Reset devmode state for next fight
        devmode = False
        last_f5_ctrl_state = False

        if not win:
            CutsceneManager.show(2)
            return None  # Game over, exit main loop

        player.health = min(player.max_health, player.health + 35)

    CutsceneManager.show(6)  # Story ending (not counted)
    
    # Show results screen and save data (only fight time)

    results_screen(player, total_time)



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Exception occurred. Press Ctrl+C to exit.")
