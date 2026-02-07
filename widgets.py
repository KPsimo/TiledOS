import pygame
import time
import data.uiData as uiData
import uiTools
import math
import importlib
import os
import sys
import canvasEndpoint
import googleTasksEndpoint
import pandas as pd
import threading

# --- Widget Template --- #

class Widget:
    name = "Widget"
    preferredSizes = [(1, 1)]
    freeSize = True
    def __init__(self, width=1, height=1, pos=(0, 0)):
        # logical target sizes (integers commonly), current animated size stored in self.size
        self.width = width
        self.height = height
        self.pos = (float(pos[0]), float(pos[1]))
        self.posOverridden = False

        # size easing state
        self.size = (float(width), float(height))
        self.targetSize = (float(width), float(height))
        self.sizeSnapped = True

        # position easing state
        self.targetPos = (float(pos[0]), float(pos[1]))
        self.returnPos = self.targetPos
        self.posSnapped = True

        self.easeSpeed = 0.25
        self.snapThreshold = 0.01

        self.color = uiData.widgetBackgroundColor

        pygame.font.init()
        self.fonts = []

        for size in [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]:
            self.fonts.append(pygame.font.Font('resources/outfit.ttf', size))

        self.flashOverlayAlpha = 0

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
        if self.posOverridden:
            return self.pos
        else:
            return (
                self.pos[0] * (uiData.cellSize + uiData.cellPadding) + uiData.cellPadding // 2,
                self.pos[1] * (uiData.cellSize + uiData.cellPadding) + uiData.cellPadding // 2
            )

    def getSize(self):
        return (self.width, self.height)
    
    def getPos(self):
        return (int(self.pos[0]), int(self.pos[1]))

    def setSize(self, width, height):
        if not self.freeSize:
            best = min(
            self.preferredSizes,
            key=lambda s: abs(s[0] - width) + abs(s[1] - height)
            )

            # snap to that size
            bw, bh = best
            self.width = bw
            self.height = bh
            self.targetSize = (float(bw), float(bh))

        else:
            self.width = width
            self.height = height
            self.targetSize = (float(width), float(height))

        # animate toward it
        self.sizeSnapped = False

    def setPosition(self, x, y):
        self.targetPos = (float(x), float(y))
        self.posSnapped = False
        self.posOverridden = False

    def overrideActualPosition(self, x, y):
        self.pos = (x, y)
        self.returnPos = self.targetPos
        self.targetPos = (x, y)
        self.posSnapped = True
        self.posOverridden = True

    def disableOverride(self):
        self.posOverridden = False
        self.targetPos = self.returnPos
        self.posSnapped = False

    def setColor(self, color):
        self.color = color

    def draw(self, screen):
        if self.color == uiData.widgetBackgroundColorProgression:
            self.surface.fill((0, 0, 0, 0))
            roundedBg = uiTools.makeRoundedSurface(
                self.surface.get_size(),
                uiData.cornerRadius,
                self.color,
                outlineWidth=0
            )

            self.surface.blit(roundedBg, (0, 0))

            if uiData.widgetOutlineWidth > 0:
                roundedOutline = uiTools.makeRoundedSurface(
                    self.surface.get_size(),
                    uiData.cornerRadius,
                    uiData.textColor,
                    outlineWidth=uiData.widgetOutlineWidth
                )

                self.surface.blit(roundedOutline, (0, 0))

            self.drawContent()
            if self.posOverridden:
                x, y = self.pos
            else:
                x = (self.pos[0] * (uiData.cellSize + uiData.cellPadding)) + uiData.cellPadding // 2
                y = (self.pos[1] * (uiData.cellSize + uiData.cellPadding)) + uiData.cellPadding // 2
            screen.blit(self.surface, (int(x), int(y) - 2))
        else:
            self.surface.fill((0, 0, 0, 0))
            roundedBg = uiTools.makeRoundedSurface(
                self.surface.get_size(),
                uiData.cornerRadius,
                self.color,
                outlineWidth=0
            )

            self.surface.blit(roundedBg, (0, 0))

            if uiData.widgetOutlineWidth > 0:
                roundedOutline = uiTools.makeRoundedSurface(
                    self.surface.get_size(),
                    uiData.cornerRadius,
                    uiData.textColor,
                    outlineWidth=uiData.widgetOutlineWidth
                )

                self.surface.blit(roundedOutline, (0, 0))

            self.drawContent()

            if self.posOverridden:
                x, y = self.pos
            else:
                x = (self.pos[0] * (uiData.cellSize + uiData.cellPadding)) + uiData.cellPadding // 2
                y = (self.pos[1] * (uiData.cellSize + uiData.cellPadding)) + uiData.cellPadding // 2
            screen.blit(self.surface, (int(x), int(y)))

        if self.flashOverlayAlpha > 0:
            flashOverlay = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
            roundedFlashOverlay = uiTools.makeRoundedSurface(
                flashOverlay.get_size(),
                uiData.cornerRadius,
                (uiData.widgetBackgroundColor[0], uiData.widgetBackgroundColor[1], uiData.widgetBackgroundColor[2], int(self.flashOverlayAlpha)),
                outlineWidth=0
            )
            if self.posOverridden:
                x, y = self.pos
            else:
                x = (self.pos[0] * (uiData.cellSize + uiData.cellPadding)) + uiData.cellPadding // 2
                y = (self.pos[1] * (uiData.cellSize + uiData.cellPadding)) + uiData.cellPadding // 2
            screen.blit(roundedFlashOverlay, (int(x), int(y)))
            self.flashOverlayAlpha -= 40
            if self.flashOverlayAlpha < 0:
                self.flashOverlayAlpha = 0

    def flashTransition(self):
        self.flashOverlayAlpha = 255

    def drawContent(self):
        # To be overridden by child classes
        pass

    def update(self):
        # To be overridden by child classes
        pass

    def tick(self, screen):
        # position easing
        if not self.posOverridden:
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
            # Always update surface during animations for smooth resizing
            self._updateSurface()

        self.update()
        self.draw(screen)

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            px, py = self.getActualPosition()
            sx, sy = self.getActualSize()
            if px <= mx <= px + sx and py <= my <= py + sy:
                self.flashTransition()
                return self.clicked(mx - int(px), my - int(py))
        
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            px, py = self.getActualPosition()
            sx, sy = self.getActualSize()
            if px <= mx <= px + sx and py <= my <= py + sy:
                return self.hovered(mx - int(px), my - int(py))

    def clicked(self, mx, my):
        # To be overridden by child classes
        pass

    def hovered(self, mx, my):
        # To be overridden by child classes
        pass

class DisplayWidget(Widget):
    def __init__(self, width=2, height=2, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.rotation = 0
        self.creating = False

    def drawContent(self):
        # draw a rotating question mark for demonstration
        if self.creating:
            font = pygame.font.Font('resources/outfit.ttf', 30)
            text = font.render("Assembling...", True, uiData.textColor)
            rotatedText = pygame.transform.rotate(text, 0)
            textRect = rotatedText.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
            self.surface.blit(rotatedText, textRect)
        else:
            font = pygame.font.Font('resources/outfit.ttf', 100)
            text = font.render("?", True, uiData.textColor)
            rotatedText = pygame.transform.rotate(text, self.rotation)
            textRect = rotatedText.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
            self.surface.blit(rotatedText, textRect)

    def update(self):
        self.rotation += 5
        if self.rotation >= 360:
            self.rotation = 0

    def setCreating(self, value):
        self.creating = value

# --- Functional Widgets --- #

class Calendar(Widget):
    preferredSizes = [(3, 1), (6, 2)]

    def __init__(self, width=1, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        pygame.font.init()
        self.font = pygame.font.Font('resources/outfit.ttf', 50)

    def drawContent(self):
        text = self.font.render("Calendar", True, uiData.textColor)
        text_rect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(text, text_rect)

    def clicked(self, mx, my):
        uiData.currentPage = "calendar"
        return "openCalendar"

class Clock(Widget):
    preferredSizes = [(3, 1), (6, 2)]
    def __init__(self, width=3, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.currentTime = time.localtime()
        self.hours = self.currentTime.tm_hour
        self.minutes = self.currentTime.tm_min
        self.seconds = self.currentTime.tm_sec
        self.ampm = "AM"

        self.styles = ["hh:mm", "hh:mm:ss", "hh:mm AM/PM", "hh:mm:ss AM/PM"]
        self.style = 0;

    def update(self):
        self.currentTime = time.localtime()
        self.hours = self.currentTime.tm_hour
        self.minutes = self.currentTime.tm_min
        self.seconds = self.currentTime.tm_sec

        # ap/pm logic
        if (self.hours > 12):
            self.hours -= 12
            self.ampm = "PM"
        else:
            self.ampm = "AM"

    def drawContent(self):
        if (self.style == 0):
            timeStr = f"{self.hours:02}:{self.minutes:02}"
        elif (self.style == 1):
            timeStr = f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}"
        elif (self.style == 2):
            timeStr = f"{self.hours:02}:{self.minutes:02} {self.ampm}"
        elif (self.style == 3):
            timeStr = f"{self.hours:02}:{self.minutes:02}:{self.seconds:02} {self.ampm}"
        
        text = self.fonts[int(self.height-1)].render(timeStr, True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(text, textRect)

    def clicked(self, mx, my):
        self.style += 1;
        if self.style >= len(self.styles):
            self.style = 0;

class Stopwatch(Widget):
    preferredSizes = [(2, 1), (4, 2)]
    def __init__(self, width=2, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.startTime = None
        self.elapsedTime = 0
        self.running = False
        self.fadedTextColor = (170, 170, 170)
        self.textColor = self.fadedTextColor

    def start(self):
        if not self.running:
            self.startTime = time.time() - self.elapsedTime
            self.running = True
            self.textColor = uiData.textColor

    def stop(self):
        if self.running:
            self.elapsedTime = time.time() - self.startTime
            self.running = False
            self.textColor = self.fadedTextColor

    def reset(self):
        self.startTime = None
        self.elapsedTime = 0
        self.running = False

    def update(self):
        if self.running:
            self.elapsedTime = time.time() - self.startTime

    def drawContent(self):
        minutes = int(self.elapsedTime // 60)
        seconds = int(self.elapsedTime % 60)
        milliseconds = int((self.elapsedTime - int(self.elapsedTime)) * 100)

        timeStr = f"{minutes:02}:{seconds:02}"
        text = self.fonts[int(self.height-1)].render(timeStr, True, self.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(text, textRect)

        clockCircleRadius = min(self.surface.get_width(), self.surface.get_height()) // 6
        clockCircleCenter = (self.surface.get_width() - clockCircleRadius - 10, clockCircleRadius + 10)
        pygame.draw.circle(self.surface, self.fadedTextColor, clockCircleCenter, clockCircleRadius, 2)
        
        if self.running:
            elapsedFraction = (self.elapsedTime % 30) / 30.0
            endAngle = -math.pi / 2 + elapsedFraction * 2 * math.pi
            pygame.draw.arc(
                self.surface,
                self.fadedTextColor,
                (
                    clockCircleCenter[0] - clockCircleRadius,
                    clockCircleCenter[1] - clockCircleRadius,
                    clockCircleRadius * 2,
                    clockCircleRadius * 2
                ),
                -math.pi / 2,
                endAngle,
                clockCircleRadius
            )

    def clicked(self, mx, my):
        if self.running:
            self.stop()
        else:
            self.start()

class Date(Widget):
    preferredSizes = [(2, 1), (4, 2)]
    def __init__(self, width=2, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.dayOfWeekNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        self.monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

        self.date = time.localtime()

        self.wday = self.dayOfWeekNames[self.date.tm_wday]
        self.day = self.date.tm_mday
        self.month = self.date.tm_mon
        self.monthName = self.monthNames[self.month-1]
        self.year = self.date.tm_year

        self.styles = ["numeric-short", "numeric-long", "textual-short", "textual-normal", "textual-long"]
        self.style = 0

    def drawContent(self):
        if self.style == 0:
            dateStr = f"{self.day}/{self.month}/{self.year}"
        elif self.style == 1:
            dateStr = f"{self.wday}, {self.month}/{self.day}"
        elif self.style == 2:
            dateStr = f"{self.monthName} {self.day}"
        elif self.style == 3:
            dateStr = f"{self.monthName} {self.day}, {self.year}"
        else:
            dateStr = f"{self.wday} {self.monthName} {self.day}, {self.year}"

        text = self.fonts[int(self.height-1)].render(dateStr, True, uiData.textColor)
        textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
        self.surface.blit(text, textRect)

    def clicked(self, mx, my):
        self.style += 1;
        if self.style >= len(self.styles):
            self.style = 0;

class PomodoroTimer(Widget):
    preferredSizes = [(2, 2), (4, 4)]
    def __init__(self, width=2, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.startTime = None
        self.elapsedTime = 0
        self.running = False
        self.textColor = uiData.textColor

        self.totalWorkTime = 20 * 60
        self.totalBreakTime = 5 * 60

        self.workTime = self.totalWorkTime
        self.breakTime = self.totalBreakTime

        self.currentJob = "Work"

        self.startTime = time.time()

        self.fonts = []

        for size in range(10):
            self.fonts.append(pygame.font.Font('resources/outfit.ttf', 70 * size))

        self.titleFonts = []

        for size in range(10):
            self.titleFonts.append(pygame.font.Font('resources/outfit.ttf', 85 * size))

    def update(self):
        elapsedTime = time.time() - self.startTime

        if self.currentJob == "Work":
            self.workTime = self.totalWorkTime - elapsedTime
        
            if self.workTime < 0:
                self.workTime = self.totalWorkTime
                self.currentJob = "Break"
                self.startTime = time.time()

        else:
            self.breakTime = self.totalBreakTime - elapsedTime
        
            if self.breakTime < 0:
                self.breakTime = self.totalBreakTime
                self.currentJob = "Work"
                self.startTime = time.time()


    def drawContent(self):
        if self.currentJob == "Work":
            minutes = int(self.workTime // 60)
            seconds = int(self.workTime % 60)
            timeStr = f"{minutes:02}:{seconds:02}"
        else:
            minutes = int(self.breakTime // 60)
            seconds = int(self.breakTime % 60)
            timeStr = f"{minutes:02}:{seconds:02}"
        
        jobText = self.titleFonts[int(self.height-1)].render(self.currentJob, True, self.textColor)
        jobTextRect = jobText.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 3))
        self.surface.blit(jobText, jobTextRect)

        timeText = self.fonts[int(self.height-1)].render(timeStr, True, self.textColor)
        timeTextRect = timeText.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() - (self.surface.get_height() // 3)))
        self.surface.blit(timeText, timeTextRect)

class StickyNote(Widget):
    preferredSizes = [(2, 2), (4, 4)]
    def __init__(self, width=2, height=2, pos=(0, 0)):
        super().__init__(width, height, pos)
        pygame.font.init()
        self.font = pygame.font.Font('resources/outfit.ttf', 30)
        self.note = "Click to add note."

    def drawContent(self):        
        lines = uiTools.wrapText(self.note, maxCharacters=self.width * 5)
        lineHeight = self.font.get_height()
        totalTextHeight = lineHeight * len(lines)
        startY = (self.surface.get_height() - totalTextHeight) // 2

        for i, line in enumerate(lines):
            text = self.font.render(line, True, uiData.textColor)
            textRect = text.get_rect(center=(self.surface.get_width() // 2, startY + i * lineHeight + lineHeight // 2))
            self.surface.blit(text, textRect)

    def update(self):
        if not self.note:
            self.note = "Click to add note."

    def clicked(self, mx, my):
        return "editNote"

class UpcomingAssignments(Widget):
    assignments = pd.DataFrame()
    fetching = True
    completed = set()

    @staticmethod
    def fetchAssignments():
        UpcomingAssignments.assignments = canvasEndpoint.getAllCurrentAssignments()
        UpcomingAssignments.assignments = UpcomingAssignments.assignments.sort_values(by=['Due Date'])
        UpcomingAssignments.fetching = False

    threading.Thread(target=fetchAssignments, daemon=True).start()

    preferredSizes = [(3, 2), (6, 4)]

    def __init__(self, width=3, height=2, pos=(0, 0)):
        super().__init__(width, height, pos)

        self.titleFonts = []
        self.subtitleFonts = []
        self.buttonFonts = []

        for size in [18, 36, 54, 72, 90, 108, 126, 144, 162, 180]:
            self.titleFonts.append(pygame.font.Font('resources/outfit.ttf', size))
        
        for size in [12, 24, 36, 48, 60, 72, 84, 96, 108, 120]:
            self.subtitleFonts.append(pygame.font.Font('resources/outfit.ttf', size))

        for size in [9, 18, 27, 36, 45, 54, 63, 72, 81, 90]:
            self.buttonFonts.append(pygame.font.Font('resources/outfit.ttf', size))

        self.listFont = pygame.font.Font('resources/outfit.ttf', 28)

        self.loadingArcAngle = 0
        self.loadingArcLength = 200
        self.loadingArcIncreasing = True

        self.highlightedAssignment = None

    def drawContent(self):
        if UpcomingAssignments.assignments.empty:
            if UpcomingAssignments.fetching:
                loadingRadius = min(self.surface.get_width(), self.surface.get_height()) // 6
                loadingCenter = (self.surface.get_width() // 2, self.surface.get_height() // 2)
                endAngle = math.radians(self.loadingArcAngle)
                pygame.draw.arc(
                    self.surface,
                    uiData.textColor,
                    (
                        loadingCenter[0] - loadingRadius,
                        loadingCenter[1] - loadingRadius,
                        loadingRadius * 2,
                        loadingRadius * 2
                    ),
                    math.radians(self.loadingArcAngle),
                    math.radians(self.loadingArcAngle + self.loadingArcLength),
                    4
                )

                return
            else:
                text = self.subtitleFonts[int(self.height-1)].render("All Finished!", True, uiData.textColor)
                textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
                self.surface.blit(text, textRect)

        else:
            if self.highlightedAssignment is None:
                displayAssignments = UpcomingAssignments.assignments.head(math.floor(self.height * 2.5))
                font = self.listFont
                lineHeight = font.get_height() + 5
                startY = (self.surface.get_height() - (lineHeight * len(displayAssignments))) // 2

                for index, row in displayAssignments.iterrows():
                    assignmentStr = f"{row['Name']}"

                    if len(assignmentStr) > 7*self.width:
                        assignmentStr = assignmentStr[:7*int(self.width)] + "..."

                    dueDate = row['Due Date'][:10]

                    textColor = uiData.textColor
                    isCompleted = index in UpcomingAssignments.completed

                    if isCompleted:
                        textColor = (150, 150, 150)
                    elif (dueDate == canvasEndpoint.getCurrentDate()): pass
                    elif (dueDate < canvasEndpoint.getCurrentDate()): textColor = (255, 100, 100)
                    else: textColor = (150, 150, 150)

                    text = font.render(assignmentStr, True, textColor)
                    textRect = text.get_rect(center=(self.surface.get_width() // 2, startY + lineHeight // 2))
                    self.surface.blit(text, textRect)
                    
                    if isCompleted:
                        lineY = textRect.centery
                        thickness = max(1, font.get_height() // 12)
                        pygame.draw.line(self.surface, textColor, (textRect.left, lineY), (textRect.right, lineY), thickness)
                    
                    startY += lineHeight
            
            else:
                titleFont = self.titleFonts[int(self.height-1)]
                subtitleFont = self.subtitleFonts[int(self.height-1)]
                lineHeight = subtitleFont.get_height() + 5
                totalHeight = titleFont.get_height() + (lineHeight * 2)
                startY = (self.surface.get_height() - totalHeight) // 2

                assignmentStr = f"{self.highlightedAssignment['Name']}"
                dueDate = self.highlightedAssignment['Due Date'][:10]
                points = self.highlightedAssignment['Points']

                textColor = uiData.textColor

                wrappedLines = uiTools.wrapText(assignmentStr, maxCharacters=self.width * 3)
                for line in wrappedLines:
                    nameText = titleFont.render(line, True, textColor)
                    nameTextRect = nameText.get_rect(center=(self.surface.get_width() // 2, startY))
                    self.surface.blit(nameText, nameTextRect)
                    startY += lineHeight

                dueDateText = subtitleFont.render(f"Due {dueDate[5:]}", True, (170, 170, 170))
                dueDateTextRect = dueDateText.get_rect(center=(self.surface.get_width() // 2, startY))
                self.surface.blit(dueDateText, dueDateTextRect)
                startY += lineHeight

                pointsText = subtitleFont.render(f"{int(points)} Points", True, (170, 170, 170))
                pointsTextRect = pointsText.get_rect(center=(self.surface.get_width() // 2, startY))
                self.surface.blit(pointsText, pointsTextRect)

                buttonWidth = self.surface.get_width() - self.surface.get_width() // 4
                buttonHeight = self.surface.get_height() // 8
                buttonX = (self.surface.get_width() - buttonWidth) // 2
                buttonY = self.surface.get_height() - buttonHeight - 10
                pygame.draw.rect(
                    self.surface,
                    (50, 50, 50),
                    (buttonX, buttonY, buttonWidth, buttonHeight),
                    border_radius=buttonHeight // 4
                )

                buttonText = self.buttonFonts[int(self.height-1)].render("Complete", True, (255, 255, 255))
                buttonTextRect = buttonText.get_rect(center=(self.surface.get_width() // 2, buttonY + buttonHeight // 2))
                self.surface.blit(buttonText, buttonTextRect)

    def update(self):
        self.loadingArcAngle += 10

        if self.loadingArcIncreasing:
            self.loadingArcLength *= 1.1
            if self.loadingArcLength >= 370:
                self.loadingArcIncreasing = False
        else:
            self.loadingArcLength *= 0.9
            if self.loadingArcLength <= 50:
                self.loadingArcIncreasing = True

    def clicked(self, mx, my):
        if self.highlightedAssignment is None:
            displayAssignments = UpcomingAssignments.assignments.head(math.floor(self.height * 2.5))
            lineHeight = self.listFont.get_height() + 5
            startY = (self.surface.get_height() - (lineHeight * len(displayAssignments))) // 2
            
            clickIndex = (my - startY) // lineHeight

            if 0 <= clickIndex < len(displayAssignments):
                self.highlightedAssignment = UpcomingAssignments.assignments.iloc[clickIndex]

        else:
            buttonWidth = self.surface.get_width() - self.surface.get_width() // 4
            buttonHeight = self.surface.get_height() // 8
            buttonX = (self.surface.get_width() - buttonWidth) // 2
            buttonY = self.surface.get_height() - buttonHeight - 10

            if buttonX <= mx <= buttonX + buttonWidth and buttonY <= my <= buttonY + buttonHeight:
                UpcomingAssignments.completed.add(self.highlightedAssignment.name)
            
            self.highlightedAssignment = None

class Taskboard(Widget):
    preferredSizes = [(4, 3), (8, 6)]
    def __init__(self, width=4, height=3, pos=(0, 0)):
        super().__init__(width, height, pos)

        self.subtitleFonts = []

        for size in [12, 24, 36, 48, 60, 72, 84, 96, 108, 120]:
            self.subtitleFonts.append(pygame.font.Font('resources/outfit.ttf', size))

        self.font = pygame.font.Font('resources/outfit.ttf', 28)
        
        self.tasksToDo = googleTasksEndpoint.getTasksList()
        self.tasksCompleted = []

    def drawContent(self):
        if len(self.tasksToDo) == 0 and len(self.tasksCompleted) == 0:
                text = self.subtitleFonts[int(self.height)-1].render("No Tasks", True, uiData.textColor)
                textRect = text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
                self.surface.blit(text, textRect)
                return
        else:
            todoLines = self.tasksToDo
            doneLines = self.tasksCompleted

            lineHeight = self.font.get_height() + 5
            lotalLines = len(todoLines) + len(doneLines)
            startY = (self.surface.get_height() - (lineHeight * lotalLines)) // 2

            for i, line in enumerate(todoLines):
                text = self.font.render(line, True, uiData.textColor)
                textRect = text.get_rect(center=(self.surface.get_width() // 2, startY + i * lineHeight + lineHeight // 2))
                self.surface.blit(text, textRect)

            fadedColor = (150, 150, 150)
            for j, line in enumerate(doneLines):
                idx = len(todoLines) + j
                text = self.font.render(line, True, fadedColor)
                textRect = text.get_rect(center=(self.surface.get_width() // 2, startY + idx * lineHeight + lineHeight // 2))
                self.surface.blit(text, textRect)

                lineY = textRect.centery
                thickness = max(1, self.font.get_height() // 12)
                pygame.draw.line(self.surface, fadedColor, (textRect.left, lineY), (textRect.right, lineY), thickness)

    def clicked(self, mx, my):
        lineHeight = self.font.get_height() + 5
        lotalLines = len(self.tasksToDo) + len(self.tasksCompleted)
        startY = (self.surface.get_height() - (lineHeight * lotalLines)) // 2

        clickIndex = (my - startY) // lineHeight

        if 0 <= clickIndex < len(self.tasksToDo):
            task = self.tasksToDo.pop(clickIndex)
            self.tasksCompleted.append(task)
        elif len(self.tasksToDo) <= clickIndex < lotalLines:
            task = self.tasksCompleted.pop(clickIndex - len(self.tasksToDo))
            self.tasksToDo.append(task)

# --- Import Widgets & Assemblies --- #

allWidgets = {}

def reloadWidgets():
    global allWidgets

    allWidgets = {
        "Clock": Clock(),
        "Calendar": Calendar(),
        "Stopwatch": Stopwatch(),
        "Date": Date(),
        "Pomodoro Timer": PomodoroTimer(),
        "Sticky Note": StickyNote(),
        "Upcoming": UpcomingAssignments(),
        "Taskboard": Taskboard()
    }

    def addWidget(widgetName, widget):
        allWidgets[widgetName] = widget

    def loadWidgets():
        widgetsDir = "assemblies"
        sys.path.insert(0, widgetsDir)

        loaded = []
        for file in os.listdir(widgetsDir):
            if not file.endswith(".py"):
                continue

            moduleName = file[:-3]

            try:
                mod = importlib.import_module(moduleName)
                cls = getattr(mod, "WIDGET_CLASS")
                loaded.append(cls())
            except Exception as e:
                print("failed to load", file, e)

        return loaded

    loadedWidgets = loadWidgets()
    for widget in loadedWidgets:
        addWidget(widget.name, widget)

reloadWidgets()