import pygame
import json
import os
import data.uiData as uiData
import widgets
import components
import time

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

def addWidget(name, widget):
    global screenWidgets
    screenWidgets[name] = widget

screenWidgets = {}

widgetPalette = components.widgetPallettePanel(300, 200, (100, 100))

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((uiData.screenWidth, uiData.screenHeight))
pygame.display.set_caption("TileOS")

clock = pygame.time.Clock()

running = True

draggingWidget = None
dragOffsetPixels = (0, 0)
resizingWidget = None
resizeStartPos = None

editMode = False
editModeHoldTime = .75
mouseDownStartTime = None

while running:
    for event in pygame.event.get():
        # check quit
        if event.type == pygame.QUIT:
            running = False   

        # check normal events 

        if True:
            widgetPaletteOut = widgetPalette.handleEvent(event)
            if widgetPaletteOut is not None:
                addWidget(list(widgets.allWidgets.keys())[widgetPaletteOut].lower(), widgets.allWidgets[list(widgets.allWidgets.keys())[widgetPaletteOut]])

        # check edit mode events
        if True:
            if not widgetPalette.getRect().collidepoint(pygame.mouse.get_pos()):
                if editMode:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = event.pos
                        for widget in screenWidgets.values():
                            wPos = widget.getActualPosition()
                            wSize = widget.getActualSize()
                            resizeHandleSize = 40

                            bottomRight = (wPos[0] + wSize[0], wPos[1] + wSize[1])

                            if (bottomRight[0] - resizeHandleSize <= mx <= bottomRight[0]
                                and bottomRight[1] - resizeHandleSize <= my <= bottomRight[1]):
                                resizingWidget = widget
                                resizeStartPos = (mx + (uiData.cellSize) / 4, my + (uiData.cellSize) / 4)
                                break

                            elif wPos[0] <= mx <= wPos[0] + wSize[0] and wPos[1] <= my <= wPos[1] + wSize[1]:
                                draggingWidget = widget
                                dragOffsetPixels = ((mx - wPos[0]) + uiData.cellSize / 4, (my - wPos[1]) + uiData.cellSize / 4)
                                break

                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        draggingWidget = None
                        resizingWidget = None
                        resizeStartPos = None

                    elif event.type == pygame.MOUSEMOTION:
                        if draggingWidget is not None:
                            mx, my = event.pos
                            newLeft = mx - dragOffsetPixels[0]
                            newTop = my - dragOffsetPixels[1]
                            cellSizeWithPadding = uiData.cellSize + uiData.cellPadding
                            newX = newLeft // cellSizeWithPadding
                            newY = newTop // cellSizeWithPadding
                            newX = max(0, newX)
                            newY = max(0, newY)
                            draggingWidget.setPosition(newX, newY)

                        elif resizingWidget is not None:
                            mx, my = event.pos
                            wPos = resizingWidget.getActualPosition()
                            cellSizeWithPadding = uiData.cellSize + uiData.cellPadding
                            newWidthCells = max(1, (mx - wPos[0]) // cellSizeWithPadding)
                            newHeightCells = max(1, (my - wPos[1]) // cellSizeWithPadding)
                            resizingWidget.setSize(newWidthCells, newHeightCells)

                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_0:
                        addWidget("date", widgets.Date(pos=(0, 0), width=5, height=2))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouseDownStartTime = time.time()
                mouseDownPos = event.pos

            elif event.type == pygame.MOUSEMOTION:
                if mouseDownStartTime is not None:
                    mx, my = event.pos
                    dx = mx - mouseDownPos[0]
                    dy = my - mouseDownPos[1]
                    if abs(dx) > 6 or abs(dy) > 6:
                        mouseDownStartTime = None

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouseDownStartTime = None

    if mouseDownStartTime is not None:
        elapsed = time.time() - mouseDownStartTime
        if elapsed >= editModeHoldTime:
            editMode = not editMode
            mouseDownStartTime = None

    if editMode: 
        screen.fill(uiData.backgroundColorEditMode)
        drawGrid(screen, (50, 50, 50), uiData.cellSize, uiData.cellPadding, uiData.screenWidth, uiData.screenHeight)
    else: 
        screen.fill(uiData.backgroundColor)

    # draw backmost layer

    for widget in screenWidgets.values():
        widget.tick(screen)

        if editMode:
            wPos = widget.getActualPosition()
            wSize = widget.getActualSize()
            pygame.draw.circle(
                screen,
                (180, 180, 180),
                (int(wPos[0] + wSize[0] - 5), int(wPos[1] + wSize[1] - 5)),
                5
            )
    
    # draw frontmost layer
    if editMode:
        widgetPalette.tick(screen)

    pygame.display.flip()
    clock.tick(60)