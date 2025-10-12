import pygame
import time
import data.uiData as uiData

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
        self.width = width
        self.height = height
        self.pos = pos
        self._updateSurface()

    def _updateSurface(self):
        self.surface = pygame.Surface(
            (
                self.width * uiData.cellSize + (self.width - 1) * uiData.cellPadding,
                self.height * uiData.cellSize + (self.height - 1) * uiData.cellPadding
            ),
            pygame.SRCALPHA
        )

    def setSize(self, width, height):
        self.width = width
        self.height = height
        self._updateSurface()

    def setPosition(self, x, y):
        self.pos = (x, y)

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
        screen.blit(self.surface, (x, y))

    def drawContent(self):
        # To be overridden by child classes
        pass

    def tick(self, screen):
        self.draw(screen)
        self._updateSurface()
        self.drawContent()

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