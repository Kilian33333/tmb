"""Base Fighter class for common attributes and methods"""

class Fighter:
    def __init__(self, x, color, health=100, strength=10, speed=4):
        self.rect = None  # Will be set by subclass
        self.color = color
        self.health = health
        self.max_health = health
        self.strength = strength
        self.speed = speed
        self.x = x
        
    def draw(self, screen):
        """Draw the fighter on screen"""
        raise NotImplementedError("Subclasses must implement draw()")
    
    def take_damage(self, damage):
        """Take damage and return remaining health"""
        self.health = max(0, self.health - damage)
        return self.health
    
    def is_alive(self):
        """Check if fighter is still alive"""
        return self.health > 0
    
