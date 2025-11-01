import pygame
import math
import data.uiData as uiData
import uiTools
import widgets

class FloatingPanel:
    def __init__(self, width, height, pos):
        self.width = width
        self.height = height
        self.pos = (pos[0], pos[1])

        self.size = width, height

        self.dragging = False
        self.dragOffset = (0, 0)

        self._updateSurface()

    def _updateSurface(self):

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def getSize(self):
        return self.surface.get_size()
    
    def getPosition(self):
        return self.pos

    def getRect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)

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
            uiData.primaryTransparentColor
        )

        self.surface.blit(roundedBg, (0, 0))
        self.drawContent()
        screen.blit(self.surface, self.pos)

    def drawContent(self):
        # To be overridden by child classes
        pass

    def tick(self, screen):
        self.draw(screen)

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            px, py = self.pos
            if px <= mx <= px + self.width and py <= my <= py + self.height:
                self.dragging = True
                self.dragOffset = (mx - px, my - py)
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mx, my = event.pos
                newX = mx - self.dragOffset[0]
                newY = my - self.dragOffset[1]
                self.setPosition(newX, newY)

class widgetPallettePanel(FloatingPanel):
    def __init__(self, width, height, pos):
        super().__init__(width, height, pos)

        self.fontTitle = pygame.font.Font('resources/outfit.ttf', 40)
        self.fontSmall = pygame.font.Font('resources/outfit.ttf', 35)

    def drawContent(self):
        titleSurface = self.fontTitle.render("Widget Pallette", True, uiData.textColor)
        self.surface.blit(titleSurface, (10, 10))

        for widget in widgets.allWidgets:
            # all widgets is a dictionary with widget names as keys and widget classes as values
            widgetName = widget
            textSurface = self.fontSmall.render(widgetName, True, uiData.textColor)
            self.surface.blit(textSurface, (10, 75 + list(widgets.allWidgets.keys()).index(widgetName) * 60))

    def handleEvent(self, event):
        super().handleEvent(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            px, py = self.pos
            if px <= mx <= px + self.width and py <= my <= py + self.height:
                relativeY = my - py - 75
                index = relativeY // 60
                if 0 <= index < len(widgets.allWidgets):
                    return index

        return None