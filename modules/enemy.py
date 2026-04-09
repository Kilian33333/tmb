"""Enemy AI with multiple attacks and attack telegraph"""
import pygame
import random
import os
from .fighter import Fighter


class Enemy(Fighter):
#  Difficulty stages with stat multipliers
    #Difficulty 1: recruits - Enemy 1-3
    #Difficulty 2: heavy_recruits - Enemy 4-5
    #Difficulty 3: heavy_knight - Enemy 6-10
    #Difficulty 4: veteran_knight - Enemy 11-15
    #Difficulty 5: elite_knight - Enemy 16-18
    #Difficulty 6: magic_knight - Enemy 19
    #Difficulty 7: the_king - Enemy 20 (final boss)

    STAGES = {
        "recruits": {"damage_multiplier": 0.9, "resistance": 1.0, "speed_multiplier": 1.1, "crit_chance": 0, "crit_addition": 0, "intelligence": "Low"}, 
        "heavy_recruits": {"damage_multiplier": 1.0, "resistance": 1.5, "speed_multiplier": 1.0, "crit_chance": 5, "crit_addition": 0.05, "intelligence": "Low"},
        "heavy_knight": {"damage_multiplier": 1.0, "resistance": 2.0, "speed_multiplier": 1.0, "crit_chance": 5, "crit_addition": 0.15, "intelligence": "Medium"},
        "veteran_knight": {"damage_multiplier": 1.5, "resistance": 2.5, "speed_multiplier": 1.0, "crit_chance": 10, "crit_addition": 0.2, "intelligence": "Medium"},
        "elite_knight": {"damage_multiplier": 2.5, "resistance": 3.5, "speed_multiplier": 0.9, "crit_chance": 10, "crit_addition": 0.6, "intelligence": "High"},
        "magic_knight": {"damage_multiplier": 2.5, "resistance": 4.5, "speed_multiplier": 1.1, "crit_chance": 15, "crit_addition": 0.6, "intelligence": "High"},
        "the_king": {"damage_multiplier": 3.0, "resistance": 6.5, "speed_multiplier": 1.05, "crit_chance": 20, "crit_addition": 0.7, "intelligence": "High"},
    }
    # Attack patterns with damage and symbols
    ATTACKS = {
        "slash": {"damage": 8, "cooldown": 60, "symbol": "⚔", "telegraph_time": 25},
        "smash": {"damage": 12, "cooldown": 80, "symbol": "↓", "telegraph_time": 30},
        "thrust": {"damage": 10, "cooldown": 120, "symbol": "→", "telegraph_time": 28},
    }
    
    def __init__(self, x, color, health=100, strength=12, fight_number=1):
        super().__init__(x, color, health, strength)
        # Calculate stage based on fight number
        if fight_number <= 3:
            self.stage_num = 0  # recruits
        elif fight_number <= 5:
            self.stage_num = 1  # heavy_recruits
        elif fight_number <= 10:
            self.stage_num = 2  # heavy_knight
        elif fight_number <= 15:
            self.stage_num = 3  # veteran_knight
        elif fight_number <= 18:
            self.stage_num = 4  # elite_knight
        elif fight_number == 19:
            self.stage_num = 5  # magic_knight
        else:
            self.stage_num = 6  # the_king

        STAGENAMES = list(self.STAGES.keys())
        self.stage_name = STAGENAMES[min(self.stage_num, len(STAGENAMES))]
        # Damage hitbox (where enemy takes damage)
        self.damage_rect = pygame.Rect(x, 340, 100, 160)
        # Attack hitbox (where enemy deals damage - larger for attack reach)
        self.attack_rect = pygame.Rect(x, 340, 140, 160)
        # For backwards compatibility
        self.rect = self.damage_rect
        self.speed = 3
        self.fight_number = fight_number
        self.attack_cooldown = 0
        self.max_attack_cooldown = 0  # Track max for cooldown bar
        self.telegraph_cooldown = 0
        self.incoming_attack = None
        self.incoming_attack_symbol = None
        self.decision_timer = 0

        # Jump mechanics
        self.velocity_y = 0
        self.is_jumping = False
        self.jump_power = -15
        self.gravity = 0.5
        self.floor_y = 500

        self.facing = -1
        
        # Shield mechanics
        self.shield_active = False
        self.shield_duration = 0
        self.shield_cooldown = 0
        self.max_shield_duration = 300  # 5 seconds at 60fps
        self.max_shield_cooldown = 900  # 15 seconds at 60fps
        
        # AI action tracking
        self.current_action = "idle"

        # Scale difficulty
        self._scale_difficulty()
    
    def _scale_difficulty(self):
        """Scale stats based on fight number and stage multipliers"""
        stage_multipliers = self.STAGES[self.stage_name]
        
        self.speed = int(self.speed * stage_multipliers["speed_multiplier"])
        self.max_health = self.health
        self.strength = int(self.strength * stage_multipliers["damage_multiplier"])
        
        self.crit_chance = stage_multipliers["crit_chance"]
        self.crit_addition = stage_multipliers["crit_addition"]
        self.damage_multiplier = stage_multipliers["damage_multiplier"]
        self.resistance = stage_multipliers["resistance"]
        self.speed_multiplier = stage_multipliers["speed_multiplier"]
        
        # Behavior multipliers
    
    def draw(self, screen):
        """Draw enemy with health bar and attack telegraph"""
        pygame.draw.rect(screen, self.color, self.damage_rect)
        
        # Draw shield if active
        if self.shield_active:
            pygame.draw.rect(screen, (100, 150, 255), self.damage_rect, 3)
        
        if self.telegraph_cooldown > 0 and self.incoming_attack_symbol:
            font = pygame.font.SysFont("arial", 40)
            symbol_surf = font.render(self.incoming_attack_symbol, True, (255, 100, 0))
            symbol_rect = symbol_surf.get_rect(center=(self.damage_rect.centerx, self.damage_rect.top - 50))
            screen.blit(symbol_surf, symbol_rect)
            
            bar_width = 100
            bar_height = 8
            bar_x = self.damage_rect.centerx - bar_width // 2
            bar_y = self.damage_rect.top - 30
            
            pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # Green progress
            progress = max(0, self.telegraph_cooldown) / self.ATTACKS[self.incoming_attack]["telegraph_time"]
            pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, bar_width * progress, bar_height))
    

#---------------------------------------------
#           +++Movement Algorythm+++
#---------------------------------------------

#Possible player (or specific enemy) states to react to:
# - nearby wall
# - Using Ultimate
# - being far from player
# - Mid range from player
# - Close to player:
    # - Idle
    # - Attacking (with different attack types)
    # - Jumping
    # - blocking
# - colliding with player
    # - Idle
    # - Attacking (with different attack types)
    # - Jumping
    # - blocking
#Enemy will react to these states with different behaviors:
# - Idle
# - Move towards player
# - Move away from player
# - Jump
# - Shield
# - Telegraphed attack (with different attack types)
# - jump while moving towards player
# - jump while moving away from player

#AI will act random every 3 ticks, with weighted probabilities based on player state and multiplies or divides by stage

#Using probabilitys and multipliers/divisions per Player stage
#Player is:
# - far away: 50 Points Idle, 10 Points move towards, 0 Others
# - mid range: 30 Points Idle, 20 Points move towards, 5 Points move away, 10 Points jump, 10 Points shield, 0 Others

# - close but not colliding:
# - - idle: 20 Points Idle, 50 Points move towards, 5 Points move away, 5 Points jump, 0 Points shield, 10 Points attack
# - - attacking: 10 Points Idle, 0 Points move towards, 20 Points move away, 5 Points jump, 70 Points shield, 30 Points attack
# - - jumping: 20 Points Idle, 20 Points move towards, 5 Points move away, 2 Points jump, 0 Points shield, 10 Points attack
# - - blocking: 10 Points Idle, 10 Points move towards, 30 Points move away, 5 Points jump, 0 Points shield, 5 Points attack

# - colliding:
# - - idle: 20 Points Idle, 5 Points move towards, 20 Points move away, 10 Points jump, 0 Points shield, 80 Points attack
# - - attacking: 5 Points Idle, 0 Points move towards, 50 Points move away, 30 Points jump, 70 Points shield, 30 Points attack
# - - jumping: 20 Points Idle, 0 Points move towards, 60 Points move away, 10 Points jump, 0 Points shield, 80 Points attack
# - - blocking: 10 Points Idle, 0 Points move towards, 70 Points move away, 5 Points jump, 0 Points shield, 40 Points attack

    player_states = ["far", "mid", "close_idle", "close_attacking", "close_jumping", "close_blocking", "colliding_idle", "colliding_attacking", "colliding_jumping", "colliding_blocking",]
    chosing_states = ["idle", "move_towards", "move_away", "jump", "shield", "attack"]
    chosing_states_weights = {
        "far":          [83, 57, 3, 0, 1, 12],
        "mid":          [37, 68, 17, 2, 29, 7],
        "close_idle":   [4, 23, 14, 19, 33, 72],
        "close_attacking":[1, 6, 27, 11, 81, 88],
        "close_jumping":[9, 31, 4, 52, 6, 63],
        "close_blocking":[3, 16, 59, 8, 11, 41],
        "colliding_idle":[2, 4, 42, 28, 21, 91],
        "colliding_attacking":[0, 1, 12, 49, 93, 79],
        "colliding_jumping":[6, 0, 83, 18, 1, 69],
        "colliding_blocking":[1, 2, 91, 13, 0, 82],
    }

    def _get_player_state(self, target):
        """Determine the player's current state"""
        distance = abs(target.damage_rect.centerx - self.damage_rect.centerx)
        collision = self.damage_rect.colliderect(target.damage_rect)
        
        # Define distance ranges
        far_distance = 300
        mid_distance = 150
        
        if distance > far_distance:
            return "far"
        elif distance > mid_distance:
            return "mid"
        else:
            # Close range - check sub-states
            if collision:
                # Colliding - check player action
                if hasattr(target, 'is_jumping') and target.is_jumping:
                    return "colliding_jumping"
                elif hasattr(target, 'shield_active') and target.shield_active:
                    return "colliding_blocking"
                elif hasattr(target, 'incoming_attack') and target.incoming_attack:
                    return "colliding_attacking"
                else:
                    return "colliding_idle"
            else:
                # Close but not colliding - check player action
                if hasattr(target, 'is_jumping') and target.is_jumping:
                    return "close_jumping"
                elif hasattr(target, 'shield_active') and target.shield_active:
                    return "close_blocking"
                elif hasattr(target, 'incoming_attack') and target.incoming_attack:
                    return "close_attacking"
                else:
                    return "close_idle"
    
    def _calculate_action_weights(self, player_state):
        """Calculate weighted probabilities based on player state and difficulty"""
        base_weights = self.chosing_states_weights[player_state]
        
        # Get difficulty multiplier based on stage
        # Higher stages are more aggressive and reactive
        stage_multiplier = 1.0 + (self.stage_num * 0.15)
        
        # Apply stage multiplier to weights (more aggressive = higher attack/shield weights)
        adjusted_weights = list(base_weights)
        adjusted_weights[5] = int(adjusted_weights[5] * stage_multiplier)  # attack weight
        adjusted_weights[4] = int(adjusted_weights[4] * stage_multiplier)  # shield weight
        
        return adjusted_weights
    
    def _choose_action(self, weights):
        """Choose an action based on weighted probabilities"""
        total_weight = sum(weights)
        if total_weight == 0:
            return "idle"
        
        choice = random.randint(0, total_weight - 1)
        cumulative = 0
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if choice < cumulative:
                return self.chosing_states[i]
        
        return self.chosing_states[0]
    
    def ai(self, target, width):
        """AI movement logic with state-based decisions"""
        distance = target.damage_rect.centerx - self.damage_rect.centerx
        
        # Decide action every 30 frames for smoother gameplay
        if self.decision_timer <= 0:
            player_state = self._get_player_state(target)
            weights = self._calculate_action_weights(player_state)
            self.current_action = self._choose_action(weights)
            self.decision_timer = 30
        
        # Execute the chosen action
        if self.current_action == "move_towards":
            if distance > 0:
                self.damage_rect.x += self.speed
                self.attack_rect.x += self.speed
                self.facing = -1
            else:
                self.damage_rect.x -= self.speed
                self.attack_rect.x -= self.speed
                self.facing = 1
        
        elif self.current_action == "move_away":
            if distance > 0:
                self.damage_rect.x -= self.speed
                self.attack_rect.x -= self.speed
                self.facing = 1
            else:
                self.damage_rect.x += self.speed
                self.attack_rect.x += self.speed
                self.facing = -1
        
        elif self.current_action == "jump":
            self.jump()
        
        elif self.current_action == "shield":
            self.shield()
        
        elif self.current_action == "attack":
            if self.attack_cooldown == 0:  # Only attack when not in cooldown
                attack_type = random.choice(list(self.ATTACKS.keys()))
                self._prepare_attack(attack_type)
        
        # Keep enemy in bounds
        self.damage_rect.x = max(0, min(width - self.damage_rect.width, self.damage_rect.x))
        self.attack_rect.x = max(0, min(width - self.attack_rect.width, self.attack_rect.x))
        
        # Execute telegraphed attack when telegraph ends
        if self.telegraph_cooldown <= 0 and self.incoming_attack:
            self._execute_attack(target, self.incoming_attack)
            self.incoming_attack = None
            self.incoming_attack_symbol = None
    
    def _prepare_attack(self, attack_type):
        """Prepare attack with telegraph"""
        if self.attack_cooldown == 0:
            self.incoming_attack = attack_type
            self.incoming_attack_symbol = self.ATTACKS[attack_type]["symbol"]
            self.telegraph_cooldown = self.ATTACKS[attack_type]["telegraph_time"]
            self.attack_cooldown = self.ATTACKS[attack_type]["cooldown"]  # Set cooldown immediately
    
    def _execute_attack(self, target, attack_type):
        """Execute the telegraphed attack - use attack_rect for hit detection and target's damage_rect for damage"""
        if self.attack_rect.colliderect(target.damage_rect):
            #add critical hit chance
            is_critical = random.random() < self.crit_addition
            if is_critical:
                print("Enemy landed a critical hit!")
                damage = int(self.ATTACKS[attack_type]["damage"] * self.damage_multiplier * (self.crit_addition + 1))
            else:
                print("Enemy landed a normal hit.")
                damage = int(self.ATTACKS[attack_type]["damage"] * self.damage_multiplier)
            target.take_damage(damage, can_block=True)
    
    def take_damage(self, damage, can_block=False):
        """Take damage from player"""
        return super().take_damage(damage/self.STAGES[self.stage_name]["resistance"])
    
    
    def update(self):
        """Update cooldowns and timers"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.telegraph_cooldown > 0:
            self.telegraph_cooldown -= 1
        if self.decision_timer > 0:
            self.decision_timer -= 1
        
        # Shield management
        if self.shield_active:
            self.shield_duration -= 1
            if self.shield_duration <= 0:
                self.shield_active = False
        
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1

    def apply_gravity(self, floor_y):
        """Apply gravity and update vertical position"""
        self.velocity_y += self.gravity
        self.damage_rect.y += self.velocity_y
        self.attack_rect.y += self.velocity_y
        
        # Check if landed on floor
        if self.damage_rect.bottom >= floor_y:
            self.damage_rect.bottom = floor_y
            self.attack_rect.bottom = floor_y
            self.velocity_y = 0
            self.is_jumping = False
    
    def jump(self):
        """Make enemy jump"""
        if not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True
    
    def shield(self):
        """Activate shield"""
        if self.shield_cooldown <= 0 and not self.shield_active:
            self.shield_active = True
            self.shield_duration = self.max_shield_duration
            self.shield_cooldown = self.max_shield_cooldown
    
