"""Enemy AI with multiple attacks and attack telegraph"""
import pygame
import random
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
        "recruits": {"damage_multiplier": 0.8, "resistance": 0.9, "speed_multiplier": 1.1, "crit_chance": 0, "crit_addition": 0, "strength_multiplier": 0, "aggression": 0.6, "defense": 0.3, "shield_freq": 0.2 }, #Strength = knockback
        "heavy_recruits": {"damage_multiplier": 0.9, "resistance": 0.95, "speed_multiplier": 1.0, "crit_chance": 5, "crit_addition": 5, "strength_multiplier": 0, "aggression": 0.7, "defense": 0.4, "shield_freq": 0.3},
        "heavy_knight": {"damage_multiplier": 1.0, "resistance": 1.0, "speed_multiplier": 1.0, "crit_chance": 5, "crit_addition": 15, "strength_multiplier": 0.1, "aggression": 0.75, "defense": 0.5, "shield_freq": 0.4},
        "veteran_knight": {"damage_multiplier": 1.25, "resistance": 1.0, "speed_multiplier": 1.0, "crit_chance": 10, "crit_addition": 20, "strength_multiplier": 0.2, "aggression": 0.8, "defense": 0.6, "shield_freq": 0.5},
        "elite_knight": {"damage_multiplier": 1.5, "resistance": 1.5, "speed_multiplier": 0.9, "crit_chance": 10, "crit_addition": 40, "strength_multiplier": 0.2, "aggression": 0.85, "defense": 0.65, "shield_freq": 0.6},
        "magic_knight": {"damage_multiplier": 2.0, "resistance": 2.0, "speed_multiplier": 1.1, "crit_chance": 15, "crit_addition": 60, "strength_multiplier": 0.5, "aggression": 0.9, "defense": 0.7, "shield_freq": 0.7},
        "the_king": {"damage_multiplier": 3.0, "resistance": 3.0, "speed_multiplier": 1.0, "crit_chance": 20, "crit_addition": 100, "strength_multiplier": 0.6, "aggression": 1.0, "defense": 0.8, "shield_freq": 0.8},
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
        self.rect = pygame.Rect(x, 340, 100, 160)
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
        self.max_shield_duration = 60
        self.max_shield_cooldown = 120

        # Scale difficulty
        self._scale_difficulty()
    
    def _scale_difficulty(self):
        """Scale stats based on fight number and stage multipliers"""
        stage_multipliers = self.STAGES[self.stage_name]
        
        self.strength = int(self.strength * (1 + stage_multipliers["strength_multiplier"]))
        self.speed = int(self.speed * stage_multipliers["speed_multiplier"])
        self.max_health = self.health
        
        self.crit_chance = stage_multipliers["crit_chance"]
        self.crit_addition = stage_multipliers["crit_addition"]
        self.damage_multiplier = stage_multipliers["damage_multiplier"]
        self.resistance = stage_multipliers["resistance"]
        self.speed_multiplier = stage_multipliers["speed_multiplier"]
        self.strength_multiplier = stage_multipliers["strength_multiplier"]
        
        # Behavior multipliers
        self.aggression = stage_multipliers["aggression"]
        self.defense = stage_multipliers["defense"]
        self.shield_freq = stage_multipliers["shield_freq"]
    
    def draw(self, screen):
        """Draw enemy with health bar and attack telegraph"""
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw shield if active
        if self.shield_active:
            pygame.draw.rect(screen, (100, 150, 255), self.rect, 3)
        
        if self.telegraph_cooldown > 0 and self.incoming_attack_symbol:
            font = pygame.font.SysFont("arial", 40)
            symbol_surf = font.render(self.incoming_attack_symbol, True, (255, 100, 0))
            symbol_rect = symbol_surf.get_rect(center=(self.rect.centerx, self.rect.top - 50))
            screen.blit(symbol_surf, symbol_rect)
            
            bar_width = 100
            bar_height = 8
            bar_x = self.rect.centerx - bar_width // 2
            bar_y = self.rect.top - 30
            
            pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # Green progress
            progress = max(0, self.telegraph_cooldown) / self.ATTACKS[self.incoming_attack]["telegraph_time"]
            pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, bar_width * progress, bar_height))
    
    def ai_move(self, target, width):
        """AI movement logic - move toward target"""
        distance = target.rect.centerx - self.rect.centerx
        
        attack_range = 40
        if distance > attack_range:
            self.rect.x += self.speed
            self.facing = -1
        elif distance < -attack_range:
            self.rect.x -= self.speed
            self.facing = 1
        
        self.rect.x = max(0, min(width - self.rect.width, self.rect.x))
    
    def ai_attack(self, target):
        """AI decision to attack"""
        if self.decision_timer <= 0:
            attack_type = random.choice(list(self.ATTACKS.keys()))
            self._prepare_attack(attack_type)
            self.decision_timer = 60
        
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
        """Execute the telegraphed attack"""
        if self.rect.colliderect(target.rect.inflate(20, 0)):
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
        self.rect.y += self.velocity_y
        
        # Check if landed on floor
        if self.rect.bottom >= floor_y:
            self.rect.bottom = floor_y
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
    
    def ai_think(self, player, width):
        """
        SCAFFOLD: Implement stage-oriented AI behavior here.
        Called once per frame in game loop.
        
        Use behavior multipliers:
        - self.aggression: controls attack frequency 
        - self.defense: controls defensive maneuvers
        - self.shield_freq: controls shield usage
        
        Available actions:
        - self.ai_move(player, width)
        - self.ai_attack(player)
        - self.jump()
        - self.shield()
        """
        # TODO: Implement AI decision logic
        pass