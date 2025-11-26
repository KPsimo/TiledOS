
from widgets import *
import data.uiData as uiData
                
class BouncingBall(Widget):
    name = "Bouncing Ball"
    def __init__(self, width=1, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.radius = min(width, height) * uiData.cellSize // 4 - uiData.cellPadding // 4  # Made smaller
        self.x = self.radius
        self.y = self.radius
        self.dx = 3
        self.dy = 2
        self.color = (255, 255, 255)

    def update(self):
        self.x += self.dx
        self.y += self.dy

        if self.x + self.radius > self.getActualSize()[0]:
            self.x = self.getActualSize()[0] - self.radius
            self.dx = -self.dx
        if self.x - self.radius < 0:
            self.x = self.radius
            self.dx = -self.dx
        if self.y + self.radius > self.getActualSize()[1]:
            self.y = self.getActualSize()[1] - self.radius
            self.dy = -self.dy
        if self.y - self.radius < 0:
            self.y = self.radius
            self.dy = -self.dy

    def drawContent(self):
        pygame.draw.circle(self.surface, self.color, (int(self.x), int(self.y)), self.radius)

WIDGET_CLASS = BouncingBall
