from openai import OpenAI
from data.keys import openaiKey
import importlib.util
import traceback
import pygame
import data.uiData as uiData
import uiTools

# be sure you have keys.py in data/ with your OpenAI key defined as openaiKey variable
client = OpenAI(
    api_key=openaiKey
)

if True:
    systemMessage = '''
    You are an agent that generates Python widget classes for Tiled, a widget-based organization tool for high-school students.
    Tiled is a Pygame application that allows users to add, remove, and customize widgets on their desktop.
    You will be provided with the parent widget class for Tiled, including an example with a date widget.

    You may also be requested to modify or extend existing widgets.

    Output expectations:
    - Output a single Python class definition for the requested widget and functionality.
    - Do not include any explanations
    - Ensure the class inherits from the provided Widget class.
    - Use only standard Python libraries and Pygame.
    - Absolutely do not include any special formatting or LaTeX, just raw, plaintext Python code.
    - DO NOT OVERRIDE THESE METHODS
        - draw(self, screen)
        - setSize(self, width, height)
        - setPosition(self, x, y)
        - getSize(self)
        - getPos(self)
        - getActualSize(self)
        - getActualPosition(self)
        - _updateSurface(self)
        - setColor(self, color)

    The parent widget class is as follows:

    class Widget:
        name = "Widget"
        preferredSizes = [(1, 1)]
        freeSize = True
        def __init__(self, width=1, height=1, pos=(0, 0)):
            # logical target sizes (integers commonly), current animated size stored in self.size
            self.width = width
            self.height = height
            self.pos = (float(pos[0]), float(pos[1]))

            # size easing state
            self.size = (float(width), float(height))
            self.targetSize = (float(width), float(height))
            self.sizeSnapped = True

            # position easing state
            self.targetPos = (float(pos[0]), float(pos[1]))
            self.posSnapped = True

            self.easeSpeed = 0.25
            self.snapThreshold = 0.01

            self.color = uiData.widgetBackgroundColor

            pygame.font.init()
            self.fonts = []

            for size in [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]:
                self.fonts.append(pygame.font.Font('resources/outfit.ttf', size))

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
            return (
                self.pos[0] * (uiData.cellSize + uiData.cellPadding) + uiData.cellPadding // 2,
                self.pos[1] * (uiData.cellSize + uiData.cellPadding) + uiData.cellPadding // 2
            )

        def getSize(self):
            return (self.width, self.height)
        
        def getPos(self):
            return (int(self.pos[0]), int(self.pos[1]))

        def setSize(self, width, height):
            best = min(
            self.preferredSizes,
            key=lambda s: abs(s[0] - width) + abs(s[1] - height)
            )

            # snap to that size
            bw, bh = best
            self.width = bw
            self.height = bh
            self.targetSize = (float(bw), float(bh))

            # animate toward it
            self.sizeSnapped = False

        def setPosition(self, x, y):
            self.targetPos = (float(x), float(y))
            self.posSnapped = False

        def setColor(self, color):
            self.color = color

        def draw(self, screen):
            self.surface.fill((0, 0, 0, 0))
            roundedBg = uiTools.makeRoundedSurface(
                self.surface.get_size(),
                uiData.cornerRadius,
                self.color
            )
            self.surface.blit(roundedBg, (0, 0))
            self.drawContent()
            x = (self.pos[0] * (uiData.cellSize + uiData.cellPadding)) + uiData.cellPadding // 2
            y = (self.pos[1] * (uiData.cellSize + uiData.cellPadding)) + uiData.cellPadding // 2
            screen.blit(self.surface, (int(x), int(y)))

        def drawContent(self):
            # To be overridden by child classes
            pass

        def update(self):
            # To be overridden by child classes
            pass

        def tick(self, screen):
            # position easing
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
                # recreate surface to match new size
                self._updateSurface()

            self.update()
            self.draw(screen)

        def handleEvent(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                px, py = self.getActualPosition()
                sx, sy = self.getActualSize()
                if px <= mx <= px + sx and py <= my <= py + sy:
                    self.clicked(mx, my)

        def clicked(self, mx, my):
            # To be overridden by child classes
            pass


    Using the above Widget class as a base, generate a new Python class that defines a widget called "Date".

    class Date(Widget):
        name = "Date"
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

    When possible, pull colors and styles from the uiData module to maintain consistency with other widgets.

    Here is the uiData module for reference:

    screenWidth = 1920
    screenHeight = 1080

    quickScale = 1

    cellSize = 110 * quickScale
    cellPadding = 10 * quickScale

    backgroundColor = (10, 10, 10)

    widgetBackgroundColor = (30, 30, 30, 255)
    widgetBackgroundColorProgression = (widgetBackgroundColor[0] + 10, widgetBackgroundColor[1] + 10, widgetBackgroundColor[2] + 10, 240)
    widgetBackgroundColorCollision = (80, 30, 30)

    primaryTransparentColor = (widgetBackgroundColor[0] + 10, widgetBackgroundColor[1] + 10, widgetBackgroundColor[2] + 10, 200)

    textColor = (255, 255, 255)

    backgroundColorEditMode = (20, 20, 22)

    cornerRadius = 15

    An example call to cellSize wpuld be uiData.cellSize
    '''

messages = [
    {"role": "system", "content": systemMessage}
]

def getWidgetCode(prompt):

    messages.append({"role": "user", "content": prompt})
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    reply = completion.choices[0].message.content
    messages.append({"role": "agent", "content": reply})

    return reply

def buildAssembly(requestedWidget, assemblyName):
    prompt = f"Create a Python class that defines a widget with the requested description '{requestedWidget}' for TiledOS. The class should be named '{assemblyName.replace(" ", "")}', with the static name {assemblyName} and inherit from the Widget class provided. Ensure that preferred sizes are set. Ensure the widget has useful functionality and a visually appealing design. Import modules as needed."

    assemblyCode = getWidgetCode(prompt)
    
    # add a python file with the generated code to the assemblies directory
    with open(f"assemblies/{assemblyName.replace(" ", "")}.py", "w") as f:
        f.write(f'''
from widgets import *
import data.uiData as uiData
                
{assemblyCode}

WIDGET_CLASS = {assemblyName.replace(" ", "")}
''')

def modifyAssembly(modificationRequest, assemblyName):
    with open(f"assemblies/{assemblyName.replace(' ', '')}.py", "r") as f:
        assemblyCode = f.read()
    prompt = f"Modify the existing widget class '{assemblyName.replace(' ', '')}' for TiledOS with the following request: '{modificationRequest}'. Ensure the widget retains its original functionality while incorporating the requested changes. Here is the existing code for reference:\n\n{assemblyCode}\n\nProvide the complete modified class definition only."

    assemblyCode = getWidgetCode(prompt)
    
    # overwrite the python file with the modified code in the assemblies directory
    with open(f"assemblies/{assemblyName.replace(" ", "")}.py", "w") as f:
        f.write(f'''
from widgets import *
import data.uiData as uiData
                
{assemblyCode}

WIDGET_CLASS = {assemblyName.replace(" ", "")}
''')
        
if __name__ == "__main__":
    name = input("Enter the name of the widget you want to create: ")
    description = input("Enter a brief description of the widget's functionality: ")
    print("Building assembly...")
    buildAssembly(description, name)