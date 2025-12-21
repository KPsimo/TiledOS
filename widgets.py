
import pygame
import time
import data.uiData as uiData
import uiTools
import math
import importlib
import os
import sys

# --- Widget Template --- #

class Widget:
    name = "Widget"
    preferredSizes = [(1, 1)]
    freeSize = True
    def __init__(self, width=1, height=1, pos=(0, 0)):
        # logical target sizes (integers commonly), current animated size stored in self.size
        self.width = width
        self.height = height
        self.pos = (float(pos[0]), float(pos[1]))
        self.posOverridden = False

        # size easing state
        self.size = (float(width), float(height))
        self.targetSize = (float(width), float(height))
        self.sizeSnapped = True

        # position easing state
        self.targetPos = (float(pos[0]), float(pos[1]))
        self.posSnapped = True

        self.easeSpeed = 0.25
        self.snapThreshold = 0.01

        self.color = uiData.widgetBackgroundColor

        pygame.font.init()
        self.fonts = []

        for size in [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]:
            self.fonts.append(pygame.font.Font('resources/outfit.ttf', size))

        self._updateSurface()

    def _updateSurface(self):
        # compute pixel dimensions from current (possibly fractional) logical size
        w_pixels = int(self.size[0] * uiData.cellSize + (self.size[0] - 1) * uiData.cellPadding)
        h_pixels = int(self.size[1] * uiData.cellSize + (self.size[1] - 1) * uiData.cellPadding)
        w_pixels = max(1, w_pixels)
        h_pixels = max(1, h_pixels)

        self.surface = pygame.Surface((w_pixels, h_pixels), pygame.SRCALPHA)

    def getActualSize(self):
        return self.surface.get_size()
    
    def getActualPosition(self):
        if self.posOverridden:
            return self.pos
        else:
            return (
                self.pos[0] * (uiData.cellSize + uiData.cellPadding) + uiData.cellPadding // 2,
                self.pos[1] * (uiData.cellSize + uiData.cellPadding) + uiData.cellPadding // 2
            )

    def getSize(self):
        return (self.width, self.height)
    
    def getPos(self):
        return (int(self.pos[0]), int(self.pos[1]))

    def setSize(self, width, height):
        if not Widget.freeSize:
            best = min(
            self.preferredSizes,
            key=lambda s: abs(s[0] - width) + abs(s[1] - height)
            )

            # snap to that size
            bw, bh = best
            self.width = bw
            self.height = bh
            self.targetSize = (float(bw), float(bh))

        else:
            self.width = width
            self.height = height
            self.targetSize = (float(width), float(height))

        # animate toward it
        self.sizeSnapped = False

    def setPosition(self, x, y):
        self.targetPos = (float(x), float(y))
        self.posSnapped = False
        self.posOverridden = False

    def overrideActualPosition(self, x, y):
        self.pos = (x, y)
        self.targetPos = (x, y)
        self.posSnapped = True
        self.posOverridden = True

    def setColor(self, color):
        self.color = color

    def draw(self, screen):
        if self.color == uiData.widgetBackgroundColorProgression:
            self.surface.fill((0, 0, 0, 0))
            roundedBg = uiTools.makeRoundedSurface(
                self.surface.get_size(),
                uiData.cornerRadius,
                self.color
            )
            self.surface.blit(roundedBg, (0, 0))
            self.drawContent()
            if self.posOverridden:
                x, y = self.pos
            else:
                x = (self.pos[0] * (uiData.cellSize + uiData.cellPadding)) + uiData.cellPadding // 2
                y = (self.pos[1] * (uiData.cellSize + uiData.cellPadding)) + uiData.cellPadding // 2
            screen.blit(self.surface, (int(x), int(y) - 2))
        else:
            self.surface.fill((0, 0, 0, 0))
            roundedBg = uiTools.makeRoundedSurface(
                self.surface.get_size(),
                uiData.cornerRadius,
                self.color
            )
            self.surface.blit(roundedBg, (0, 0))
            self.drawContent()
            if self.posOverridden:
                x, y = self.pos
            else:
                x = (self.pos[0] * (uiData.cellSize + uiData.cellPadding)) + uiData.cellPadding // 2
                y = (self.pos[1] * (uiData.cellSize + uiData.cellPadding)) + uiData.cellPadding // 2
            screen.blit(self.surface, (int(x), int(y)))

    def drawContent(self):
        # To be overridden by child classes
        pass

    def update(self):
        # To be overridden by child classes
        pass

    def tick(self, screen):
        # position easing
        if not self.posOverridden:
            if not self.posSnapped:
                px, py = self.pos
                tx, ty = self.targetPos
                nx = px + (tx - px) * self.easeSpeed
                ny = py + (ty - py) * self.easeSpeed

                if math.hypot(tx - nx, ty - ny) < self.snapThreshold:
                    nx, ny = tx, ty
                    self.posSnapped = True

                self.pos = (nx, ny)

        # size easing
        if not self.sizeSnapped:
            sx, sy = self.size
            tx, ty = self.targetSize
            nx = sx + (tx - sx) * self.easeSpeed
            ny = sy + (ty - sy) * self.easeSpeed

            if math.hypot(tx - nx, ty - ny) < self.snapThreshold:
                nx, ny = tx, ty
                self.sizeSnapped = True

            self.size = (nx, ny)
            # recreate surface to match new size
            self._updateSurface()

        self.update()
        self.draw(screen)

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            px, py = self.getActualPosition()
            sx, sy = self.getActualSize()
            if px <= mx <= px + sx and py <= my <= py + sy:
                self.clicked(mx, my)

    def clicked(self, mx, my):
        # To be overridden by child classes
        pass

# --- Widgets --- #

class Calendar(Widget):
    preferredSizes = [(3, 1), (6, 2)]
    def __init__(self, width=1, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        pygame.font.init()
        self.font = pygame.font.Font('resources/outfit.ttf', 50)

    def drawContent(self):
        text = self.font.render("Calendar", True, uiData.textColor)
        text_rect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(text, text_rect)

class Clock(Widget):
    preferredSizes = [(3, 1), (6, 2)]
    def __init__(self, width=3, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.currentTime = time.localtime()
        self.hours = self.currentTime.tm_hour
        self.minutes = self.currentTime.tm_min
        self.seconds = self.currentTime.tm_sec

    def update(self):
        self.currentTime = time.localtime()
        self.hours = self.currentTime.tm_hour
        self.minutes = self.currentTime.tm_min
        self.seconds = self.currentTime.tm_sec

    def drawContent(self):
        timeStr = f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}"
        text = self.fonts[int(self.height-1)].render(timeStr, True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(text, textRect)

# --- Import Widgets & Assemblies --- #

allWidgets = {
    "Clock": Clock(),
    "Calendar": Calendar()
}

def addWidget(widgetName, widget):
    allWidgets[widgetName] = widget

def loadWidgets():
    widgetsDir = "assemblies"
    sys.path.insert(0, widgetsDir)

    loaded = []
    for file in os.listdir(widgetsDir):
        if not file.endswith(".py"):
            continue

        moduleName = file[:-3]

        try:
            mod = importlib.import_module(moduleName)
            cls = getattr(mod, "WIDGET_CLASS")
            loaded.append(cls())
        except Exception as e:
            print("failed to load", file, e)

    return loaded

loadedWidgets = loadWidgets()
for widget in loadedWidgets:
    addWidget(widget.name, widget)