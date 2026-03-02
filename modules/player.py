"""Player character with multiple attacks and blocking"""
import pygame
from .fighter import Fighter
clock = pygame.time.Clock()

class Player(Fighter):
    # Attack types with their properties
    ATTACKS = {
        "Front Kick": {"damage": 25, "cooldown": 60, "symbol": "1"},
        "Rush Kick": {"damage": 25, "cooldown": 5, "symbol": "1.1"},
        "High Kick": {"damage": 40, "cooldown": 90, "symbol": "2"},
        "Upward swing": {"damage": 55, "cooldown": 160, "symbol": "3"},
        "Side head strike": {"damage": 50, "cooldown": 140, "symbol": "4"},
        "Direct Punch": {"damage": 3, "cooldown": 14, "symbol": "5"},
        "Ultimate": {"damage": 95, "cooldown": 300, "symbol": "6"},
    }
    
    def __init__(self, x, color=(50, 100, 255), health=100, strength=12):
        super().__init__(x, color, health, strength)
        self.rect = pygame.Rect(x, 170, 140, 198)  # 99:70 ratio, bigger size
        self.attack_cooldown = 0
        self.max_attack_cooldown = 0  # Track max for cooldown bar
        self.current_attack_type = "slash"
        self.block_active = False
        self.block_cooldown = 0
        self.resistance = 0.7
        self.can_block_attacks = ["slash", "thrust", "spin"]
        # Jump mechanics
        self.velocity_y = 0
        self.is_jumping = False
        self.jump_power = -15
        self.gravity = 0.5
        self.floor_y = 500
        self.rush_kick_used_this_jump = False
        self.facing = -1

        
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
        if self.attack_cooldown == 0 or self.current_attack_type == "Direct Punch":
            if keys[pygame.K_a]:
                self.rect.x = max(0, self.rect.x - self.speed)
                self.facing = 1
            if keys[pygame.K_d]:
                self.rect.x = min(width - self.rect.width, self.rect.x + self.speed)
                self.facing = -1
        
        # Jumping with SPACE
        if keys[pygame.K_SPACE] and not self.is_jumping:
            if self.attack_cooldown == 0:
                self.velocity_y = self.jump_power
                self.is_jumping = True
                self.rush_kick_used_this_jump = False
    
    def apply_gravity(self, floor_y):
        """Apply gravity and update vertical position"""
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        
        # Check if landed on floor
        if self.rect.bottom >= floor_y:
            self.rect.bottom = floor_y
            self.velocity_y = 0
            self.is_jumping = False
            self.rush_kick_used_this_jump = False
    
    def attack(self, target, attack_type="slash"):
        """Perform an attack on target - cooldown FIRST, then deal damage"""
        if attack_type == "Rush Kick" and self.is_jumping and self.rush_kick_used_this_jump:
            return
        
        if self.attack_cooldown == 0 and attack_type in self.ATTACKS:
            if attack_type == "Rush Kick" and self.is_jumping:
                self.rush_kick_used_this_jump = True
            
            self.current_attack_type = attack_type
            self.attack_cooldown = self.ATTACKS[attack_type]["cooldown"]
            self.max_attack_cooldown = self.attack_cooldown
            self.damage_dealt = False
            self.damage_delay = int(self.ATTACKS[attack_type]["cooldown"] * 0.66)
    
    def block(self, keys):
        """Toggle block (SHIFT key)"""
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.attack_cooldown == 0:
            self.block_active = True
        else:
            self.block_active = False
    
    def take_damage(self, damage, can_block=True):
        """Take damage with resistance and block chance"""
        if self.block_active and can_block:
            damage = int(damage * 0.3)
        
        actual_damage = int(damage * self.resistance)
        if damage > 0 and actual_damage == 0:
            actual_damage = 1
        return super().take_damage(actual_damage)
    
    def update(self):
        """Update cooldowns and status"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            if hasattr(self, 'damage_delay') and self.attack_cooldown == self.damage_delay:
                self.damage_dealt = True
        if self.block_cooldown > 0:
            self.block_cooldown -= 1
