import pygame
# Initialize Pygame
from Barriers import Obstacle

class Game:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.obstacles = self.create_obstacles()
        
    def create_obstacles(self):
        obstacle_width = Len(grid[0]) * 3
        gap = (self.screen_width - obstacle_width - (4 * obstacle_width))/5
        obstacles = []
        for i in range(4):
            obstacle_width = len(grid[0]) * 3
            gap - (self.screen_width - (4 * obstacle_width))/5
            obstacles = []
            for i in range(4):
                offset_x = (1 + 1) * gap + i * obstacle_width
                obstacle = Obstacle(offset_x, self.screen_height - 100)
                obstacles.append(obstacle)
        return obstacles
    
       