
from widgets import *
import data.uiData as uiData
                
import random
import time

class Quote(Widget):
    name = "Quote"
    preferredSizes = [(3, 2)]
    
    def __init__(self, width=3, height=2, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.quotes = [
            "The best way to predict the future is to create it.",
            "You only live once, but if you do it right, once is enough.",
            "Success is not the key to happiness. Happiness is the key to success.",
            "Life is 10% what happens to us and 90% how we react to it.",
            "Good things come to people who wait, but better things come to those who go get them."
        ]
        self.currentQuote = self.get_random_quote()
        self.lastUpdate = time.time()

    def update(self):
        currentTime = time.time()
        if currentTime - self.lastUpdate >= 3600:  # Update every hour
            self.currentQuote = self.get_random_quote()
            self.lastUpdate = currentTime

    def get_random_quote(self):
        return random.choice(self.quotes)

    def drawContent(self):
        text = self.fonts[int(self.height * 1.5 - 1)].render(self.currentQuote, True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        
        self.surface.blit(text, textRect)

WIDGET_CLASS = Quote
