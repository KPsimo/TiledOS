
from widgets import *
import data.uiData as uiData
                
import pygame
import random

class Rain(Widget):
    name = "Rain"
    preferredSizes = [(3, 3), (4, 4), (5, 5)]
    
    def __init__(self, width=4, height=4, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.drops = []
        self.max_drops = 50
        self.initializeDrops()

    def initializeDrops(self):
        for _ in range(self.max_drops):
            x = random.randint(0, int(self.getActualSize()[0] // uiData.cellSize) - 1)
            y = random.randint(0, int(self.getActualSize()[1] // uiData.cellSize) - 1)
            self.drops.append({'x': x, 'y': y, 'length': random.randint(10, 30), 'speed': random.uniform(1, 3)})

    def update(self):
        for drop in self.drops:
            drop['y'] += drop['speed']
            if drop['y'] * uiData.cellSize > self.getActualSize()[1]:
                drop['y'] = 0
                drop['x'] = random.randint(0, int(self.getActualSize()[0] // uiData.cellSize) - 1)
                drop['length'] = random.randint(10, 30)
                drop['speed'] = random.uniform(1, 3)

    def drawContent(self):
        for drop in self.drops:
            color = (0, 0, 255)
            pygame.draw.line(self.surface, color, 
                             (drop['x'] * uiData.cellSize + uiData.cellSize // 2, drop['y']),
                             (drop['x'] * uiData.cellSize + uiData.cellSize // 2, drop['y'] + drop['length']), 
                             2)

WIDGET_CLASS = Rain
