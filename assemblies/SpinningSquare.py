from widgets import *
import data.uiData as uiData

class SpinningSquare(Widget):
    name = "Spinning Square"
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
    
    def clicked(self, mx, my):
        self.speed += .05

WIDGET_CLASS = SpinningSquare