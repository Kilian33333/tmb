"""Enemy AI with multiple attacks and attack telegraph"""
import pygame
import random
from .fighter import Fighter


class Enemy(Fighter):
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
        scale = 1 + (self.fight_number * 0.15)
        self.strength = int(self.strength * scale)
        self.health = int(self.health * scale)
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
