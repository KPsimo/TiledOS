
from widgets import *
import data.uiData as uiData
                
import pygame
import math

class Spiral(Widget):
    name = "Spiral"
    preferredSizes = [(3, 3)]
    
    def __init__(self, width=3, height=3, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.angle = 0
        self.radius = 50
        self.center = (self.surface.get_width() // 2, self.surface.get_height() // 2)
    
    def update(self):
        self.angle += 0.05
    
    def drawContent(self):
        self.surface.fill((0, 0, 0, 0))
        for i in range(100):
            angle = self.angle + i * 0.1
            radius = self.radius + i * 2
            x = self.center[0] + int(radius * math.cos(angle))
            y = self.center[1] + int(radius * math.sin(angle))
            pygame.draw.circle(self.surface, uiData.textColor, (x, y), 2)

WIDGET_CLASS = Spiral
