import sys
import breakGuard
import argparse

parser = argparse.ArgumentParser(description="Tiled")

parser.add_argument("--user", type=str, default="dev", help="use \'client\' as a user, \'dev\' as a developer")

args = parser.parse_args()

if args.user == "dev": print("Running as developer")

if not breakGuard.checkAllSecrets():
    print("Exiting due to missing files.")
    sys.exit()

import pygame
import json
import os
import uiTools
import widgets
import components
import time
import windowTools
import widgetBuilder
import data.uiData as uiData
import testAssembly
import googleCalendarEndpoint
import threading
import calendar as pycal
import datetime as dt
from datetime import date

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
    #loaded before widgets.allWidgets
    except Exception as e:
        print(f"Error loading widgets state: {e}")

def drawGrid(surface, color, cellSize, cellPadding, width, height):
    """Draw grid more efficiently using pygame.draw.lines instead of individual line calls"""
    cellSizeWithPadding = cellSize + cellPadding
    
    # Vertical lines
    x = 0
    while x <= width:
        pygame.draw.line(surface, color, (x, 0), (x, height), 1)
        x += cellSizeWithPadding
    pygame.draw.line(surface, color, (width - 1, 0), (width - 1, height), 1)
    
    # Horizontal lines
    y = 0
    while y <= height:
        pygame.draw.line(surface, color, (0, y), (width, y), 1)
        y += cellSizeWithPadding
    pygame.draw.line(surface, color, (0, height - 1), (width, height - 1), 1)

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
actualScreen = pygame.display.set_mode((1366, 768))
screen = pygame.Surface((uiData.screenWidth, uiData.screenHeight))
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
    today = date.today()
    uiData.cal_year = today.year
    uiData.cal_month = today.month


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
    
    # Pre-create overlay surface for reuse
    overlay_surface = pygame.Surface((uiData.screenWidth, uiData.screenHeight), pygame.SRCALPHA)
    last_overlay_opacity = -1  # Track last opacity to know when to update

    while running:
        # Always draw the same background image for ALL pages (main + calendar + builder)
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
                        for name, widget in screenWidgets.items():
                            if name != "Sticky Note":
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
                                        # Store initial widget dimensions and mouse position to resize calculation
                                        resizeStartPos = (mx, my, widget.width, widget.height)
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

                                elif resizingWidget is not None and resizeStartPos is not None:
                                    mx, my = event.pos
                                    startMouseX, startMouseY, startWidth, startHeight = resizeStartPos
                                    
                                    # mouse delta in pixels
                                    deltaX = mx - startMouseX
                                    deltaY = my - startMouseY
                                    
                                    # Convert pixel delta -> cell delta
                                    cellSizeWithPadding = uiData.cellSize + uiData.cellPadding
                                    widthDelta = round(deltaX / cellSizeWithPadding)
                                    heightDelta = round(deltaY / cellSizeWithPadding)
                                    
                                    # Calculate new dimensions (minimum 1 cell)
                                    newWidthCells = max(1, startWidth + widthDelta)
                                    newHeightCells = max(1, startHeight + heightDelta)
                                    
                                    # Check collision + update size
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
            # BAN edits in calendar page
            editMode = False
            showActionPanel = False
            mouseDownStartTime = None

            # Responsive layout
            W, H = uiData.screenWidth, uiData.screenHeight

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        uiData.currentPage = "main"

                    # Month navigation
                    elif event.key == pygame.K_LEFT:
                        uiData.cal_month -= 1
                        if uiData.cal_month < 1:
                            uiData.cal_month = 12
                            uiData.cal_year -= 1

                    elif event.key == pygame.K_RIGHT:
                        uiData.cal_month += 1
                        if uiData.cal_month > 12:
                            uiData.cal_month = 1
                            uiData.cal_year += 1

                # Month navigation by clicking on both sides
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos

                    # left 15% of screen = previous month, right 15% = next month
                    if mx < W * 0.15:
                        uiData.cal_month -= 1
                        if uiData.cal_month < 1:
                            uiData.cal_month = 12
                            uiData.cal_year -= 1

                    elif mx > W * 0.85:
                        uiData.cal_month += 1
                        if uiData.cal_month > 12:
                            uiData.cal_month = 1
                            uiData.cal_year += 1

            # !!! Don't screen.fill() here
            # screen.fill((10, 10, 10))

            # Responsive layout
            margin_x = max(16, int(W * 0.02))   # ~2% of width
            margin_bottom = max(16, int(H * 0.02))

            title_font = pygame.font.Font("resources/outfit.ttf", max(34, int(H * 0.06)))
            day_font   = pygame.font.Font("resources/outfit.ttf", max(18, int(H * 0.028)))
            num_font   = pygame.font.Font("resources/outfit.ttf", max(16, int(H * 0.026)))

            # Title (top-left)
            month_name = pycal.month_name[uiData.cal_month]
            title_surf = title_font.render(f"{month_name} {uiData.cal_year}", True, uiData.textColor)
            title_x = margin_x
            title_y = max(8, int(H * 0.01))
            screen.blit(title_surf, (title_x, title_y))

            # Reserve header space so nothing overlaps
            title_h = title_surf.get_height()
            header_gap = max(10, int(H * 0.01))
            weekday_h = day_font.get_height()

            grid_top = title_y + title_h + header_gap + weekday_h + 8

            # Grid area is the rest of the screen
            grid_right = W - margin_x
            grid_bottom = H - margin_bottom
            grid_w = grid_right - margin_x
            grid_h = grid_bottom - grid_top

            cols, rows = 7, 6
            cell_w = grid_w // cols
            cell_h = grid_h // rows

            # Recompute exact grid size and center it horizontally to avoid right clipping
            actual_grid_w = cell_w * cols
            grid_x = (W - actual_grid_w) // 2
            grid_x = max(0, grid_x)

            # Weekday headers (Monday start)
            weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            weekday_y = grid_top - weekday_h - 6
            for i, wd in enumerate(weekdays):
                wd_surf = day_font.render(wd, True, uiData.textColor)
                screen.blit(wd_surf, (grid_x + i * cell_w + 10, weekday_y))

            # Calendar matrix with spillover dates (Monday start)
            cal = pycal.Calendar(firstweekday=0)  # Monday
            month_days = cal.monthdatescalendar(uiData.cal_year, uiData.cal_month)  # real dates incl prev/next month

            # Force EXACTLY 6 rows so the calendar size never changes
            while len(month_days) < 6:
                last_day = month_days[-1][-1]  # last date in current grid
                next_week = [last_day + dt.timedelta(days=i) for i in range(1, 8)]
                month_days.append(next_week)
            month_days = month_days[:6]

            pad = max(2, min(8, int(min(cell_w, cell_h) * 0.06)))  # scales with cell size

            for row, week in enumerate(month_days):
                for col, day in enumerate(week):
                    x = grid_x + col * cell_w
                    y = grid_top + row * cell_h

                    in_current_month = (day.month == uiData.cal_month)

                    # remi-transparent cell cards (spillover more transparent) 
                    alpha = 240 if in_current_month else 190  # tweak: current 130-160, spillover 60-100

                    card_w = cell_w - pad * 2
                    card_h = cell_h - pad * 2

                    cell_surface = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                    # rounded corners + alpha
                    pygame.draw.rect(
                        cell_surface,
                        (50, 50, 50, alpha),
                        (0, 0, card_w, card_h),
                        border_radius=10
                    )
                    screen.blit(cell_surface, (x + pad, y + pad))

                    # text labels 
                    if in_current_month:
                        text_color = uiData.textColor
                        label = str(day.day)
                    else:
                        text_color = (160, 160, 160)
                        # show "Aug 1" / "Sep 1" on month boundary like your screenshot
                        if day.day == 1:
                            label = f"{day.strftime('%b')} {day.day}"
                        else:
                            label = str(day.day)

                    num_surf = num_font.render(label, True, text_color)
                    screen.blit(num_surf, (x + pad + 6, y + pad + 6))

                # --- Simple white chevron navigation arrows (inside grid, not on cells) ---
                hint_surface = pygame.Surface((W, H), pygame.SRCALPHA)

                # Vertically center on the grid
                arrow_cy = grid_top + (rows * cell_h) // 2

                # Chevron sizing
                arrow_size = max(18, int(min(W, H) * 0.018))
                arrow_thickness = 6

                # Solid white
                arrow_color = (255, 255, 255, 255)

                # Grid bounds
                grid_left  = grid_x
                grid_right = grid_x + (cols * cell_w)

                # Card bounds (cards inset by pad)
                first_card_left = grid_left + pad
                last_card_right = grid_right - pad

                # Place arrows in the gutter between grid edge and cards
                left_x = grid_left + (first_card_left - grid_left) * 1 // 4
                right_x = grid_right - (grid_right - last_card_right) * 1 // 4

                # LEFT chevron  <
                pygame.draw.lines(
                    hint_surface,
                    arrow_color,
                    False,
                    [
                        (left_x + arrow_size // 2, arrow_cy - arrow_size // 2),
                        (left_x - arrow_size // 2, arrow_cy),
                        (left_x + arrow_size // 2, arrow_cy + arrow_size // 2),
                    ],
                    arrow_thickness
                )

                # RIGHT chevron  >
                pygame.draw.lines(
                    hint_surface,
                    arrow_color,
                    False,
                    [
                        (right_x - arrow_size // 2, arrow_cy - arrow_size // 2),
                        (right_x + arrow_size // 2, arrow_cy),
                        (right_x - arrow_size // 2, arrow_cy + arrow_size // 2),
                    ],
                    arrow_thickness
                )

                screen.blit(hint_surface, (0, 0))

                # end calendar page

        # always active 
        if uiData.currentPage == "main": 
            if mouseDownStartTime is not None:
                elapsed = time.time() - mouseDownStartTime
                if elapsed >= actionPanelHoldTime:
                    if editMode: editMode = not editMode
                    else: showActionPanel = not showActionPanel
                    if not editMode: saveWidgetsState()
                    mouseDownStartTime = None
        else:
            showActionPanel = False
            mouseDownStartTime = None

        if showActionPanel and tActionPanelOpacity < 1: tActionPanelOpacity += 0.2
        elif not showActionPanel and tActionPanelOpacity > 0: tActionPanelOpacity -= 0.2

        if tActionPanelOpacity < 0: tActionPanelOpacity = 0
        
        if tActionPanelOpacity > 0:
            # only update overlay if opacity changed
            if abs(tActionPanelOpacity - last_overlay_opacity) > 0.01:
                overlay_surface.fill((0, 0, 0, 0))
                overlay_surface.fill(uiTools.interpolateColors((0, 0, 0, 0),
                                                    (0, 0, 0, 200),
                                                    tActionPanelOpacity))
                last_overlay_opacity = tActionPanelOpacity
            
            screen.blit(overlay_surface, (0, 0))
        
        if showActionPanel: actionPanel.tick(screen)

        scaled = pygame.transform.smoothscale(screen, actualScreen.get_size())
        actualScreen.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(60)