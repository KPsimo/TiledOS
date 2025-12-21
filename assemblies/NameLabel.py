
from widgets import *
import data.uiData as uiData
                
class NameLabel(Widget):
    name = "Name Label"
    preferredSizes = [(3, 1)]
    
    def __init__(self, width=3, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.labelText = "Ashrit's Tile Pro"

    def update(self):
        pass

    def drawContent(self):
        text = self.fonts[int(self.height-1)].render(self.labelText, True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        
        self.surface.blit(text, textRect)

WIDGET_CLASS = NameLabel
