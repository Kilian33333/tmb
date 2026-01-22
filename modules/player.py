"""Player character with multiple attacks and blocking"""
import pygame
from .fighter import Fighter


class Player(Fighter):
    # Attack types with their properties
    ATTACKS = {
        "slash": {"damage": 12, "cooldown": 30, "symbol": "⚔"},
        "thrust": {"damage": 15, "cooldown": 45, "symbol": "→"},
        "spin": {"damage": 10, "cooldown": 25, "symbol": "⊙"},
    }
    
    def __init__(self, x, color=(50, 100, 255), health=120, strength=12):
        super().__init__(x, color, health, strength)
        self.rect = pygame.Rect(x, 240, 100, 160)  # FLOOR_Y - 160 (2x bigger)
        self.attack_cooldown = 0
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
        self.floor_y = 240
        
    def draw(self, screen):
        """Draw player with health indicator"""
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw block indicator if active
        if self.block_active:
            pygame.draw.rect(screen, (100, 200, 100), self.rect, 5)
    
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
        """Perform an attack on target"""
        if self.attack_cooldown == 0 and attack_type in self.ATTACKS:
            if self.rect.colliderect(target.rect.inflate(20, 0)):
                damage = self.ATTACKS[attack_type]["damage"]
                target.take_damage_from_player(damage, attack_type)
            self.attack_cooldown = self.ATTACKS[attack_type]["cooldown"]
            self.current_attack_type = attack_type
    
    def block(self, keys):
        """Toggle block (SHIFT key)"""
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.block_active = True
        else:
            self.block_active = False
    
    def take_damage_from_player(self, damage, attack_type):
        """Placeholder - overridden in subclasses"""
        pass
    
    def take_damage(self, damage, can_block=True):
        """Take damage with resistance and block chance"""
        if self.block_active and can_block:
            damage = int(damage * 0.3)  # Block reduces damage to 30%
        
        # Apply resistance
        actual_damage = int(damage * self.resistance)
        return super().take_damage(actual_damage)
    
    def update(self):
        """Update cooldowns and status"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.block_cooldown > 0:
            self.block_cooldown -= 1
