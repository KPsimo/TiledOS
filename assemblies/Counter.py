
from widgets import *
import data.uiData as uiData
                
import pygame

class Counter(Widget):
    name = "Counter"
    preferredSizes = [(2, 1)]
    
    def __init__(self, width=2, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.count = 0

    def update(self):
        pass

    def drawContent(self):
        countStr = str(self.count)
        text = self.fonts[int(self.height-1)].render(countStr, True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(text, textRect)

    def clicked(self, mx, my):
        self.count += 1

WIDGET_CLASS = Counter
