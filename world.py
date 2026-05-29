"""
World System
Manages the game world, camera, and realm rendering
"""

import sys
import pygame
import math
import config

IS_WEB = sys.platform == 'emscripten'

class World:
    """Manages the game world and camera"""

    def __init__(self):
        """Initialize world"""
        self.width = config.WORLD_WIDTH
        self.height = config.WORLD_HEIGHT

        # Camera position (top-left corner of view)
        self.camera_x = 0
        self.camera_y = 0

        # Cached rotated text surfaces (created once, reused every frame)
        self._gem_text_cache = None
        
    def update_camera(self, player_x, player_y):
        """
        Update camera to follow player
        
        Args:
            player_x: Player x position in world
            player_y: Player y position in world
        """
        # Center camera on player
        self.camera_x = player_x - config.SCREEN_WIDTH // 2
        self.camera_y = player_y - config.SCREEN_HEIGHT // 2
        
        # Clamp camera to world bounds
        self.camera_x = max(0, min(self.camera_x, 
                                   self.width - config.SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y,
                                   self.height - config.SCREEN_HEIGHT))
                                   
    def draw_world(self, surface, player):
        """
        Draw the game world (realms as concentric circles)
        
        Args:
            surface: Surface to draw on
            player: Player object
        """
        # Fill with black background
        surface.fill(config.BLACK)
        
        # Draw concentric circles representing realms
        # Calculate temple position relative to camera
        temple_x = config.TEMPLE_CENTER[0] - self.camera_x
        temple_y = config.TEMPLE_CENTER[1] - self.camera_y
        
        # Draw from outermost to innermost
        realms_to_draw = [
            (config.HELL_RADIUS, 'hell'),
            (config.HUNGRY_GHOST_RADIUS, 'hungry_ghost'),
            (config.ANIMAL_RADIUS, 'animal'),
            (config.HUMAN_RADIUS, 'human'),
            (config.ASURA_RADIUS, 'asura'),
            (config.DEVA_RADIUS, 'deva'),
            (config.TEMPLE_RADIUS, 'temple')
        ]
        
        for radius, realm_name in realms_to_draw:
            # Only draw if circle is visible on screen
            if self.is_circle_visible(temple_x, temple_y, radius):
                color = config.REALM_COLORS[realm_name]
                
                # Draw filled circle
                try:
                    pygame.draw.circle(surface, color, 
                                     (int(temple_x), int(temple_y)), 
                                     radius)
                except:
                    # Circle too large or off screen
                    pass
                    
                # Draw border
                try:
                    border_color = self.lighten_color(color, 50)
                    pygame.draw.circle(surface, border_color,
                                     (int(temple_x), int(temple_y)),
                                     radius, 3)
                except:
                    pass
        
        # SAMSARA ATMOSPHERE — lighter on web but fully visible
        if self.is_point_visible(temple_x, temple_y):
            import math

            # Draw 6 spokes (direct lines, no SRCALPHA surface)
            spoke_color = (60, 60, 60)
            for i in range(6):
                angle = (i * 60) * (math.pi / 180)
                start_x = temple_x + int(math.cos(angle) * config.HELL_RADIUS)
                start_y = temple_y + int(math.sin(angle) * config.HELL_RADIUS)
                end_x = temple_x + int(math.cos(angle) * config.TEMPLE_RADIUS)
                end_y = temple_y + int(math.sin(angle) * config.TEMPLE_RADIUS)
                if (self.is_point_visible(start_x, start_y) or
                        self.is_point_visible(end_x, end_y)):
                    pygame.draw.line(surface, spoke_color,
                                     (start_x, start_y), (end_x, end_y), 4)

            # Chain links around realm borders — fewer on web
            chain_positions = [
                (config.HELL_RADIUS,         (40, 0, 0)),
                (config.HUNGRY_GHOST_RADIUS, (60, 30, 0)),
                (config.ANIMAL_RADIUS,       (40, 25, 10)),
                (config.HUMAN_RADIUS,        (30, 40, 50)),
                (config.ASURA_RADIUS,        (50, 0, 50)),
                (config.DEVA_RADIUS,         (70, 60, 0)),
            ]
            num_links = 8 if IS_WEB else 16
            for radius, chain_color in chain_positions:
                for i in range(num_links):
                    angle = (i * (360 / num_links)) * (math.pi / 180)
                    link_x = temple_x + int(math.cos(angle) * radius)
                    link_y = temple_y + int(math.sin(angle) * radius)
                    if self.is_point_visible(link_x, link_y):
                        pygame.draw.circle(surface, chain_color, (link_x, link_y), 6)
                        pygame.draw.circle(surface, (0, 0, 0), (link_x, link_y), 6, 2)
                        pygame.draw.circle(surface, (0, 0, 0), (link_x, link_y), 3)

            # Skulls in Hell realm
            if self.is_point_visible(temple_x + config.HELL_RADIUS - 100, temple_y):
                for i in range(8):
                    angle = (i * 45) * (math.pi / 180)
                    skull_x = temple_x + int(math.cos(angle) * (config.HELL_RADIUS - 50))
                    skull_y = temple_y + int(math.sin(angle) * (config.HELL_RADIUS - 50))
                    if self.is_point_visible(skull_x, skull_y):
                        pygame.draw.circle(surface, (100, 0, 0), (skull_x, skull_y), 8)
                        pygame.draw.rect(surface, (80, 0, 0),
                                         (skull_x - 6, skull_y + 4, 12, 6))
                    
        # Draw SACRED TRIPLE GEM TEMPLE at center - CLEARLY VISIBLE NOW!
        if self.is_point_visible(temple_x, temple_y):
            import math
            
            # TRIPLE GEM SACRED WALLS - Enclosing the temple area
            # These walls protect Buddha and represent refuge in the Triple Gem
            wall_size = 180  # Larger than temple structure
            wall_thickness = 8
            wall_color = (220, 200, 150)  # Light stone color
            
            # Draw four walls forming a square around temple
            # Top wall
            pygame.draw.rect(surface, wall_color,
                           (temple_x - wall_size//2, temple_y - wall_size//2,
                            wall_size, wall_thickness))
            # Bottom wall
            pygame.draw.rect(surface, wall_color,
                           (temple_x - wall_size//2, temple_y + wall_size//2 - wall_thickness,
                            wall_size, wall_thickness))
            # Left wall
            pygame.draw.rect(surface, wall_color,
                           (temple_x - wall_size//2, temple_y - wall_size//2,
                            wall_thickness, wall_size))
            # Right wall
            pygame.draw.rect(surface, wall_color,
                           (temple_x + wall_size//2 - wall_thickness, temple_y - wall_size//2,
                            wall_thickness, wall_size))
            
            # Draw gates in each wall (openings to enter)
            gate_width = 40
            gate_color = (200, 200, 200)
            # Top gate
            pygame.draw.rect(surface, gate_color,
                           (temple_x - gate_width//2, temple_y - wall_size//2,
                            gate_width, wall_thickness))
            # Bottom gate
            pygame.draw.rect(surface, gate_color,
                           (temple_x - gate_width//2, temple_y + wall_size//2 - wall_thickness,
                            gate_width, wall_thickness))
            # Left gate
            pygame.draw.rect(surface, gate_color,
                           (temple_x - wall_size//2, temple_y - gate_width//2,
                            wall_thickness, gate_width))
            # Right gate
            pygame.draw.rect(surface, gate_color,
                           (temple_x + wall_size//2 - wall_thickness, temple_y - gate_width//2,
                            wall_thickness, gate_width))
            
            # Draw "Triple Gem" symbols on corners of walls
            corner_distance = wall_size // 2 - 10
            for i in range(4):
                angle = (i * 90 + 45) * (math.pi / 180)  # 45, 135, 225, 315 degrees
                corner_x = temple_x + math.cos(angle) * corner_distance
                corner_y = temple_y + math.sin(angle) * corner_distance
                # Draw three small circles representing Buddha, Dhamma, Sangha
                for j in range(3):
                    offset_angle = angle + (j - 1) * 0.3
                    gem_x = corner_x + math.cos(offset_angle) * 8
                    gem_y = corner_y + math.sin(offset_angle) * 8
                    pygame.draw.circle(surface, config.GOLD, (int(gem_x), int(gem_y)), 5)
                    pygame.draw.circle(surface, config.WHITE, (int(gem_x), int(gem_y)), 5, 1)
            
            # Draw "TRIPLE GEM" text on walls — cache rotated surfaces (rotation is expensive)
            if self._gem_text_cache is None:
                gem_font = config.make_font(24)
                flat  = gem_font.render("TRIPLE GEM", True, (255, 215, 0))
                left  = pygame.transform.rotate(flat, 90)
                right = pygame.transform.rotate(flat, -90)
                self._gem_text_cache = (flat, left, right)

            top_text, left_text, right_text = self._gem_text_cache

            surface.blit(top_text,
                         (temple_x - top_text.get_width() // 2,
                          temple_y - wall_size // 2 - 25))
            surface.blit(top_text,
                         (temple_x - top_text.get_width() // 2,
                          temple_y + wall_size // 2 + 10))
            surface.blit(left_text,
                         (temple_x - wall_size // 2 - 30,
                          temple_y - left_text.get_height() // 2))
            surface.blit(right_text,
                         (temple_x + wall_size // 2 + 10,
                          temple_y - right_text.get_height() // 2))
            
            # TEMPLE STRUCTURE - Large and imposing (inside the walls!)
            temple_size = 100
            
            # Temple roof (triangle)
            roof_points = [
                (temple_x, temple_y - temple_size//2 - 20),  # Top peak
                (temple_x - temple_size//2, temple_y - 10),   # Left
                (temple_x + temple_size//2, temple_y - 10)    # Right
            ]
            pygame.draw.polygon(surface, config.GOLD, roof_points)
            pygame.draw.polygon(surface, config.WHITE, roof_points, 4)
            
            # Temple base (rectangle)
            base_rect = pygame.Rect(temple_x - temple_size//2,
                                   temple_y - 10,
                                   temple_size, temple_size//2)
            pygame.draw.rect(surface, (255, 215, 0), base_rect)
            pygame.draw.rect(surface, config.WHITE, base_rect, 4)
            
            # Three pillars (for Triple Gem!)
            pillar_width = 15
            pillar_height = 30
            pillar_spacing = 25
            
            for i in [-1, 0, 1]:  # Left, Center, Right
                pillar_x = temple_x + (i * pillar_spacing) - pillar_width//2
                pillar_y = temple_y + 10
                pillar_rect = pygame.Rect(pillar_x, pillar_y, pillar_width, pillar_height)
                pygame.draw.rect(surface, config.WHITE, pillar_rect)
                pygame.draw.rect(surface, config.GOLD, pillar_rect, 2)
            
            # GIANT DHARMA WHEEL at center
            wheel_radius = 30
            self.draw_dharma_wheel(surface, temple_x, temple_y - 20, wheel_radius)
            
            # Sacred symbols around temple
            num_symbols = 8
            symbol_distance = 80
            for i in range(num_symbols):
                angle = (i * 45) * (math.pi / 180)
                symbol_x = temple_x + math.cos(angle) * symbol_distance
                symbol_y = temple_y + math.sin(angle) * symbol_distance
                pygame.draw.circle(surface, config.GOLD, (int(symbol_x), int(symbol_y)), 8)
                pygame.draw.circle(surface, config.WHITE, (int(symbol_x), int(symbol_y)), 8, 2)
            
    def draw_dharma_wheel(self, surface, x, y, radius):
        """
        Draw a simplified dharma wheel symbol
        
        Args:
            surface: Surface to draw on
            x: Center x
            y: Center y
            radius: Wheel radius
        """
        # Center circle
        pygame.draw.circle(surface, config.WHITE, (int(x), int(y)), 3)
        
        # 8 spokes (Noble Eightfold Path)
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            end_x = x + radius * math.cos(angle)
            end_y = y + radius * math.sin(angle)
            pygame.draw.line(surface, config.WHITE,
                           (int(x), int(y)), 
                           (int(end_x), int(end_y)), 2)
                           
        # Outer circle
        pygame.draw.circle(surface, config.WHITE, (int(x), int(y)), radius, 2)
        
    def is_circle_visible(self, center_x, center_y, radius):
        """
        Check if a circle is visible on screen
        
        Args:
            center_x: Circle center x (screen coordinates)
            center_y: Circle center y (screen coordinates)
            radius: Circle radius
            
        Returns:
            bool: True if circle might be visible
        """
        # Simple check: is center within expanded screen bounds?
        margin = radius + 100
        return (-margin < center_x < config.SCREEN_WIDTH + margin and
                -margin < center_y < config.SCREEN_HEIGHT + margin)
                
    def is_point_visible(self, x, y):
        """
        Check if a point is visible on screen
        
        Args:
            x: Point x (screen coordinates)
            y: Point y (screen coordinates)
            
        Returns:
            bool: True if point is on screen
        """
        return (0 <= x <= config.SCREEN_WIDTH and
                0 <= y <= config.SCREEN_HEIGHT)
                
    def lighten_color(self, color, amount):
        """
        Lighten a color by a given amount
        
        Args:
            color: RGB tuple
            amount: Amount to lighten (0-255)
            
        Returns:
            tuple: Lightened RGB color
        """
        return (
            min(255, color[0] + amount),
            min(255, color[1] + amount),
            min(255, color[2] + amount)
        )
        
    def draw_grid(self, surface):
        """
        Draw a subtle grid for visual reference (optional, for debugging)
        
        Args:
            surface: Surface to draw on
        """
        grid_color = (30, 30, 30)
        grid_size = 100
        
        # Vertical lines
        start_x = -(self.camera_x % grid_size)
        for x in range(int(start_x), config.SCREEN_WIDTH, grid_size):
            pygame.draw.line(surface, grid_color,
                           (x, 0), (x, config.SCREEN_HEIGHT), 1)
                           
        # Horizontal lines
        start_y = -(self.camera_y % grid_size)
        for y in range(int(start_y), config.SCREEN_HEIGHT, grid_size):
            pygame.draw.line(surface, grid_color,
                           (0, y), (config.SCREEN_WIDTH, y), 1)
                           
    def get_camera_offset(self):
        """
        Get camera offset for converting world to screen coordinates
        
        Returns:
            tuple: (camera_x, camera_y)
        """
        return (self.camera_x, self.camera_y)
        
    def world_to_screen(self, world_x, world_y):
        """
        Convert world coordinates to screen coordinates
        
        Args:
            world_x: World x coordinate
            world_y: World y coordinate
            
        Returns:
            tuple: (screen_x, screen_y)
        """
        return (world_x - self.camera_x, world_y - self.camera_y)
        
    def screen_to_world(self, screen_x, screen_y):
        """
        Convert screen coordinates to world coordinates
        
        Args:
            screen_x: Screen x coordinate
            screen_y: Screen y coordinate
            
        Returns:
            tuple: (world_x, world_y)
        """
        return (screen_x + self.camera_x, screen_y + self.camera_y)
