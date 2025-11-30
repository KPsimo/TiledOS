
from widgets import *
import data.uiData as uiData
                
import pygame
import random
import math

class SpaceLines(Widget):
    name = "Space Lines"
    preferredSizes = [(3, 2)]
    
    def __init__(self, width=3, height=2, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.lines = []
        self.max_lines = 10
        self.line_color = uiData.textColor
        self.fade_speed = 0.02
        self.create_lines()

    def create_lines(self):
        for _ in range(self.max_lines):
            x_start = random.uniform(0, self.width * uiData.cellSize)
            y = random.uniform(0, self.height * uiData.cellSize)
            self.lines.append({'x_start': x_start, 'y': y, 'alpha': 255})

    def update(self):
        for line in self.lines:
            line['x_start'] -= random.uniform(0.5, 3)  # Move line to the left
            if line['alpha'] > 0:
                line['alpha'] -= self.fade_speed * 255  # Fade out
            if line['x_start'] < -uiData.cellSize:  # Reset line when it goes off screen
                line['x_start'] = random.uniform(self.width * uiData.cellSize, self.width * uiData.cellSize + 100)
                line['y'] = random.uniform(0, self.height * uiData.cellSize)
                line['alpha'] = 255

    def drawContent(self):
        for line in self.lines:
            if line['alpha'] > 0:
                pygame.draw.line(self.surface, (self.line_color[0], self.line_color[1], self.line_color[2], int(line['alpha'])), 
                                 (line['x_start'], line['y']), 
                                 (line['x_start'] + uiData.cellSize, line['y']))

    def tick(self, screen):
        self.update()
        super().tick(screen)

WIDGET_CLASS = SpaceLines
