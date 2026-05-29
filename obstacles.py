"""
Mini-Mara Obstacle System
Obstacles that represent delusions and attachments blocking the path
Players can destroy them to gain progress
"""

import pygame
import random
import math
import config

class MiniMara:
    """A mini obstacle representing delusions/attachments"""
    
    def __init__(self, x, y, obstacle_type):
        """
        Initialize mini-Mara obstacle
        
        Args:
            x: World x position
            y: World y position
            obstacle_type: Type of obstacle (determines appearance and rewards)
        """
        self.x = x
        self.y = y
        self.type = obstacle_type
        self.alive = True
        self.health = 3  # Takes 3 hits to destroy
        self.shake_timer = 0
        self.particle_timer = 0
        
        # Obstacle types and their meanings
        self.obstacle_data = {
            'doubt': {
                'color': (100, 100, 150),
                'size': 30,
                'symbol': '?',
                'message': '💥 Shattered the obstacle of DOUBT!',
                'wisdom': 15,
                'merit': 10,
                'karma': 10
            },
            'fear': {
                'color': (120, 80, 120),
                'size': 35,
                'symbol': '!',
                'message': '💥 Destroyed the obstacle of FEAR!',
                'wisdom': 18,
                'merit': 12,
                'karma': 12
            },
            'attachment': {
                'color': (150, 100, 80),
                'size': 32,
                'symbol': '♦',
                'message': '💥 Broke through ATTACHMENT!',
                'wisdom': 20,
                'merit': 15,
                'karma': 15
            },
            'delusion': {
                'color': (130, 130, 100),
                'size': 38,
                'symbol': '◊',
                'message': '💥 Pierced the veil of DELUSION!',
                'wisdom': 22,
                'merit': 18,
                'karma': 18
            },
            'craving': {
                'color': (150, 120, 90),
                'size': 33,
                'symbol': '○',
                'message': '💥 Released CRAVING!',
                'wisdom': 16,
                'merit': 12,
                'karma': 14
            }
        }
        
        self.data = self.obstacle_data.get(obstacle_type, self.obstacle_data['doubt'])
        
    def take_damage(self):
        """
        Damage the obstacle
        
        Returns:
            Dict with rewards if destroyed, None otherwise
        """
        self.health -= 1
        self.shake_timer = 20  # Shake for visual feedback
        
        if self.health <= 0:
            self.alive = False
            return {
                'merit': self.data['merit'],
                'karma': self.data['karma'],
                'wisdom': self.data['wisdom'],
                'message': self.data['message']
            }
        return None
        
    def is_near_player(self, player_x, player_y, distance=50):
        """Check if player is near enough to attack"""
        dx = self.x - player_x
        dy = self.y - player_y
        return (dx*dx + dy*dy) < (distance * distance)
        
    def draw(self, surface, camera_x, camera_y):
        """Draw the obstacle"""
        if not self.alive:
            return
            
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Apply shake if damaged
        if self.shake_timer > 0:
            screen_x += random.randint(-3, 3)
            screen_y += random.randint(-3, 3)
            self.shake_timer -= 1
            
        size = self.data['size']
        color = self.data['color']
        
        # Pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() / 300))
        pulse_size = int(size + pulse * 8)
        
        # Dark aura
        for i in range(3):
            aura_size = pulse_size + (i * 10)
            aura_alpha = int(100 - (i * 30))
            aura_surf = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (*color, aura_alpha), 
                             (aura_size, aura_size), aura_size)
            surface.blit(aura_surf, (screen_x - aura_size, screen_y - aura_size))
        
        # Main body - diamond shape
        points = [
            (screen_x, screen_y - size),      # Top
            (screen_x + size, screen_y),      # Right
            (screen_x, screen_y + size),      # Bottom
            (screen_x - size, screen_y)       # Left
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (200, 0, 0), points, 3)
        
        # Symbol in center
        font = pygame.font.Font(None, 36)
        symbol_surf = font.render(self.data['symbol'], True, (255, 255, 255))
        symbol_x = screen_x - symbol_surf.get_width() // 2
        symbol_y = screen_y - symbol_surf.get_height() // 2
        surface.blit(symbol_surf, (symbol_x, symbol_y))
        
        # Health indicator
        for i in range(self.health):
            health_x = screen_x - 15 + (i * 10)
            health_y = screen_y + size + 10
            pygame.draw.circle(surface, (255, 50, 50), (health_x, health_y), 4)


class ObstacleManager:
    """Manages all mini-Mara obstacles"""
    
    def __init__(self):
        """Initialize obstacle manager"""
        self.obstacles = []
        self.spawn_timer = 0
        self.spawn_interval = 600  # Spawn every 10 seconds
        
    def spawn_obstacles(self, num_obstacles=15):
        """
        Spawn initial obstacles across the world
        
        Args:
            num_obstacles: Number of obstacles to spawn
        """
        obstacle_types = ['doubt', 'fear', 'attachment', 'delusion', 'craving']
        
        for _ in range(num_obstacles):
            # Random position in world (avoiding very center)
            angle = random.random() * 2 * math.pi
            distance = random.randint(600, 1400)  # Between Deva and Hungry Ghost realms
            
            x = config.TEMPLE_CENTER[0] + math.cos(angle) * distance
            y = config.TEMPLE_CENTER[1] + math.sin(angle) * distance
            
            obstacle_type = random.choice(obstacle_types)
            self.obstacles.append(MiniMara(x, y, obstacle_type))
            
    def update(self):
        """Update obstacles - spawn new ones periodically"""
        self.spawn_timer += 1
        
        # Remove dead obstacles
        self.obstacles = [obs for obs in self.obstacles if obs.alive]
        
        # Spawn new obstacle periodically if below threshold
        if self.spawn_timer >= self.spawn_interval and len(self.obstacles) < 20:
            self.spawn_timer = 0
            obstacle_types = ['doubt', 'fear', 'attachment', 'delusion', 'craving']
            
            angle = random.random() * 2 * math.pi
            distance = random.randint(600, 1400)
            
            x = config.TEMPLE_CENTER[0] + math.cos(angle) * distance
            y = config.TEMPLE_CENTER[1] + math.sin(angle) * distance
            
            obstacle_type = random.choice(obstacle_types)
            self.obstacles.append(MiniMara(x, y, obstacle_type))
            
    def get_nearby_obstacle(self, player_x, player_y):
        """
        Get obstacle near player that can be attacked
        
        Args:
            player_x: Player x position
            player_y: Player y position
            
        Returns:
            MiniMara object or None
        """
        for obstacle in self.obstacles:
            if obstacle.alive and obstacle.is_near_player(player_x, player_y):
                return obstacle
        return None
        
    def draw(self, surface, camera_x, camera_y):
        """Draw all obstacles"""
        for obstacle in self.obstacles:
            if obstacle.alive:
                obstacle.draw(surface, camera_x, camera_y)
