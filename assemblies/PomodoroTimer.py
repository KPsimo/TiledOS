
from widgets import *
import data.uiData as uiData
                
class PomodoroTimer(Widget):
    name = "Pomodoro Timer"
    preferredSizes = [(5, 1)]
    def __init__(self, width=5, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.timerDuration = 300  # 5 minutes in seconds
        self.isActive = False
        self.remainingTime = self.timerDuration
        self.startTime = 0
        self.font = pygame.font.Font('resources/outfit.ttf', 50)

    def update(self):
        if self.isActive:
            elapsed = time.time() - self.startTime
            self.remainingTime = max(0, self.timerDuration - int(elapsed))
            if self.remainingTime == 0:
                self.isActive = False

    def drawContent(self):
        minutes = self.remainingTime // 60
        seconds = self.remainingTime % 60
        timerStr = f"{minutes:01}:{seconds:02}"
        
        text = self.font.render(timerStr, True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        
        self.surface.blit(text, textRect)

    def clicked(self, mx, my):
        if not self.isActive:
            self.isActive = True
            self.startTime = time.time()
            self.remainingTime = self.timerDuration
            
    def reset(self):
        self.isActive = False
        self.remainingTime = self.timerDuration

WIDGET_CLASS = PomodoroTimer
