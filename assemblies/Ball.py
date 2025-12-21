
from widgets import *
import data.uiData as uiData
                
import pygame
import random

class Ball(Widget):
    name = "Ball"
    preferredSizes = [(2, 2)]
    def __init__(self, width=2, height=2, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.radius = int(min(width, height) * uiData.cellSize / 2 * 0.8)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.speed = [random.choice([-2, 2]), random.choice([-2, 2])]

    def update(self):
        x, y = self.getActualPosition()
        if x < 0 or x + self.radius * 2 > uiData.cellSize:
            self.speed[0] = -self.speed[0]
        if y < 0 or y + self.radius * 2 > uiData.cellSize:
            self.speed[1] = -self.speed[1]
        self.pos = (self.pos[0] + self.speed[0], self.pos[1] + self.speed[1])

    def drawContent(self):
        pygame.draw.circle(self.surface, self.color, (self.radius, self.radius), self.radius)

WIDGET_CLASS = Ball
