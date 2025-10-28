import pygame
import time
import data.uiData as uiData
import math

# -- Helper Functions -- #

def makeRoundedSurface(size, radius, color):
    scale = 3
    big = pygame.Surface((size[0] * scale, size[1] * scale), pygame.SRCALPHA)
    big.fill((0, 0, 0, 0))
    pygame.draw.rect(big, color, big.get_rect(), border_radius=radius * scale)
    return pygame.transform.smoothscale(big, size)

# --- Widget Template --- #

class Widget:
    def __init__(self, width=1, height=1, pos=(0, 0)):
        # logical target sizes (integers commonly), current animated size stored in self.size
        self.width = width
        self.height = height
        self.pos = (float(pos[0]), float(pos[1]))

        # size easing state
        self.size = (float(width), float(height))
        self.targetSize = (float(width), float(height))
        self.sizeSnapped = True

        # position easing state
        self.targetPos = (float(pos[0]), float(pos[1]))
        self.posSnapped = True

        self.easeSpeed = 0.25
        self.snapThreshold = 0.01

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
        return (
            self.pos[0] * (uiData.cellSize + uiData.cellPadding) + uiData.cellPadding // 2,
            self.pos[1] * (uiData.cellSize + uiData.cellPadding) + uiData.cellPadding // 2
        )

    def setSize(self, width, height):
        self.targetSize = (float(width), float(height))
        self.width = width
        self.height = height
        self.sizeSnapped = False

    def setPosition(self, x, y):
        self.targetPos = (float(x), float(y))
        self.posSnapped = False

    def draw(self, screen):
        self.surface.fill((0, 0, 0, 0))
        roundedBg = makeRoundedSurface(
            self.surface.get_size(),
            uiData.cornerRadius,
            uiData.widgetBackgroundColor
        )
        self.surface.blit(roundedBg, (0, 0))
        self.drawContent()
        x = (self.pos[0] * (uiData.cellSize + uiData.cellPadding)) + uiData.cellPadding // 2
        y = (self.pos[1] * (uiData.cellSize + uiData.cellPadding)) + uiData.cellPadding // 2
        screen.blit(self.surface, (int(x), int(y)))

    def drawContent(self):
        # To be overridden by child classes
        pass

    def tick(self, screen):
        # position easing
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

        self.draw(screen)

# --- Widgets --- #

class Clock(Widget):
    def __init__(self, width=3, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.currentTime = time.localtime()
        self.hours = self.currentTime.tm_hour
        self.minutes = self.currentTime.tm_min
        self.seconds = self.currentTime.tm_sec
        pygame.font.init()
        self.fontSmall = pygame.font.Font('resources/outfit.ttf', 50)

    def update(self):
        self.currentTime = time.localtime()
        self.hours = self.currentTime.tm_hour
        self.minutes = self.currentTime.tm_min
        self.seconds = self.currentTime.tm_sec

    def drawContent(self):
        timeStr = f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}"
        text = self.fontSmall.render(timeStr, True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(text, textRect)

# --- Assemblies (AI Generated Widgets) --- #

class Date(Widget):
    def __init__(self, width=3, height=1, pos=(0, 1)):
        super().__init__(width, height, pos)
        self.currentDate = time.localtime()
        pygame.font.init()
        self.fontSmall = pygame.font.Font('resources/outfit.ttf', 50)

    def update(self):
        self.currentDate = time.localtime()

    def drawContent(self):
        dateStr = f"{self.currentDate.tm_year:04}-{self.currentDate.tm_mon:02}-{self.currentDate.tm_mday:02}"
        text = self.fontSmall.render(dateStr, True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(text, textRect)