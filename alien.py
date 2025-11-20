import pygame
from pygame.sprite import Sprite
import random
from alien_bullet import AlienBullet

class Alien(Sprite):
    """A class to represent a single alien in the fleet."""

    def __init__(self, ai_game):
        """Initialize the alien and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load the alien image and set attributes
        self.image = pygame.image.load('images/alien.bmp')
        self.rect = self.image.get_rect()

        # Start each new alien near the top left of the screen
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store the alien's exact horizontal position
        self.x = float(self.rect.x)

        # Reference to main game for bullet spawning
        self.ai_game = ai_game
        
        # Shooting mechanics
        self.last_shot_time = 0
        self.burst_count = 0
        self.burst_timer = 0

    def update(self):
        """Move the alien right or left."""
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x

        # Enhanced shooting mechanics
        current_time = pygame.time.get_ticks()
        
        # Check for burst firing
        if self.burst_count > 0:
            if current_time - self.burst_timer > 200:  # 200ms between burst shots
                self._fire_bullet()
                self.burst_count -= 1
                self.burst_timer = current_time
        else:
            # Regular shooting with dynamic fire rate
            fire_chance = self.settings.alien_fire_rate
            
            # Increase fire chance for bottom row aliens
            if self.rect.bottom > self.screen.get_rect().height * 0.7:
                fire_chance *= 2
                
            # Random chance to fire
            if random.random() < fire_chance:
                if len(self.ai_game.alien_bullets) < self.settings.alien_bullets_allowed:
                    # 30% chance for burst fire (3 shots)
                    if random.random() < 0.3:
                        self.burst_count = 2  # 3 total shots (1 now + 2 in burst)
                        self.burst_timer = current_time
                    
                    self._fire_bullet()
                    self.last_shot_time = current_time
    
    def _fire_bullet(self):
        """Fire a single bullet."""
        self.ai_game.alien_bullets.add(AlienBullet(self.ai_game, self))

    def check_edges(self):
        """Return True if alien is at screen edge."""
        screen_rect = self.screen.get_rect()
        return self.rect.right >= screen_rect.right or self.rect.left <= 0
