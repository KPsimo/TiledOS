
from widgets import *
import data.uiData as uiData
                
import pygame
import random
import string

class RandomLetters(Widget):
    name = "Random Letters"
    preferredSizes = [(2, 1), (3, 1)]
    
    def __init__(self, width=2, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.letters = self.generateRandomLetters()

    def generateRandomLetters(self):
        return ''.join(random.choices(string.ascii_uppercase, k=self.width))

    def update(self):
        self.letters = self.generateRandomLetters()

    def drawContent(self):
        text = self.fonts[int(self.height - 1)].render(self.letters, True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(text, textRect)

WIDGET_CLASS = RandomLetters
