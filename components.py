import pygame
import math
import data.uiData as uiData
import uiTools
import widgets
import windowTools

# --- Panel Types --- #

class FloatingPanel:
    def __init__(self, width, height, pos):
        self.width = width
        self.height = height
        self.pos = (pos[0], pos[1])

        self.size = width, height

        self.dragging = False
        self.dragOffset = (0, 0)

        # optional overall alpha for the panel (None = unchanged)
        self.global_alpha = None

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
        # ensure the surface matches the new size
        self._updateSurface()

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
        # If a global alpha is set, blit a temporary copy with that alpha
        if self.global_alpha is not None:
            tmp = self.surface.copy()
            tmp.set_alpha(int(self.global_alpha))
            screen.blit(tmp, self.pos)
        else:
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

class CenteredPanel(FloatingPanel):
    def __init__(self, width, height):
        screenWidth, screenHeight = uiData.screenWidth, uiData.screenHeight
        pos = ((screenWidth - width) // 2, (screenHeight - height) // 2)
        super().__init__(width, height, pos)
    
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

    def handleEvent(self, event):
        return None
    
    def setSize(self, width, height):
        super().setSize(width, height)
        screenWidth, screenHeight = uiData.screenWidth, uiData.screenHeight
        self.setPosition((screenWidth - width) // 2, (screenHeight - height) // 2)

class SnappingPanel(widgets.Widget):
    def __init__(self, width, height, pos):
        super().__init__(width, height, pos)

# --- Panels --- #

class widgetPallettePanel(FloatingPanel):
    def __init__(self, width, height, pos):
        super().__init__(width, height, pos)

        self.height = 70 + len(widgets.allWidgets) * 60 + 10
        self._updateSurface()

        self.fontTitle = pygame.font.Font('resources/outfit.ttf', 40)
        self.fontSmall = pygame.font.Font('resources/outfit.ttf', 35)

    def drawContent(self):

        titleSurface = self.fontTitle.render("Widget Pallette", True, uiData.textColor)
        self.surface.blit(titleSurface, (10, 10))

        for widget in widgets.allWidgets:
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
    
class actionPanel(CenteredPanel):
    def __init__(self):
        self.iconSize = 230
        self.icons = {
            "power" : pygame.image.load("resources/icons/power.png").convert_alpha(),
            "edit" : pygame.image.load("resources/icons/edit.png").convert_alpha(),
            "assemble" : pygame.image.load("resources/icons/assemble.png").convert_alpha(),
            "close" : pygame.image.load("resources/icons/close.png").convert_alpha(),
        }
        self.page = "main"

        super().__init__(self.iconSize * len(self.icons), 200)

    def setPage(self, pageName):
        self.page = pageName

        if self.page == "main":
            self.icons = {
                "power" : pygame.image.load("resources/icons/power.png").convert_alpha(),
                "edit" : pygame.image.load("resources/icons/edit.png").convert_alpha(),
                "assemble" : pygame.image.load("resources/icons/assemble.png").convert_alpha(),
                "close" : pygame.image.load("resources/icons/close.png").convert_alpha(),
            }
        elif self.page == "builder":
            self.icons = {
                "power" : pygame.image.load("resources/icons/power.png").convert_alpha(),
                "close" : pygame.image.load("resources/icons/close.png").convert_alpha(),
            }
            newWidth = self.iconSize * len(self.icons)
            self.setSize(newWidth, self.height)

    def drawContent(self):
        xOffset = 0

        for icon in self.icons.values():
            icon = pygame.transform.smoothscale(icon, (self.iconSize, self.iconSize))
            y = (self.height // 2) - (self.iconSize // 2)
            self.surface.blit(icon, (xOffset, y))
            xOffset += self.iconSize

    def tick(self, screen):
        newWidth = self.iconSize * len(self.icons)
        if newWidth != self.width:
            self.setSize(newWidth, self.height)
        self.draw(screen)

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            px, py = self.pos
            sx, sy = self.getSize()
            if px <= mx <= px + sx and py <= my <= py + sy:
                return self.clicked(mx, my)

    def clicked(self, mx, my):
        px, py = self.getPosition()
        relativeX = mx - px

        index = relativeX // self.iconSize

        if self.page == "main":
            if index == 0:
                return "quit"
            elif index == 1:
                return "toggleEdit"
            elif index == 2:
                return "openBuilder"
            elif index == 3:
                return "toggleActionPanel"

            return None
        
        elif self.page == "builder":
            if index == 0:
                return "quit"
            elif index == 1:
                return "toggleActionPanel"

            return None
    
class snappingTitleBar(SnappingPanel):
    def __init__(self, title):
        super().__init__(width=16, height=1, pos=(0, 0))
        self.color = (0, 0, 0, 0)
        self.title = title

    def drawContent(self):
        titleFont = pygame.font.Font('resources/outfit.ttf', 40)
        titleSurface = titleFont.render(self.title, True, uiData.textColor)
        sw, sh = self.surface.get_size()
        tw, th = titleSurface.get_size()
        self.surface.blit(titleSurface, ((sw - tw) // 2, (sh - th) // 2))

class widgetBuilderPanel(SnappingPanel):
    def __init__(self):
        super().__init__(width=16, height=4, pos=(0, 5))
        self.color = (0, 0, 0, 0)

    def drawContent(self):
        titleFont = pygame.font.Font('resources/outfit.ttf', 40)
        titleSurface = titleFont.render("Builder", True, uiData.textColor)
        self.surface.blit(titleSurface, (10, 10))

class textFieldPanel(SnappingPanel):
    def __init__(self, width, height, pos):
        self.width = width
        self.height = height
        self.pos = pos
        self.text = ""
    
        self.color = uiData.widgetBackgroundColor

        pygame.font.init()
        self.font = pygame.font.Font('resources/outfit.ttf', 30)

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def draw(self, screen):
        self.surface.fill((0, 0, 0, 0))
        roundedBg = uiTools.makeRoundedSurface(
            self.surface.get_size(),
            uiData.cornerRadius,
            self.color
        )

        self.surface.blit(roundedBg, (0, 0))

        textSurface = self.font.render(self.text, True, uiData.textColor)
        self.surface.blit(textSurface, (10, 10))

        screen.blit(self.surface, self.pos)

    def tick(self, screen):
        self.draw(screen)

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            px, py = self.pos
            sx, sy = self.getSize()
            if px <= mx <= px + sx and py <= my <= py + sy:
                return self.clicked(mx, my)

    def clicked(self, mx, my):
        self.text = windowTools.getText()
        return self.text