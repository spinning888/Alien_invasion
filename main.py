import sys
from time import sleep
import random

import json

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from alien_bullet import AlienBullet
from shield import Shield


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        pygame.mixer.init()

        # Load sounds with error handling
        try:
            self.shoot_sound = pygame.mixer.Sound('sounds/shoot.wav')
            self.explosion_sound = pygame.mixer.Sound('sounds/explosion.wav')
        except (pygame.error, FileNotFoundError):
            # Create dummy sound objects if files don't exist
            self.shoot_sound = None
            self.explosion_sound = None
            
        self.alien_bullets = pygame.sprite.Group()  # new bullets for aliens

        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        # Create an instance to store game statistics,
        #   and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)

        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.shields = pygame.sprite.Group()

        # Shield skill system
        self.shield_active = False
        self.shield_start_time = 0
        self.shield_last_used = 0
        
        # Ship crash animation
        self.ship_crashing = False
        self.crash_start_time = 0
        self.crash_particles = []
        self.ship_alpha = 255  # Ship transparency
        self.crash_delay_active = False
        self.crash_delay_start = 0
        
        self._create_fleet()

        # Start Alien Invasion in an inactive state.
        self.game_active = False

        # Make the Play button.
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.game_active:
                if not self.crash_delay_active:
                    self.ship.update()
                    self._update_bullets()
                    self._update_aliens()
                    self._update_shield_skill()
                self._update_crash_animation()
                self._update_crash_delay()

            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)


    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()

            # Reset the game statistics.
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()
            self.alien_bullets.empty()
            self.shields.empty()

            # Reset shield skill
            self.shield_active = False
            self.shield_start_time = 0
            self.shield_last_used = 0
            
            # Reset crash animation states
            self.ship_crashing = False
            self.crash_start_time = 0
            self.crash_particles.clear()
            self.ship_alpha = 255
            self.crash_delay_active = False
            self.crash_delay_start = 0

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            self._save_high_score()
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
            self._activate_shield_skill()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
        if self.shoot_sound:
            self.shoot_sound.play()

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()
        self.alien_bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)

        self._check_alien_bullet_ship_collision()
        self._check_bullet_alien_collisions()
        self._check_bullet_shield_collisions()
        self._check_alien_bullet_shield_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
            if self.explosion_sound:
                self.explosion_sound.play()

        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            # Start crash animation
            self._start_ship_crash()
            
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()
            self.alien_bullets.empty()
            self.shields.empty()

            # Deactivate shield skill
            self.shield_active = False
            self.shield_start_time = 0

            # Start delay after crash
            self.crash_delay_active = True
            self.crash_delay_start = pygame.time.get_ticks()
        else:
            # Start final crash animation
            self._start_ship_crash()
            # Delay before game over
            self.crash_delay_active = True
            self.crash_delay_start = pygame.time.get_ticks()

    def _check_alien_bullet_ship_collision(self):
        """Respond to alien bullets hitting the ship."""
        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            self._ship_hit()
        

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and keep adding aliens until there's no room left.
        # Spacing between aliens is one alien width and one alien height.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            # Finished a row; reset x value, and increment y value.
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _save_high_score(self):
        """Save the high score to a file."""
        with open('high_score.json', 'w') as f:
            json.dump(self.stats.high_score, f)

    def _activate_shield_skill(self):
        """Activate shield skill if available."""
        # Only allow activation during active game
        if not self.game_active:
            return
            
        current_time = pygame.time.get_ticks()
        cooldown_remaining = current_time - self.shield_last_used
        
        # Check if skill is on cooldown
        if cooldown_remaining < self.settings.shield_cooldown:
            return
            
        # Check if shield is already active
        if self.shield_active:
            return
            
        # Activate shield skill
        self.shield_active = True
        self.shield_start_time = current_time
        self.shield_last_used = current_time
        
        # Create shields around the ship
        self._create_skill_shields()

    def _update_shield_skill(self):
        """Update shield skill duration and remove expired shields."""
        if not self.shield_active:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Update shield animations and positions
        self.shields.update()
        
        # Check if skill duration has expired
        if current_time - self.shield_start_time >= self.settings.shield_duration:
            self.shield_active = False
            self.shields.empty()

    def _create_skill_shields(self):
        """Create shields around the ship when skill is activated."""
        self.shields.empty()  # Clear any existing shields
        
        # Create a single shield that follows the ship
        shield = Shield(self, self.ship)
        self.shields.add(shield)

    def _start_ship_crash(self):
        """Start the ship crash animation."""
        self.ship_crashing = True
        self.crash_start_time = pygame.time.get_ticks()
        self.ship_alpha = 255
        
        # Play explosion sound if available
        if self.explosion_sound:
            self.explosion_sound.play()
        
        # Create explosion particles
        ship_center = self.ship.rect.center
        for i in range(35):  # More particles for dramatic effect
            angle = random.uniform(0, 2 * 3.14159)  # Random direction
            speed = random.uniform(3, 8)  # Faster particles
            particle = {
                'x': float(ship_center[0]),
                'y': float(ship_center[1]),
                'vel_x': speed * random.uniform(-1, 1) * 2,  # Wider spread
                'vel_y': speed * random.uniform(-1, 1) * 2,
                'color': random.choice([(255, 80, 0), (255, 180, 0), (255, 255, 80), 
                                       (255, 0, 0), (255, 120, 20), (255, 255, 255),
                                       (200, 50, 0), (255, 200, 100)]),  # More colors
                'life': random.randint(60, 120),  # Longer life
                'max_life': random.randint(60, 120),
                'size': random.randint(3, 8)  # Bigger particles
            }
            self.crash_particles.append(particle)
            
    def _update_crash_animation(self):
        """Update crash animation effects."""
        if not self.ship_crashing:
            return
            
        # Gradually fade ship (slower fade)
        fade_speed = 2
        self.ship_alpha = max(0, self.ship_alpha - fade_speed)
        
        # Update particles
        for particle in self.crash_particles[:]:
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            particle['vel_y'] += 0.1  # Gravity effect
            particle['vel_x'] *= 0.985  # Air resistance
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.crash_particles.remove(particle)
                
    def _draw_crash_effects(self):
        """Draw crash animation effects."""
        # Draw explosion particles
        particles_drawn = 0
        for particle in self.crash_particles:
            if particle['life'] > 0:
                alpha_ratio = max(0, particle['life'] / particle['max_life'])
                size = max(1, int(particle['size'] * alpha_ratio))
                
                # Draw particle with fading effect - ensure color values are valid
                color = tuple(max(0, min(255, int(c * alpha_ratio))) for c in particle['color'])
                if sum(color) > 0 and size > 0:  # Only draw if visible and valid
                    try:
                        pygame.draw.circle(self.screen, color, 
                                         (int(particle['x']), int(particle['y'])), size)
                        particles_drawn += 1
                    except (ValueError, TypeError):
                        # Skip invalid particles
                        continue
        
        # Draw fading ship
        if self.ship_crashing and self.ship_alpha > 0:
            # Create semi-transparent ship surface
            ship_surface = self.ship.image.copy()
            ship_surface.set_alpha(max(0, min(255, int(self.ship_alpha))))
            self.screen.blit(ship_surface, self.ship.rect)
            
        # Add screen flash effect for dramatic crash
        if self.ship_crashing:
            current_time = pygame.time.get_ticks()
            time_since_crash = current_time - self.crash_start_time
            
            # Flash effect for first 500ms
            if time_since_crash < 500:
                flash_alpha = max(0, min(255, int(100 - (time_since_crash * 0.2))))
                if flash_alpha > 0:
                    flash_surface = pygame.Surface((self.settings.screen_width, 
                                                  self.settings.screen_height))
                    flash_surface.set_alpha(flash_alpha)
                    flash_surface.fill((255, 255, 255))
                    self.screen.blit(flash_surface, (0, 0))

    def _draw_shield_ui(self):
        """Draw shield skill UI information."""
        current_time = pygame.time.get_ticks()
        
        # Calculate cooldown remaining
        cooldown_remaining = max(0, self.settings.shield_cooldown - (current_time - self.shield_last_used))
        
        # Draw skill status
        font = pygame.font.SysFont(None, 36)
        
        if self.shield_active:
            # Show duration remaining
            duration_remaining = max(0, self.settings.shield_duration - (current_time - self.shield_start_time))
            status_text = f"Shield: {duration_remaining // 1000 + 1}s"
            color = (0, 255, 0)  # Green when active
        elif cooldown_remaining > 0:
            # Show cooldown
            status_text = f"Shield: {cooldown_remaining // 1000 + 1}s"
            color = (255, 0, 0)  # Red when on cooldown
        else:
            # Ready to use
            status_text = "Shield: Ready [Ctrl]"
            color = (255, 255, 255)  # White when ready
            
        text_surface = font.render(status_text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.left = self.screen.get_rect().left + 20
        text_rect.bottom = self.screen.get_rect().bottom - 50
        
        self.screen.blit(text_surface, text_rect)

    def _check_bullet_shield_collisions(self):
        """Check for collisions between player bullets and shields."""
        for bullet in self.bullets.sprites():
            hit_shields = pygame.sprite.spritecollide(bullet, self.shields, False)
            if hit_shields:
                bullet.kill()
                for shield in hit_shields:
                    if shield.hit(damage=20):
                        continue  # Shield already removed by hit()

    def _check_alien_bullet_shield_collisions(self):
        """Check for collisions between alien bullets and shields."""
        for bullet in self.alien_bullets.sprites():
            hit_shields = pygame.sprite.spritecollide(bullet, self.shields, False)
            if hit_shields:
                bullet.kill()
                for shield in hit_shields:
                    if shield.hit(damage=20):
                        continue  # Shield already removed by hit()

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        
        # Draw ship (only when not crashing, crash effects handles fading ship)
        if not self.ship_crashing:
            self.ship.blitme()
        
        # Draw shields
        for shield in self.shields.sprites():
            shield.draw()
        
        for alien_bullet in self.alien_bullets.sprites(): 
            alien_bullet.draw_bullet()

        self.aliens.draw(self.screen)
        
        # Always draw crash effects (handles crash particles and fading ship)
        self._draw_crash_effects()

        # Draw the score information.
        self.sb.show_score()
        
        # Draw shield skill UI
        self._draw_shield_ui()

        # Draw the play button if the game is inactive.
        if not self.game_active:
            self.play_button.draw_button()

        pygame.display.flip()

    def _update_crash_delay(self):
        """Handle the delay after ship crash before continuing."""
        if not self.crash_delay_active:
            return
            
        current_time = pygame.time.get_ticks()
        
        if self.stats.ships_left > 0:
            # Normal crash - wait 1.5 seconds
            if current_time - self.crash_delay_start > 1500:
                self.crash_delay_active = False
                # Reset ship crash state
                self.ship_crashing = False
                self.crash_particles.clear()
                self.ship_alpha = 255
                # Create a new fleet and center the ship.
                self._create_fleet()
                self.ship.center_ship()
        else:
            # Final crash - wait 2.5 seconds
            if current_time - self.crash_delay_start > 2500:
                self.crash_delay_active = False
                self.game_active = False
                pygame.mouse.set_visible(True)
                self._save_high_score()


if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()