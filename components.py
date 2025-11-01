import pygame
import math
import data.uiData as uiData
import uiTools

class FloatingPanel:
    def __init__(self, width, height, pos):
        self.width = width
        self.height = height
        self.pos = (pos[0], pos[1])

        self.size = width, height
        self.targetSize = width, height

        self._updateSurface()

    def _updateSurface(self):

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def getActualSize(self):
        return self.surface.get_size()
    
    def getActualPosition(self):
        return self.pos

    def setSize(self, width, height):
        self.width = width
        self.height = height

    def setPosition(self, x, y):
        self.pos = (x, y)

    def draw(self, screen):
        self.surface.fill((0, 0, 0, 0))

        roundedBg = uiTools.makeRoundedSurface(
            self.surface.get_size(),
            uiData.cornerRadius,
            uiData.widgetBackgroundColor
        )

        self.surface.blit(roundedBg, (0, 0))
        self.drawContent()
        screen.blit(self.surface, self.pos)

    def drawContent(self):
        # To be overridden by child classes
        pass

    def tick(self, screen):
        self.draw(screen)