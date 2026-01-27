import sys
import breakGuard

if not breakGuard.checkAllSecrets():
    print("Exiting due to missing files.")
    sys.exit()

import pygame
import json
import os
import data.uiData as uiData
import uiTools
import widgets
import components
import time
import windowTools
import widgetBuilder
import data.uiData as uiData
import testAssembly

widgetsPath = os.path.join("data", "widgets.json")

def addWidget(name, widget):
    global screenWidgets
    screenWidgets[name] = widget

def saveWidgetsState():
    state = {}

    for name, widget in screenWidgets.items():
        state[name] = {
            "pos": widget.getPos(),
            "width": widget.getSize()[0],
            "height": widget.getSize()[1]
        }

    with open(widgetsPath, "w") as f:
        json.dump(state, f, indent=4)

def loadWidgetsState():
    try:
        with open(widgetsPath, "r") as f:
            savedState = json.load(f)
            for name, state in savedState.items():
                widget = widgets.allWidgets[name]
                widget.setPosition(state["pos"][0], state["pos"][1])
                widget.setSize(state["width"], state["height"])
                addWidget(name, widget)
    except:
        pass

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

def checkCollision(testWidget, newPos, newSize):
    testRect = pygame.Rect(newPos[0], newPos[1], newSize[0], newSize[1])
    
    for widget in screenWidgets.values():
        if widget == testWidget:
            continue
        widgetRect = pygame.Rect(widget.pos[0], widget.pos[1], widget.width, widget.height)
        if testRect.colliderect(widgetRect):
            return True
    return False

def reloadWidgets():
    global screenWidgets
    screenWidgets = {}
    loadWidgetsState()

def minimize():
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    if sys.platform == "win32":
        user32.ShowWindow(hwnd, SW_MINIMIZE)

def maximize():
    pygame.display.set_mode((uiData.screenWidth, uiData.screenHeight), pygame.FULLSCREEN)
    if sys.platform == "win32":
        user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetForegroundWindow(hwnd)

screenWidgets = {}

loadWidgetsState()

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((uiData.screenWidth, uiData.screenHeight), pygame.FULLSCREEN)
pygame.display.set_caption("TiledOS")

if sys.platform == "win32":
    import ctypes
    hwnd = pygame.display.get_wm_info()["window"]
    user32 = ctypes.windll.user32
    SW_MINIMIZE = 6
    SW_RESTORE = 9

clock = pygame.time.Clock()

if __name__ == "__main__":
    bgPath = os.path.join("resources", "backgrounds", "default-dark.jpg")
    useBgColor = False
    showGrid = False

    actionPanel = components.actionPanel()
    widgetPalette = components.widgetPallettePanel(300, 200, (100, 100))

    widgetPalette.setLoadedWidgets(screenWidgets)

    builderTitleBar = components.snappingTitleBar("Create Assembly")
    builderPanel = components.widgetBuilderPanel()

    builderNameInput = components.textFieldPanel(1100, 110, (-1, 550), fontSize=60, hint="Widget Name")
    builderDescriptionInput = components.textFieldPanel(1100, 250, (-1, 680), fontSize=40, hint="Widget Description")

    builderAssembleButton = components.button("Assemble", 1100, 90, (-1, 950), fontSize=60)

    running = True

    draggingWidget = None
    dragOffsetPixels = (0, 0)
    resizingWidget = None
    resizeStartPos = None

    editMode = False

    showActionPanel = False
    actionPanelHoldTime = .75
    mouseDownStartTime = None

    tEditModeBackgroundColor = 0

    tActionPanelOpacity = 0

    displayWidget = widgets.DisplayWidget(width=2, height=2)

    bg = pygame.image.load(bgPath)
    bg = pygame.transform.scale(bg, (uiData.screenWidth, uiData.screenHeight))

    jobsToDo = []

    while running:
        screen.blit(bg, (0, 0))

        if uiData.currentPage == "main":
            for event in pygame.event.get():
                # check quit
                if event.type == pygame.QUIT:
                    running = False   

                # check normal events 
                if True:
                    # always active events
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                        editMode = not editMode
                        if not editMode:
                            saveWidgetsState()

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                        uiData.currentPage = "builder"
                        actionPanel.setPage("builder")

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        showActionPanel = not showActionPanel

                    if showActionPanel:
                        actionPanelOut = actionPanel.handleEvent(event)
                        if actionPanelOut == "quit":
                            running = False
                        
                        elif actionPanelOut == "toggleEdit":
                            editMode = not editMode
                            if not editMode:
                                saveWidgetsState()
                            showActionPanel = not showActionPanel

                        elif actionPanelOut == "openBuilder":
                            uiData.currentPage = "builder"
                            actionPanel.setPage("builder")
                            showActionPanel = not showActionPanel

                        elif actionPanelOut == "toggleActionPanel":
                            showActionPanel = not showActionPanel

                    # not edit mode events
                    if not editMode:
                        for widget in screenWidgets.values():
                            if widget != "Sticky Note":
                                widget.handleEvent(event)

                        if "Sticky Note" in screenWidgets:
                            stickyNoteOut = screenWidgets["Sticky Note"].handleEvent(event)

                            if stickyNoteOut:
                                newText = windowTools.getText()
                                screenWidgets["Sticky Note"].note = newText
                    # edit mode events
                    if editMode:
                        widgetPaletteOut = widgetPalette.handleEvent(event)
                        if widgetPaletteOut is not None:
                            widgetName = list(widgets.allWidgets.keys())[widgetPaletteOut]
                            if widgetName in screenWidgets:
                                del screenWidgets[widgetName]
                            else:
                                addWidget(widgetName, widgets.allWidgets[list(widgets.allWidgets.keys())[widgetPaletteOut]])



                # check edit mode events
                if True:
                    widgetPalette.setLoadedWidgets(screenWidgets)

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
                                        resizeStartPos = (mx - uiData.cellSize, my - uiData.cellSize)
                                        break

                                    elif wPos[0] <= mx <= wPos[0] + wSize[0] and wPos[1] <= my <= wPos[1] + wSize[1]:
                                        draggingWidget = widget
                                        dragOffsetPixels = ((mx - wPos[0]) - uiData.cellSize/2, (my - wPos[1]) - uiData.cellSize/2)
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
                                    if not checkCollision(draggingWidget, (newX, newY), (draggingWidget.width, draggingWidget.height)):
                                        draggingWidget.setPosition(newX, newY)

                                elif resizingWidget is not None:
                                    mx, my = event.pos
                                    mx += uiData.cellSize // 2
                                    my += uiData.cellSize // 2
                                    wPos = resizingWidget.getActualPosition()
                                    cellSizeWithPadding = uiData.cellSize + uiData.cellPadding
                                    newWidthCells = max(1, (mx - wPos[0]) // cellSizeWithPadding)
                                    newHeightCells = max(1, (my - wPos[1]) // cellSizeWithPadding)
                                    if not checkCollision(resizingWidget, (resizingWidget.pos[0], resizingWidget.pos[1]), (newWidthCells, newHeightCells)):
                                        resizingWidget.setSize(newWidthCells, newHeightCells)

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

            if editMode and tEditModeBackgroundColor < 1: tEditModeBackgroundColor += 0.2
            elif not editMode and tEditModeBackgroundColor > 0: tEditModeBackgroundColor -= 0.2

            if tEditModeBackgroundColor < 0: tEditModeBackgroundColor = 0

            if useBgColor: screen.fill(
                uiTools.interpolateColors(uiData.backgroundColor,
                                        uiData.backgroundColorEditMode,
                                        tEditModeBackgroundColor))

            if tEditModeBackgroundColor > 0:
                drawGrid(screen, uiTools.interpolateColors(
                    (50, 50, 50, 255),
                    uiData.backgroundColor,
                    tEditModeBackgroundColor), uiData.cellSize, uiData.cellPadding, uiData.screenWidth, uiData.screenHeight)

            if draggingWidget is not None: draggingWidget.setColor(uiData.widgetBackgroundColorProgression)
            elif resizingWidget is not None: resizingWidget.setColor(uiData.widgetBackgroundColorProgression)

            if draggingWidget is None and resizingWidget is None:
                for widget in screenWidgets.values():
                    widget.setColor(uiData.widgetBackgroundColor)

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
            
            if editMode: widgetPalette.tick(screen)        
        
        elif uiData.currentPage == "builder":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    showActionPanel = not showActionPanel
                
                if showActionPanel:
                        actionPanelOut = actionPanel.handleEvent(event)
                        if actionPanelOut == "quit":
                            running = False
                        
                        elif actionPanelOut == "toggleActionPanel":
                            showActionPanel = not showActionPanel

                        elif actionPanelOut == "back":
                            uiData.currentPage = "main"
                            actionPanel.setPage("main")
                            reloadWidgets()
                            showActionPanel = not showActionPanel
                else:
                    builderNameInput.handleEvent(event)
                    builderDescriptionInput.handleEvent(event)
                    if builderAssembleButton.handleEvent(event) == "clicked":
                        widgetName = builderNameInput.getText()
                        widgetDescription = builderDescriptionInput.getText()
                        if widgetName != "" and widgetDescription != "":
                            if "assembleWidget" not in jobsToDo:
                                jobsToDo.append("assembleWidget")
                            
            

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouseDownStartTime = time.time()
                    mouseDownPos = event.pos

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    mouseDownStartTime = None

            if useBgColor: screen.fill(uiData.backgroundColor)
            # builderPanel.tick(screen)
            builderTitleBar.tick(screen)
            
            if "assembleWidget" in jobsToDo:
                widgetBuilder.buildAssembly(widgetDescription, widgetName)
                displayWidget.setCreating(False)
                reloadWidgets()
                widgets.reloadWidgets()
                widgetPalette.reloadHeight()
                
                testErrors = Exception("Initial")

                while testErrors:
                    testErrors = testAssembly.runAllTests()

                    if testErrors:
                        widgetBuilder.fixAssemblyError(testErrors, widgetName)

                jobsToDo.remove("assembleWidget")

            if "assembleWidget" in jobsToDo:
                displayWidget.setCreating(True)

            builderNameInput.tick(screen)
            builderDescriptionInput.tick(screen)
            builderAssembleButton.tick(screen)

            displayWidget.overrideActualPosition((uiData.screenWidth - displayWidget.getActualSize()[0]) // 2, 240)
            displayWidget.tick(screen)

        elif uiData.currentPage == "calendar":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    uiData.currentPage = "main"

            screen.fill((10, 10, 10))
            font = pygame.font.Font('resources/outfit.ttf', 80)
            text = font.render("CALENDAR SCREEN", True, uiData.textColor)
            screen.blit(text, (80, 80))

        # Always active 
        if mouseDownStartTime is not None:
                elapsed = time.time() - mouseDownStartTime
                if elapsed >= actionPanelHoldTime:
                    if editMode: editMode = not editMode
                    else: showActionPanel = not showActionPanel
                    if not editMode: saveWidgetsState()
                    mouseDownStartTime = None

        if showActionPanel and tActionPanelOpacity < 1: tActionPanelOpacity += 0.2
        elif not showActionPanel and tActionPanelOpacity > 0: tActionPanelOpacity -= 0.2

        if tActionPanelOpacity < 0: tActionPanelOpacity = 0
        
        if tActionPanelOpacity > 0:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill(uiTools.interpolateColors((0, 0, 0, 0),
                                                (0, 0, 0, 200),
                                                tActionPanelOpacity))

            screen.blit(overlay, (0, 0))
        
        if showActionPanel: actionPanel.tick(screen)

        pygame.display.flip()
        clock.tick(60)