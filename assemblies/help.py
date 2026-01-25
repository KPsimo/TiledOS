
from widgets import *
import data.uiData as uiData
                
import pygame
import math

class help(Widget):
    name = "Help"
    preferredSizes = [(2, 2)]
    
    def __init__(self, width=2, height=2, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.angle = 0
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 255), (50, 50), 40)
        font = pygame.font.Font('resources/outfit.ttf', 60)
        text = font.render("?", True, (0, 0, 0))
        textRect = text.get_rect(center=(50, 50))
        self.image.blit(text, textRect)

    def update(self):
        self.angle = (self.angle + 1) % 360

    def drawContent(self):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        rotated_rect = rotated_image.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(rotated_image, rotated_rect)

WIDGET_CLASS = help
