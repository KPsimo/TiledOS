import pygame
import json
import os
import data.uiData as uiData
import widgets

widgetsPath = os.path.join("data", "widgets.json")

def saveWidgetState(clockWidget, dateWidget):
    state = {
        "clock": {
            "pos": clockWidget.pos,
            "size": [clockWidget.width, clockWidget.height]
        },
        "date": {
            "pos": dateWidget.pos,
            "size": [dateWidget.width, dateWidget.height]
        }
    }
    with open(widgetsPath, "w") as f:
        json.dump(state, f, indent=4)

def drawGrid(surface, color, cellSize, cellPadding, width, height):
    x = 0
    while x <= width - cellSize:
        pygame.draw.line(surface, color, (x, 0), (x, height))
        x += cellSize + cellPadding
    pygame.draw.line(surface, color, (width - 1, 0), (width - 1, height))  # right edge

    y = 0
    while y <= height - cellSize:
        pygame.draw.line(surface, color, (0, y), (width, y))
        y += cellSize + cellPadding
    pygame.draw.line(surface, color, (0, height - 1), (width, height - 1))  # bottom edge

if os.path.exists(widgetsPath):
    with open(widgetsPath, "r") as f:
        state = json.load(f)
    clock_pos = tuple(state.get("clock", {}).get("pos", (0, 0)))
    clock_size = state.get("clock", {}).get("size", [4, 2])
    date_pos = tuple(state.get("date", {}).get("pos", (0, 2)))
    date_size = state.get("date", {}).get("size", [4, 1])
else:
    clock_pos = (0, 0)
    clock_size = [4, 2]
    date_pos = (0, 2)
    date_size = [4, 1]

clockWidget = widgets.Clock(pos=clock_pos, width=clock_size[0], height=clock_size[1])
dateWidget = widgets.Date(pos=date_pos, width=date_size[0], height=date_size[1])

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((uiData.screenWidth, uiData.screenHeight))

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()

            saveWidgetState(clockWidget, dateWidget)

            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_RIGHT:
                clockWidget.setSize(clockWidget.width + 1, clockWidget.height)
            if event.key == pygame.K_LEFT:
                clockWidget.setSize(max(1, clockWidget.width - 1), clockWidget.height)
            elif event.key == pygame.K_UP:
                clockWidget.setSize(clockWidget.width, max(1, clockWidget.height - 1))
            elif event.key == pygame.K_DOWN:
                clockWidget.setSize(clockWidget.width, clockWidget.height + 1)
            if event.key == pygame.K_d:
                clockWidget.setPosition(clockWidget.pos[0] + 1, clockWidget.pos[1])
            if event.key == pygame.K_a:
                clockWidget.setPosition(max(0, clockWidget.pos[0] - 1), clockWidget.pos[1])
            elif event.key == pygame.K_w:
                clockWidget.setPosition(clockWidget.pos[0], max(0, clockWidget.pos[1] - 1))
            elif event.key == pygame.K_s:
                clockWidget.setPosition(clockWidget.pos[0], clockWidget.pos[1] + 1)

    screen.fill(uiData.backgroundColor)
    drawGrid(screen, (50, 50, 50), uiData.cellSize, uiData.cellPadding, uiData.screenWidth, uiData.screenHeight)

    clockWidget.tick(screen)
    dateWidget.tick(screen)

    pygame.display.flip()