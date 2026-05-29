"""
Player Character
Handles player movement, position, and realm detection
"""

import pygame
import math
import config

class Player:
    """The player character navigating through samsara"""
    
    def __init__(self, x, y):
        """
        Initialize player
        
        Args:
            x: Starting x position
            y: Starting y position
        """
        self.x = x
        self.y = y
        self.size = config.PLAYER_SIZE
        self.speed = config.PLAYER_SPEED
        self.color = config.PLAYER_COLOR
        
        # Create rect for collision and rendering
        self.rect = pygame.Rect(x, y, self.size, self.size)
        
        # Movement state
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        
        # Hell suffering mechanics
        self.hell_drain_timer = 0
        
    def handle_input(self, keys):
        """
        Handle keyboard input for movement
        
        Args:
            keys: Pygame key state
        """
        self.moving_up = keys[pygame.K_w] or keys[pygame.K_UP]
        self.moving_down = keys[pygame.K_s] or keys[pygame.K_DOWN]
        self.moving_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        self.moving_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        
    def update(self):
        """Update player position based on input"""
        dx = 0
        dy = 0
        
        if self.moving_up:
            dy -= self.speed
        if self.moving_down:
            dy += self.speed
        if self.moving_left:
            dx -= self.speed
        if self.moving_right:
            dx += self.speed
            
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707  # 1/sqrt(2)
            dy *= 0.707
            
        # Update position
        self.x += dx
        self.y += dy
        
        # Keep player within world bounds
        self.x = max(0, min(self.x, config.WORLD_WIDTH - self.size))
        self.y = max(0, min(self.y, config.WORLD_HEIGHT - self.size))
        
        # Update rect
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
    def get_distance_from_temple(self):
        """
        Calculate distance from temple center
        
        Returns:
            float: Distance in pixels
        """
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        
        dx = center_x - config.TEMPLE_CENTER[0]
        dy = center_y - config.TEMPLE_CENTER[1]
        
        return math.sqrt(dx * dx + dy * dy)
        
    def get_current_realm(self):
        """
        Determine which realm the player is currently in
        Based on distance from temple center
        
        Returns:
            str: Name of current realm
        """
        distance = self.get_distance_from_temple()
        
        if distance <= config.TEMPLE_RADIUS:
            return 'temple'
        elif distance <= config.DEVA_RADIUS:
            return 'deva'
        elif distance <= config.ASURA_RADIUS:
            return 'asura'
        elif distance <= config.HUMAN_RADIUS:
            return 'human'
        elif distance <= config.ANIMAL_RADIUS:
            return 'animal'
        elif distance <= config.HUNGRY_GHOST_RADIUS:
            return 'hungry_ghost'
        else:
            return 'hell'
            
    def get_realm_color(self):
        """
        Get the color associated with current realm
        
        Returns:
            tuple: RGB color tuple
        """
        realm = self.get_current_realm()
        return config.REALM_COLORS.get(realm, config.WHITE)
        
    def draw(self, surface, camera_x, camera_y):
        """
        Draw player on screen
        
        Args:
            surface: Pygame surface to draw on
            camera_x: Camera x offset
            camera_y: Camera y offset
        """
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        
        # Draw player as a simple colored square (placeholder)
        pygame.draw.rect(surface, self.color, 
                        (screen_x, screen_y, self.size, self.size))
        
        # Draw a small indicator showing direction faced (center circle)
        center_x = screen_x + self.size // 2
        center_y = screen_y + self.size // 2
        pygame.draw.circle(surface, config.WHITE, (center_x, center_y), 4)
        
    def set_position(self, x, y):
        """
        Set player position (used for spawn/teleport)
        
        Args:
            x: New x position
            y: New y position
        """
        self.x = x
        self.y = y
        self.rect.x = int(x)
        self.rect.y = int(y)
        
    def get_spawn_position_for_realm(self, realm_name):
        """
        Get spawn position for a given realm
        
        Args:
            realm_name: Name of realm to spawn in
            
        Returns:
            tuple: (x, y) spawn coordinates
        """
        # Spawn at a random angle but specific distance from center
        import random
        angle = random.uniform(0, 2 * math.pi)
        
        # Determine distance based on realm
        if realm_name == 'temple':
            distance = 0
        elif realm_name == 'deva':
            distance = (config.TEMPLE_RADIUS + config.DEVA_RADIUS) / 2
        elif realm_name == 'asura':
            distance = (config.DEVA_RADIUS + config.ASURA_RADIUS) / 2
        elif realm_name == 'human':
            distance = (config.ASURA_RADIUS + config.HUMAN_RADIUS) / 2
        elif realm_name == 'animal':
            distance = (config.HUMAN_RADIUS + config.ANIMAL_RADIUS) / 2
        elif realm_name == 'hungry_ghost':
            distance = (config.ANIMAL_RADIUS + config.HUNGRY_GHOST_RADIUS) / 2
        else:  # hell
            distance = (config.HUNGRY_GHOST_RADIUS + config.HELL_RADIUS) / 2
            
        # Calculate spawn position
        spawn_x = config.TEMPLE_CENTER[0] + distance * math.cos(angle)
        spawn_y = config.TEMPLE_CENTER[1] + distance * math.sin(angle)
        
        return (spawn_x - self.size / 2, spawn_y - self.size / 2)
    
    def apply_hell_suffering(self, stats):
        """
        Apply Hell realm suffering - stats slowly drain
        
        Args:
            stats: Stats object to drain from
            
        Returns:
            String message if draining occurred, None otherwise
        """
        realm = self.get_current_realm()
        distance = self.get_distance_from_temple()
        
        # Update drain timer
        self.hell_drain_timer += 1
        
        # Only apply drain every HELL_DRAIN_INTERVAL frames (1 second)
        if self.hell_drain_timer < config.HELL_DRAIN_INTERVAL:
            return None
            
        # Reset timer
        self.hell_drain_timer = 0
        
        # Check if in VOID (beyond Hell boundary) - RAPID DRAIN!
        if distance > config.VOID_BOUNDARY:
            drain_amount = int(config.VOID_STAT_DRAIN_RATE)
            stats.merit = max(-50, stats.merit - drain_amount)
            stats.karma = max(-50, stats.karma - drain_amount)
            stats.wisdom = max(0, stats.wisdom - drain_amount)
            return f"🔥 ETERNAL TORTURE! -{drain_amount} to all stats! 🔥"
        
        # Check if in Hell realm - SLOW DRAIN
        elif realm == 'hell':
            drain_amount = max(1, int(config.HELL_STAT_DRAIN_RATE))
            stats.merit = max(-50, stats.merit - drain_amount)
            stats.karma = max(-50, stats.karma - drain_amount) 
            stats.wisdom = max(0, stats.wisdom - drain_amount)
            return f"💀 Hell's suffering drains you... 💀"
        
        return None
        
    def to_dict(self):
        """
        Convert player state to dictionary for saving
        
        Returns:
            Dict with player data
        """
        return {
            'x': self.x,
            'y': self.y
        }
        
    def from_dict(self, data):
        """
        Load player state from dictionary
        
        Args:
            data: Dict with saved player data
        """
        self.set_position(data['x'], data['y'])
