"""Player character with multiple attacks and blocking"""
import pygame
import os

from modules import screenSet
from .fighter import Fighter
screen = screenSet.screen
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
        "Ultimate": {"damage": 70, "cooldown": 300, "symbol": "6"},
    }
    
    # Animation frame counts for different actions
    ANIMATION_FRAMES = {
        "idle": {"frames": 2, "duration": 10, "does_loop": True},
        "front_kick": {"frames": 6, "duration": 2, "does_loop": False},
        "jump": {"frames": 3, "duration": 6, "does_loop": False},
        "block": {"frames": 1, "duration": 1, "does_loop": False},
        "walk": {"frames": 5, "duration": 8, "does_loop": True},
    }
    
    def __init__(self, x, color=(50, 100, 255), health=100, strength=12):
        super().__init__(x, color, health, strength)
        # Damage hitbox (where player takes damage)
        self.damage_rect = pygame.Rect(x, 170, 120, 198)
        # Attack hitbox (where player deals damage)
        self.attack_rect = pygame.Rect(x, 170, 198, 198)
        # For backwards compatibility
        self.rect = self.damage_rect
        
        # Animation system
        self.animations = {}  # Store all loaded animations
        self.current_action = "idle"  # Current action state
        self.animation_frame = 0  # Current frame index
        self.animation_counter = 0  # Counter for frame timing
        self.image = None
        
        # Load all animations
        self.load_animations()

        self.attack_cooldown = 0
        self.max_attack_cooldown = 0  # Track max for cooldown bar
        self.current_attack_type = "Direct Punch"
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
        self.ultimate_charge = 20
        self.resist = False
        self.damage_freeze_timer = 0  # Prevents damage for 20 ticks after enemy dies
    
    def load_animations(self):
        """Load all animation frames from src folder"""
        animation_types = ["idle", "front_kick", "jump", "block", "walk"]
        
        for anim_type in animation_types:
            self.animations[anim_type] = []
            frame_count = self.ANIMATION_FRAMES[anim_type]["frames"]
            
            # Try to load frames for this animation
            for frame_num in range(frame_count):
                filename = f"src/player_{anim_type}_{frame_num}.png"
                try:
                    if os.path.exists(filename):
                        img = pygame.image.load(filename).convert_alpha()
                        img = pygame.transform.scale(img, (198, 198))
                        self.animations[anim_type].append(img)
                    else:
                        print(f"Animation frame not found: {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
            
            # If no frames loaded, use a placeholder
            if not self.animations[anim_type]:
                print(f"Warning: No frames loaded for {anim_type} animation")
                self.animations[anim_type] = [None]
        
        # Set initial image
        if self.animations["idle"]:
            self.image = self.animations["idle"][0]
    
    def update_animation(self):
        """Update animation frame based on current action"""
        action = self.current_action
        
        if action not in self.animations:
            return
        
        frames = self.animations[action]
        if not frames:
            return
        
        animation_duration = self.ANIMATION_FRAMES[action]["duration"]
        self.animation_counter += 1
        
        # Change frame based on animation duration
        if self.animation_counter >= animation_duration:
            self.animation_counter = 0
            self.animation_frame += 1
            
            # Loop animation or stop at last frame
            if self.animation_frame >= len(frames):
                if self.ANIMATION_FRAMES[action]["does_loop"]:
                    # Loop animation
                    self.animation_frame = 0
                else:
                    # Non-looping animation: stay on last frame unless landing
                    if not self.is_jumping:
                        self.current_action = "idle"
                    self.animation_frame = len(frames) - 1
        
        # Get current frame image
        current_frame_index = min(self.animation_frame, len(frames) - 1)
        if frames[current_frame_index]:
            self.image = frames[current_frame_index]
    
    def set_animation(self, action):
        """Set the current animation action"""
        if action != self.current_action:
            self.current_action = action
            self.animation_frame = 0
            self.animation_counter = 0

        
    def draw(self, screen):
        """Draw player image with health indicator and cooldown bar"""
        # Draw player image based on facing direction
        if self.image:
            img_to_draw = self.image
            if self.facing == -1:  # Facing right, character on right side of image
                self.attack_rect.x = self.damage_rect.x
                img_x = self.damage_rect.x
            else:  # Facing left (facing == 1), image extends left, flip image
                img_x = self.damage_rect.x - (198/2)
                img_to_draw = pygame.transform.flip(self.image, True, False)
                self.attack_rect.x = self.damage_rect.x - (78)
            
            img_y = self.damage_rect.y
            screen.blit(img_to_draw, (img_x, img_y))
        else:
            # Fallback to colored rect if image not loaded
            pygame.draw.rect(screen, self.color, self.damage_rect)
        
        # Draw block indicator if active
        if self.block_active:
            pygame.draw.rect(screen, (100, 200, 100), self.damage_rect, 5)
        
        # Draw cooldown bar above player
        if self.max_attack_cooldown > 0:
            bar_width = 80
            bar_height = 8
            bar_x = self.damage_rect.centerx - bar_width // 2
            bar_y = self.damage_rect.top - 20
            
            # Red background
            pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # Green progress
            progress = (self.max_attack_cooldown - self.attack_cooldown) / self.max_attack_cooldown
            pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, bar_width * progress, bar_height))
    
    def move(self, keys, width, floor_y):
        """Move player with keyboard input and jumping"""
        is_moving = False
        if self.attack_cooldown == 0 or self.current_attack_type == "Direct Punch":
            if keys[pygame.K_a]:
                self.damage_rect.x = max(0, self.damage_rect.x - self.speed)
                self.attack_rect.x = max(0, self.attack_rect.x - self.speed)
                self.facing = 1
                if self.current_action != "walk" and not self.is_jumping:
                    self.set_animation("walk")
                is_moving = True
            if keys[pygame.K_d]:
                self.damage_rect.x = min(width - self.damage_rect.width, self.damage_rect.x + self.speed)
                self.attack_rect.x = min(width - self.attack_rect.width, self.attack_rect.x + self.speed)
                self.facing = -1
                if self.current_action != "walk" and not self.is_jumping:
                    self.set_animation("walk")
                is_moving = True
        
        # Return to idle if not moving
        if not is_moving and self.current_action == "walk" and not self.is_jumping:
            self.set_animation("idle")
        
        # Jumping with SPACE
        if keys[pygame.K_SPACE] and not self.is_jumping:
            if self.attack_cooldown == 0:
                self.velocity_y = self.jump_power
                self.is_jumping = True
                self.rush_kick_used_this_jump = False
                self.set_animation("jump")
    
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
            self.rush_kick_used_this_jump = False
            # Return to idle animation when landing
            if self.current_action == "jump":
                self.set_animation("idle")
    
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
            
            # Trigger attack animation
            if self.current_attack_type == "Front Kick" or self.current_attack_type == "Rush Kick":
                self.set_animation("front_kick")
    
    @property
    def image_rect(self):
        """Return the rect of where the image is actually drawn"""
        if self.facing == -1:  # Facing right, character on right side of image
            img_x = self.damage_rect.x
        else:  # Facing left (facing == 1), image extends left
            img_x = self.damage_rect.x - 198
        img_y = self.damage_rect.y
        return pygame.Rect(img_x, img_y, 198, 198)
    
    def block(self, keys):
        """Toggle block (SHIFT key)"""
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.attack_cooldown == 0:
            self.block_active = True
            if self.current_action != "block":
                self.set_animation("block")
        else:
            self.block_active = False
            if self.current_action == "block":
                self.set_animation("idle")
    
    def take_damage(self, damage, can_block=True):
        """Take damage with resistance and block chance"""
        # Check if damage is frozen (after enemy dies)
        if self.damage_freeze_timer > 0:
            return self.health
        
        if self.block_active and can_block:
            damage = int(damage * 0.3)
        elif self.resist:
            damage = int(damage * 0.1)
        
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
        if self.damage_freeze_timer > 0:
            self.damage_freeze_timer -= 1
        
        # Update animations
        self.update_animation()
        
        # Return to idle if attack finishes
        if self.current_action == "attack" and self.attack_cooldown == 0:
            if self.is_jumping:
                self.set_animation("jump")
            else:
                self.set_animation("idle")
