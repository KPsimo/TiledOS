import pygame
import time
import data.uiData as uiData
import uiTools
import math

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
        return (
            self.pos[0] * (uiData.cellSize + uiData.cellPadding) + uiData.cellPadding // 2,
            self.pos[1] * (uiData.cellSize + uiData.cellPadding) + uiData.cellPadding // 2
        )

    def getSize(self):
        return (self.width, self.height)
    
    def getPos(self):
        return (int(self.pos[0]), int(self.pos[1]))

    def setSize(self, width, height):
        self.targetSize = (float(width), float(height))
        self.width = width
        self.height = height
        self.sizeSnapped = False

    def setPosition(self, x, y):
        self.targetPos = (float(x), float(y))
        self.posSnapped = False

    def setColor(self, color):
        self.color = color

    def draw(self, screen):
        self.surface.fill((0, 0, 0, 0))
        roundedBg = uiTools.makeRoundedSurface(
            self.surface.get_size(),
            uiData.cornerRadius,
            self.color
        )
        self.surface.blit(roundedBg, (0, 0))
        self.drawContent()
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

# --- Widgets --- #

class Clock(Widget):
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

# --- Assemblies (AI Generated Widgets) --- #

class Date(Widget):
    def __init__(self, width=3, height=1, pos=(0, 1)):
        super().__init__(width, height, pos)
        self.currentDate = time.localtime()

    def update(self):
        self.currentDate = time.localtime()

    def drawContent(self):
        dateStr = f"{self.currentDate.tm_year:04}-{self.currentDate.tm_mon:02}-{self.currentDate.tm_mday:02}"
        text = self.fonts[int(self.height-1)].render(dateStr, True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(text, textRect)

class TiledLabel(Widget):
    def __init__(self, width=2, height=1, pos=(0, 2)):
        super().__init__(width, height, pos)
        pygame.font.init()
        self.font = pygame.font.Font('resources/outfit.ttf', 50)

    def drawContent(self):
        text = self.font.render("Tiled", True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(text, textRect)

class SpinningSquare(Widget):
    def __init__(self, width=1, height=1, pos=(0, 3), color=None, speed=0.06, size_ratio=0.6):
        super().__init__(width, height, pos)
        self.speed = float(speed)           # degrees per millisecond
        self.size_ratio = float(size_ratio) # fraction of widget area used by square
        self.angle = 0.0
        self.square_color = color if color is not None else uiData.textColor

    def drawContent(self):
        # update angle based on global ticks so it rotates even without explicit update() calls
        self.angle = (pygame.time.get_ticks() * self.speed) % 360

        sw, sh = self.surface.get_size()
        side = max(1, int(min(sw, sh) * self.size_ratio))

        # create square surface and draw filled rounded rect
        sq = pygame.Surface((side, side), pygame.SRCALPHA)
        pygame.draw.rect(sq, self.square_color, sq.get_rect(), border_radius=max(1, side // 8))

        # rotate and blit centered
        rotated = pygame.transform.rotate(sq, self.angle)
        rrect = rotated.get_rect(center=(sw // 2, sh // 2))
        self.surface.blit(rotated, rrect)

allWidgets = {
    "Clock": Clock(),
    "Date": Date(),
    "Label": TiledLabel(),
    "Spinning Square": SpinningSquare()
}