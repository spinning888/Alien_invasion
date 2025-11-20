import pygame
from pygame.sprite import Sprite
import math

class Shield(Sprite):
    """A class to represent a shield that protects the ship."""

    def __init__(self, ai_game, ship):
        """Initialize the shield and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.ship = ship  # Reference to ship for following
        
        # Shield dimensions and appearance
        self.radius = 60  # Circular shield radius
        self.thickness = 8
        self.base_color = (0, 150, 255)  # Blue energy color
        self.pulse_speed = 0.1
        self.pulse_offset = 0
        
        # Create shield rect for collision detection
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.update_position()
        
        # Shield health
        self.max_health = 150
        self.health = self.max_health
        
        # Visual effects
        self.alpha = 180  # Semi-transparent
        self.energy_particles = []
        
    def update_position(self):
        """Update shield position to follow the ship."""
        self.rect.centerx = self.ship.rect.centerx
        self.rect.centery = self.ship.rect.centery - 10  # Slightly above ship
        
    def update(self):
        """Update shield animation and position."""
        self.update_position()
        self.pulse_offset += self.pulse_speed
        
        # Update energy particles
        self.update_particles()
        
    def update_particles(self):
        """Update energy particles around the shield."""
        # Add new particles occasionally
        if len(self.energy_particles) < 12 and pygame.time.get_ticks() % 5 == 0:
            angle = pygame.time.get_ticks() * 0.01 + len(self.energy_particles) * 0.5
            particle = {
                'angle': angle,
                'distance': self.radius - 15,
                'life': 30
            }
            self.energy_particles.append(particle)
            
        # Update existing particles
        for particle in self.energy_particles[:]:
            particle['angle'] += 0.05
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.energy_particles.remove(particle)

    def hit(self, damage=20):
        """Reduce shield health and create damage effect."""
        self.health -= damage
        
        # Visual feedback for damage
        self.alpha = max(50, self.alpha - 20)  # Reduce opacity when damaged
        
        if self.health <= 0:
            self.kill()  # Remove shield when destroyed
            return True
        return False

    def draw(self):
        """Draw the shield with energy field effect."""
        if self.health <= 0:
            return
            
        # Calculate pulsing effect
        pulse = math.sin(self.pulse_offset) * 0.3 + 0.7
        current_radius = int(self.radius * pulse)
        
        # Calculate health-based alpha
        health_ratio = self.health / self.max_health
        current_alpha = int(self.alpha * health_ratio)
        
        # Create surface for drawing with alpha
        shield_surface = pygame.Surface((self.radius * 2 + 20, self.radius * 2 + 20), pygame.SRCALPHA)
        
        # Draw main shield circle with gradient effect
        for i in range(self.thickness):
            radius = current_radius - i * 2
            alpha = current_alpha - i * 20
            if radius > 0 and alpha > 0:
                color = (*self.base_color, max(0, alpha))
                center = (self.radius + 10, self.radius + 10)
                pygame.draw.circle(shield_surface, color, center, radius, 2)
        
        # Draw energy particles
        for particle in self.energy_particles:
            if particle['life'] > 0:
                angle = particle['angle']
                distance = particle['distance']
                x = int(self.radius + 10 + math.cos(angle) * distance)
                y = int(self.radius + 10 + math.sin(angle) * distance)
                
                particle_alpha = int(255 * (particle['life'] / 30) * health_ratio)
                if particle_alpha > 0:
                    color = (*self.base_color, particle_alpha)
                    pygame.draw.circle(shield_surface, color, (x, y), 2)
        
        # Draw inner glow
        inner_color = (*self.base_color, int(current_alpha * 0.3))
        center = (self.radius + 10, self.radius + 10)
        pygame.draw.circle(shield_surface, inner_color, center, current_radius - self.thickness, 0)
        
        # Blit to main screen
        shield_rect = shield_surface.get_rect()
        shield_rect.center = self.rect.center
        self.screen.blit(shield_surface, shield_rect)
        
        # Draw health indicator
        self.draw_health_bar()
        
    def draw_health_bar(self):
        """Draw a small health bar above the shield."""
        bar_width = 40
        bar_height = 4
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 15
        
        # Background (red)
        pygame.draw.rect(self.screen, (100, 0, 0), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Health (blue gradient)
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        if health_width > 0:
            color = (int(255 * (1 - health_ratio)), int(100 * health_ratio), int(255 * health_ratio))
            pygame.draw.rect(self.screen, color, 
                            (bar_x, bar_y, health_width, bar_height))