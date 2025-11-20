class Settings:
    """A class to store all settings for Alien Invasion."""

    def __init__(self):
        """Initialize the game's static settings."""
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # Ship settings
        self.ship_speed = 3.0  # Increased from 1.5
        self.ship_limit = 3

        # Bullet settings
        self.bullet_speed = 4.5  # Increased from 2.5
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 5  # Increased from 3 to 5

        # Alien bullet settings
        self.alien_bullet_speed = 3.0  # Increased from 1.5
        self.alien_bullet_width = 3
        self.alien_bullet_height = 15
        self.alien_bullet_color = (255, 0, 0)
        self.alien_bullets_allowed = 12  # Increased from 5 to 12
        self.alien_fire_rate = 0.003  # Base fire probability (increased from 0.0005)

        # Alien settings
        self.alien_speed = 2.0  # Increased from 1.0
        self.fleet_drop_speed = 20  # Increased from 10

        # Shield skill settings
        self.shield_duration = 8000  # 8 seconds duration
        self.shield_cooldown = 3000  # 3 seconds cooldown (shorter for testing)
        self.shield_health = 150

        # How quickly the game speeds up
        self.speedup_scale = 1.2  # Increased from 1.1 for faster progression
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initialize settings that change through the game."""
        self.ship_speed = 3.0  # Increased from 1.5
        self.bullet_speed = 4.5  # Increased from 3.0
        self.alien_speed = 2.0  # Increased from 1.0
        self.alien_fire_rate = 0.003  # Reset fire rate

        # fleet direction: 1 means right; -1 means left
        self.fleet_direction = 1

        # Scoring
        self.alien_points = 50

    def increase_speed(self):
        """Increase speed settings and alien points."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_bullet_speed *= self.speedup_scale
        
        # Increase alien fire rate as game progresses
        self.alien_fire_rate = min(0.008, self.alien_fire_rate * 1.2)

        self.alien_points = int(self.alien_points * self.speedup_scale)
