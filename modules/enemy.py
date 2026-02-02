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
        "recruits": {"damage_multiplier": 0.8, "resistance": 0.9, "speed_multiplier": 1.1, "crit_chance": 0, "crit_addition": 0},
        "heavy_recruits": {"damage_multiplier": 0.9, "resistance": 0.95, "speed_multiplier": 1.0, "crit_chance": 5, "crit_addition": 5},
        "heavy_knight": {"damage_multiplier": 1.0, "resistance": 1.0, "speed_multiplier": 1.0, "crit_chance": 5, "crit_addition": 15},
        "veteran_knight": {"damage_multiplier": 1.25, "resistance": 1.0, "speed_multiplier": 1.0, "crit_chance": 10, "crit_addition": 20},
        "elite_knight": {"damage_multiplier": 1.5, "resistance": 1.5, "speed_multiplier": 0.9, "crit_chance": 10, "crit_addition": 40},
        "magic_knight": {"damage_multiplier": 2.0, "resistance": 2.0, "speed_multiplier": 1.1, "crit_chance": 15, "crit_addition": 60},
        "the_king": {"damage_multiplier": 3.0, "resistance": 3.0, "speed_multiplier": 1.0, "crit_chance": 20, "crit_addition": 100},
    }
    # Attack patterns with damage and symbols
    ATTACKS = {
        "slash": {"damage": 8, "cooldown": 60, "symbol": "⚔", "telegraph_time": 25},
        "smash": {"damage": 12, "cooldown": 80, "symbol": "↓", "telegraph_time": 30},
        "thrust": {"damage": 10, "cooldown": 120, "symbol": "→", "telegraph_time": 28},
    }
    
    def __init__(self, x, color, health=100, strength=8, fight_number=1):
        super().__init__(x, color, health, strength)
        self.rect = pygame.Rect(x, 340, 100, 160)
        self.speed = 3
        self.fight_number = fight_number
        self.attack_cooldown = 0
        self.max_attack_cooldown = 0  # Track max for cooldown bar
        self.telegraph_cooldown = 0
        self.incoming_attack = None
        self.incoming_attack_symbol = None
        self.decision_timer = 0
        
        # Scale difficulty
        self._scale_difficulty()
    
    def _scale_difficulty(self):
        """Scale stats based on fight number"""
        self.strength = int(self.strength)
        self.health = int(self.health)
        self.max_health = self.health
    
    def draw(self, screen):
        """Draw enemy with health bar and attack telegraph"""
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw incoming attack symbol above head
        if self.telegraph_cooldown > 0 and self.incoming_attack_symbol:
            font = pygame.font.SysFont("arial", 40)
            symbol_surf = font.render(self.incoming_attack_symbol, True, (255, 100, 0))
            symbol_rect = symbol_surf.get_rect(center=(self.rect.centerx, self.rect.top - 50))
            screen.blit(symbol_surf, symbol_rect)
            
            # Draw telegraph bar
            bar_width = 100
            bar_height = 8
            bar_x = self.rect.centerx - bar_width // 2
            bar_y = self.rect.top - 30
            
            # Red bar for telegraph
            pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # Green progress
            progress = max(0, self.telegraph_cooldown) / self.ATTACKS[self.incoming_attack]["telegraph_time"]
            pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, bar_width * progress, bar_height))
    
    def ai_move(self, target, width):
        """AI movement logic - move toward target"""
        distance = target.rect.centerx - self.rect.centerx
        
        # Move toward player until within attack range (~40px)
        attack_range = 40
        if distance > attack_range:
            self.rect.x += self.speed
        elif distance < -attack_range:
            self.rect.x -= self.speed
        
        # Keep within bounds
        self.rect.x = max(0, min(width - self.rect.width, self.rect.x))
    
    def ai_attack(self, target):
        """AI decision to attack"""
        if self.decision_timer <= 0:
            # Choose random attack
            attack_type = random.choice(list(self.ATTACKS.keys()))
            self._prepare_attack(attack_type)
            self.decision_timer = 60
        
        # Execute attack if telegraph is done
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
            damage = self.ATTACKS[attack_type]["damage"]
            target.take_damage(damage, can_block=True)
    
    def take_damage(self, damage, can_block=False):
        """Take damage from player"""
        return super().take_damage(damage)
    
    def update(self):
        """Update cooldowns and timers"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.telegraph_cooldown > 0:
            self.telegraph_cooldown -= 1
        if self.decision_timer > 0:
            self.decision_timer -= 1
