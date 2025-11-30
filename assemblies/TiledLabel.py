from widgets import *
import data.uiData as uiData

class TiledLabel(Widget):
    name = "Tiled Label"
    preferredSizes = [(3, 1), (6, 2)]
    def __init__(self, width=2, height=1, pos=(0, 2)):
        super().__init__(width, height, pos)
        pygame.font.init()
        self.font = pygame.font.Font('resources/outfit.ttf', 50)

    def drawContent(self):
        text = self.font.render("Tiled", True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(text, textRect)

WIDGET_CLASS = TiledLabel