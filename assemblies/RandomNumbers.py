
from widgets import *
import data.uiData as uiData
                
import pygame
import random

class RandomNumbers(Widget):
    name = "Random Numbers"
    preferredSizes = [(3, 1)]
    
    def __init__(self, width=3, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.currentNumber = self.generateRandomNumber()

    def generateRandomNumber(self):
        return random.randint(100, 999)

    def update(self):
        self.currentNumber = self.generateRandomNumber()

    def drawContent(self):
        numberStr = str(self.currentNumber)
        text = self.fonts[int(self.height-1)].render(numberStr, True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(text, textRect)

WIDGET_CLASS = RandomNumbers
