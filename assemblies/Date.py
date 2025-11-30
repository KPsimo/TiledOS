from widgets import *
import data.uiData as uiData

class Date(Widget):
    name = "Date"
    preferredSizes = [(3, 1), (6, 2)]
    def __init__(self, width=3, height=1, pos=(0, 1)):
        super().__init__(width, height, pos)
        self.currentDate = time.localtime()
        self.style = 0

    def update(self):
        self.currentDate = time.localtime()

    def drawContent(self):
        if self.style == 0: dateStr = f"{self.currentDate.tm_year:04}-{self.currentDate.tm_mon:02}-{self.currentDate.tm_mday:02}"
        if self.style == 1: dateStr = f"{self.currentDate.tm_mon:02}/{self.currentDate.tm_mday:02}"
        
        text = self.fonts[int(self.height-1)].render(dateStr, True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        
        self.surface.blit(text, textRect)

WIDGET_CLASS = Date