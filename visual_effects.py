"""
Visual Effects System
Handles fog of ignorance, clarity effects, and particle feedback
"""

import sys
import pygame
import random
import config

IS_WEB = sys.platform == 'emscripten'

class VisualEffects:
    """Manages visual feedback for player's spiritual progress"""

    def __init__(self):
        """Initialize visual effects system"""
        self.particles = []
        self._particle_font = None
        self._fog_cache = None
        self._fog_frame = 0
        self._fog_clarity = -1
        
    def create_fog_overlay(self, surface, clarity_level):
        """
        Create "dust and dirt in your eyes" overlay
        Lower clarity = more dust and dirt obscuring vision
        
        Args:
            surface: Surface to draw dust on
            clarity_level: Float from 0.0 to 1.0 (player's clarity stat)
        """
        # Calculate dust intensity (inverse of clarity) - MUCH THICKER NOW!
        dust_alpha = int(230 * (1.0 - clarity_level))  # Was 200, now 230 - THICKER!
        
        # Create dusty brownish-tan overlay (not pure black)
        dust_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        dust_surface.set_alpha(dust_alpha)
        dust_surface.fill((80, 70, 50))
        surface.blit(dust_surface, (0, 0))

        if clarity_level < 0.6:
            if IS_WEB:
                # Cached fog — rebuild every 8 frames, fewer particles
                self._fog_frame = (self._fog_frame + 1) % 8
                if (self._fog_cache is None or self._fog_frame == 0
                        or abs(clarity_level - self._fog_clarity) > 0.05):
                    self._fog_clarity = clarity_level
                    num_p = int(60 * (1.0 - clarity_level))
                    self._fog_cache = pygame.Surface(
                        (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
                    for _ in range(num_p):
                        x = random.randint(0, config.SCREEN_WIDTH)
                        y = random.randint(0, config.SCREEN_HEIGHT)
                        size = random.randint(1, 3)
                        a = random.randint(40, 100)
                        pygame.draw.circle(self._fog_cache, (110, 90, 60, a), (x, y), size)
                surface.blit(self._fog_cache, (0, 0))
                return

        # Desktop: full-quality particles every frame
        if clarity_level < 0.6:
            dust_particle_surf = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            num_particles = int(200 * (1.0 - clarity_level))

            for _ in range(num_particles):
                x = random.randint(0, config.SCREEN_WIDTH)
                y = random.randint(0, config.SCREEN_HEIGHT)
                size = random.randint(1, 4)
                particle_alpha = random.randint(40, 120)
                pygame.draw.circle(dust_particle_surf, (110, 90, 60, particle_alpha),
                                 (x, y), size)

            surface.blit(dust_particle_surf, (0, 0))

        # Add dirt streaks when clarity is very low
        if clarity_level < 0.4:
            dirt_surf = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            num_streaks = int(30 * (1.0 - clarity_level))

            for _ in range(num_streaks):
                start_x = random.randint(0, config.SCREEN_WIDTH)
                start_y = random.randint(0, config.SCREEN_HEIGHT)
                end_x = start_x + random.randint(-50, 50)
                end_y = start_y + random.randint(10, 40)
                streak_alpha = random.randint(30, 80)
                streak_width = random.randint(1, 3)
                pygame.draw.line(dirt_surf, (60, 50, 35, streak_alpha),
                               (start_x, start_y), (end_x, end_y), streak_width)

            surface.blit(dirt_surf, (0, 0))

        # Add dirt smudges when clarity is extremely low
        if clarity_level < 0.3:
            smudge_surf = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            num_smudges = int(20 * (1.0 - clarity_level))

            for _ in range(num_smudges):
                smudge_x = random.randint(0, config.SCREEN_WIDTH)
                smudge_y = random.randint(0, config.SCREEN_HEIGHT)
                smudge_size = random.randint(10, 25)
                smudge_alpha = random.randint(20, 60)
                pygame.draw.circle(smudge_surf, (70, 60, 45, smudge_alpha),
                                 (smudge_x, smudge_y), smudge_size)

            surface.blit(smudge_surf, (0, 0))
        
    def create_vignette(self, surface, clarity_level):
        """
        Create vignette effect (darkness around edges)
        Higher clarity = less vignette
        
        Args:
            surface: Surface to draw on
            clarity_level: Player's clarity level (0.0 to 1.0)
        """
        # Vignette strength decreases with clarity
        vignette_strength = int(150 * (1.0 - clarity_level))
        
        if vignette_strength > 0:
            # Create radial gradient from center
            center_x = config.SCREEN_WIDTH // 2
            center_y = config.SCREEN_HEIGHT // 2
            max_distance = ((center_x ** 2) + (center_y ** 2)) ** 0.5
            
            vignette_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            vignette_surface.fill((0, 0, 0, 0))
            
            # Simple vignette using circular gradient
            for radius in range(int(max_distance), 0, -20):
                alpha = int(vignette_strength * (1 - radius / max_distance))
                if alpha > 0:
                    pygame.draw.circle(vignette_surface, (0, 0, 0, alpha), 
                                     (center_x, center_y), radius, 20)
                                     
            vignette_surface.set_alpha(vignette_strength)
            surface.blit(vignette_surface, (0, 0))
            
    def add_stat_particle(self, x, y, stat_type, amount):
        """
        Add floating particle to show stat gain/loss
        
        Args:
            x: Screen x position
            y: Screen y position
            stat_type: 'merit', 'karma', or 'wisdom'
            amount: Amount gained/lost
        """
        # Determine color based on stat type
        if stat_type == 'merit':
            color = config.GOLD
            symbol = '🪙'
        elif stat_type == 'karma':
            color = config.BLUE if amount > 0 else config.RED
            symbol = '☸'
        elif stat_type == 'wisdom':
            color = config.PURPLE
            symbol = '📜'
        else:
            color = config.WHITE
            symbol = '+'
            
        # Create multiple particles for dramatic effect (one for each 10 points)
        num_particles = max(1, abs(amount) // 10)
        
        for i in range(min(num_particles, 5)):  # Max 5 particles
            offset_x = (i - num_particles // 2) * 30  # Spread particles horizontally
            
            # Create particle
            particle = {
                'x': x + offset_x,
                'y': y,
                'color': color,
                'text': f"{'+' if amount > 0 else ''}{amount}",
                'symbol': symbol,
                'life': 120,  # Double lifetime for emphasis (2 seconds)
                'velocity_y': -1.5,  # Slower float for visibility
                'scale': 1.5  # Larger size
            }
            
            self.particles.append(particle)
        
    def update_particles(self):
        """Update all active particles"""
        for particle in self.particles[:]:
            particle['y'] += particle['velocity_y']
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
                
    def draw_particles(self, surface, font):
        """
        Draw all active particles
        
        Args:
            surface: Surface to draw on
            font: Pygame font for text
        """
        import pygame
        
        if self._particle_font is None:
            font_size = int(config.FONT_SIZE_MEDIUM * 1.5)
            self._particle_font = pygame.font.Font(None, font_size)

        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 120))
            large_font = self._particle_font
            
            # Draw symbol and text
            text = f"{particle['symbol']} {particle['text']}"
            text_surface = large_font.render(text, True, particle['color'])
            text_surface.set_alpha(alpha)
            
            surface.blit(text_surface, (particle['x'], particle['y']))
            
    def draw_realm_indicator(self, surface, realm_name, font):
        """
        Draw current realm name on screen
        
        Args:
            surface: Surface to draw on
            realm_name: Name of current realm
            font: Pygame font
        """
        realm_display_names = {
            'hell': 'Hell Realm - Anger & Hatred',
            'hungry_ghost': 'Hungry Ghost Realm - Craving',
            'animal': 'Animal Realm - Ignorance',
            'human': 'Human Realm - Mixed Suffering',
            'asura': 'Asura Realm - Jealousy',
            'deva': 'Deva Realm - Temporary Bliss',
            'temple': 'The Temple - Triple Gem'
        }
        
        display_name = realm_display_names.get(realm_name, realm_name)
        realm_color = config.REALM_COLORS.get(realm_name, config.WHITE)
        
        text_surface = font.render(display_name, True, realm_color)
        
        # Draw with black outline for readability
        x = 10
        y = config.SCREEN_HEIGHT - 40
        
        # Outline
        for offset_x in [-1, 0, 1]:
            for offset_y in [-1, 0, 1]:
                if offset_x != 0 or offset_y != 0:
                    outline_surface = font.render(display_name, True, config.BLACK)
                    surface.blit(outline_surface, (x + offset_x, y + offset_y))
                    
        # Main text
        surface.blit(text_surface, (x, y))
        
    def draw_temple_glow(self, surface, player_x, player_y, camera_x, camera_y, clarity_level):
        """
        Temple glow DISABLED - was too bright and obscured NPCs
        """
        pass  # No glow effect
                           
    def draw_wisdom_rays(self, surface, player_x, player_y, camera_x, camera_y, clarity_level):
        """
        Draw light rays pointing toward temple when clarity is high
        
        Args:
            surface: Surface to draw on
            player_x: Player world x position  
            player_y: Player world y position
            camera_x: Camera x offset
            camera_y: Camera y offset
            clarity_level: Player's clarity level (0.0 to 1.0)
        """
        if clarity_level < 0.5:
            return  # Rays not visible until 50% clarity
            
        # Calculate direction to temple
        dx = config.TEMPLE_CENTER[0] - (player_x + 16)
        dy = config.TEMPLE_CENTER[1] - (player_y + 16)
        
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance < config.TEMPLE_RADIUS:
            return  # Already at temple
            
        # Normalize direction
        if distance > 0:
            dx /= distance
            dy /= distance
            
        # Draw subtle directional indicators at screen edges
        ray_alpha = int(150 * (clarity_level - 0.5) * 2)  # Scale from 0.5-1.0 to 0-1.0
        
        # Calculate ray position (pointing toward temple from screen edge)
        screen_center_x = config.SCREEN_WIDTH // 2
        screen_center_y = config.SCREEN_HEIGHT // 2
        
        # Draw arrow-like indicators
        ray_length = 30
        arrow_x = screen_center_x + dx * 100
        arrow_y = screen_center_y + dy * 100
        
        arrow_end_x = arrow_x + dx * ray_length
        arrow_end_y = arrow_y + dy * ray_length
        
        if ray_alpha > 0:
            pygame.draw.line(surface, (*config.GOLD, ray_alpha),
                           (arrow_x, arrow_y), (arrow_end_x, arrow_end_y), 3)
