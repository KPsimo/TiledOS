import pygame
import os

def initPygame(width=800, height=480):
    global page
    # Initialize Pygame and set up the main display window.
    pygame.init()
    screen = pygame.display.set_mode((800, 480))
    pygame.display.set_caption("Material Quantum")
    
    # Load fonts for different text elements.
    font = pygame.font.Font('resources/outfit.ttf', 30)

    # Set initial page and clear text.
    page = "home"

    return screen, width, height

def loadIcon(icon):
    # Loads an icon image from the resources/icons directory.
    return pygame.image.load(f"resources/icons/{icon}.png").convert_alpha()

def applyRoundedCorners(surface, radius):
    # Applies rounded corners to a given surface.
    width, height = surface.get_size()
    roundedMask = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(roundedMask, (255, 255, 255, 255), (0, 0, width, height), border_radius=radius)
    surface = surface.convert_alpha()
    roundedSurface = pygame.Surface((width, height), pygame.SRCALPHA)
    roundedSurface.blit(surface, (0, 0))
    roundedSurface.blit(roundedMask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return roundedSurface

def setColor(key, color):
    # Sets a color in the global colors dictionary.
    global colors
    colors[key] = color

def setPage(pageTo):
    # Sets the current page of the GUI.
    global page
    page = pageTo

def createButton(centerX, centerY, icon, radius):
    # Creates a button with a circular area and an icon.
    rect = pygame.Rect(centerX - radius, centerY - radius, radius * 2, radius * 2)
    icon = pygame.transform.smoothscale(icon, (radius * 2, radius * 2))
    return rect, icon, (centerX, centerY, radius)

def drawButton(screen, color, buttonCircle, buttonIcon, buttonRect):
    # Draws a circular button and its icon on the given screen.
    pygame.draw.circle(screen, color, (buttonCircle[0], buttonCircle[1]), buttonCircle[2])
    screen.blit(buttonIcon, buttonRect.topleft)

def checkButtonPresses(events, buttonRects):
    # Checks if any button is pressed.
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for buttonRect in buttonRects:
                if buttonRect.collidepoint(mouse_pos):
                    return buttonRect  # Return the pressed button
    return None

def exit():
    # Exits the GUI loop.
    global running
    running = False

def runGUI():
    # Main function to run the GUI application.
    global colors, width, height, running, page
    screen, width, height = initPygame()
    clock = pygame.time.Clock()

    if True: # Initialize colors
        if True:
            colors = {
                "bg": (20, 20, 20),
                "primary": (109, 230, 254),
                "text": (255, 255, 255),
                "buttonBase": (30, 30, 30),

                "sliderKnob": (109, 230, 254),
            }

            # Initialize button colors
            # Create a new color for each button that pulses when clicked
            buttonColors = {
                "static": colors["buttonBase"],
            }

    if True: # Initialize buttons
        buttonRect, buttonIcon, buttonCircle = createButton(400, 240, loadIcon("flash"), 40)

        # List of buttons for event checking
        buttonRects = [buttonRect,
                       # Add more buttons here as needed
                      ]
    
    running = True

    while running:
        screen.fill(colors["bg"])

        # Global event handling
        events = pygame.event.get()
        pressedButton = checkButtonPresses(events, buttonRects) # Check for button presses
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()

        # Page-specific rendering
        if page == "home":
            # Draw buttons and other UI elements for homepage here
            drawButton(screen, colors["buttonBase"], buttonCircle, buttonIcon, buttonRect)

            if pressedButton == buttonRect:
                print("Button Pressed!")

        # Global display update and event handling
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

# Run the GUI if this script is executed directly
if __name__ == "__main__":
    runGUI()