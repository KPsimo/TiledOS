
from widgets import *
import data.uiData as uiData
                
import pygame
import time

class Timer(Widget):
    name = "Timer"
    preferredSizes = [(2, 1)]
    
    def __init__(self, width=2, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.duration = 90  # total time in seconds (1 minute + 30 seconds)
        self.start_time = time.time()
        self.remaining_time = self.duration
        self.is_running = True

    def update(self):
        if self.is_running:
            elapsed_time = time.time() - self.start_time
            self.remaining_time = max(0, self.duration - elapsed_time)
            if self.remaining_time == 0:
                self.start_time = time.time()  # Reset timer
                self.remaining_time = self.duration

    def drawContent(self):
        if self.remaining_time > 30:
            color = (255, 255, 255)  # White
        else:
            color = (255, 0, 0)  # Red
        
        seconds = int(self.remaining_time % 60)
        minutes = int(self.remaining_time // 60)
        timerStr = f"{minutes:01}:{seconds:02}"
        
        text = self.fonts[int(self.height - 1)].render(timerStr, True, color)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        
        self.surface.blit(text, textRect)

WIDGET_CLASS = Timer
