"""Player character with multiple attacks and blocking"""
import pygame
from .fighter import Fighter


class Player(Fighter):
    # Attack types with their properties
    ATTACKS = {
        "Front Kick": {"damage": 25, "cooldown": 30, "symbol": "1"},
        "High Kick": {"damage": 40, "cooldown": 45, "symbol": "2"},
        "Upward swing": {"damage": 55, "cooldown": 80, "symbol": "3"},
        "Side head strike": {"damage": 50, "cooldown": 70, "symbol": "4"},
        "Direct Punch": {"damage": 3, "cooldown": 7, "symbol": "5"},
        "Ultimate": {"damage": 95, "cooldown": 150, "symbol": "6"},
    }
    
    def __init__(self, x, color=(50, 100, 255), health=120, strength=12):
        super().__init__(x, color, health, strength)
        self.rect = pygame.Rect(x, 170, 140, 198)  # 99:70 ratio, bigger size
        self.attack_cooldown = 0
        self.max_attack_cooldown = 0  # Track max for cooldown bar
        self.current_attack_type = "slash"
        self.block_active = False
        self.block_cooldown = 0
        self.resistance = 0.7  # Takes 70% of damage (30% resistance)
        self.can_block_attacks = ["slash", "thrust", "spin"]
        # Jump mechanics
        self.velocity_y = 0
        self.is_jumping = False
        self.jump_power = -15
        self.gravity = 0.5
        self.floor_y = 500
        
    def draw(self, screen):
        """Draw player with health indicator and cooldown bar"""
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw block indicator if active
        if self.block_active:
            pygame.draw.rect(screen, (100, 200, 100), self.rect, 5)
        
        # Draw cooldown bar above player
        if self.max_attack_cooldown > 0:
            bar_width = 80
            bar_height = 8
            bar_x = self.rect.centerx - bar_width // 2
            bar_y = self.rect.top - 20
            
            # Red background
            pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # Green progress
            progress = (self.max_attack_cooldown - self.attack_cooldown) / self.max_attack_cooldown
            pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, bar_width * progress, bar_height))
    
    def move(self, keys, width, floor_y):
        """Move player with keyboard input and jumping"""
        if keys[pygame.K_a]:
            self.rect.x = max(0, self.rect.x - self.speed)
        if keys[pygame.K_d]:
            self.rect.x = min(width - self.rect.width, self.rect.x + self.speed)
        
        # Jumping with SPACE
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True
    
    def apply_gravity(self, floor_y):
        """Apply gravity and update vertical position"""
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        
        # Check if landed on floor
        if self.rect.bottom >= floor_y:
            self.rect.bottom = floor_y
            self.velocity_y = 0
            self.is_jumping = False
    
    def attack(self, target, attack_type="slash"):
        """Perform an attack on target - cooldown FIRST, then deal damage"""
        if self.attack_cooldown == 0 and attack_type in self.ATTACKS:
            self.current_attack_type = attack_type
            # Start cooldown FIRST (animation time)
            self.attack_cooldown = self.ATTACKS[attack_type]["cooldown"]
            self.max_attack_cooldown = self.attack_cooldown
            # After cooldown reaches a certain point, deal damage (2/3 through cooldown)
            self.damage_dealt = False
            self.damage_delay = int(self.ATTACKS[attack_type]["cooldown"] * 0.66)
    
    def block(self, keys):
        """Toggle block (SHIFT key)"""
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.block_active = True
        else:
            self.block_active = False
    
    def take_damage(self, damage, can_block=True):
        """Take damage with resistance and block chance"""
        if self.block_active and can_block:
            damage = int(damage * 0.3)  # Block reduces damage to 30%
        
        # Apply resistance
        actual_damage = int(damage * self.resistance)
        # Ensure at least 1 damage when an attack would otherwise deal 0
        if damage > 0 and actual_damage == 0:
            actual_damage = 1
        new_health = super().take_damage(actual_damage)
        print(f"Player.take_damage: incoming={damage}, after_resist={actual_damage}, new_health={new_health}")
        return new_health
    
    def update(self):
        """Update cooldowns and status"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            # Deal damage when delay is reached
            if hasattr(self, 'damage_delay') and self.attack_cooldown == self.damage_delay:
                self.damage_dealt = True
        if self.block_cooldown > 0:
            self.block_cooldown -= 1
