
from widgets import *
import data.uiData as uiData
                
import pygame
import random

class Space(Widget):
    name = "Space"
    preferredSizes = [(2, 2)]
    
    def __init__(self, width=2, height=2, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.stars = [(random.randint(0, self.getActualSize()[0]), random.randint(0, self.getActualSize()[1]), random.uniform(0.2, 1)) for _ in range(20)]
        
    def update(self):
        for i, star in enumerate(self.stars):
            self.stars[i] = (star[0], star[1], max(0, star[2] - 0.01) if star[2] > 0.2 else random.uniform(0.2, 1))
        
    def drawContent(self):
        for star in self.stars:
            alpha = int(star[2] * 255)
            pygame.draw.circle(self.surface, (255, 255, 255, alpha), (int(star[0]), int(star[1])), 2)

WIDGET_CLASS = Space
