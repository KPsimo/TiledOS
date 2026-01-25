import pygame
import sys
import os
import importlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assemblies'))
pygame.init()

def initializeTestEnvironment():
    testScreen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Assembly Widget Test")
    return testScreen

def cleanupTestEnvironment():
    pygame.quit()

def clearWidgetsModule():
    if 'widgets' in sys.modules:
        del sys.modules['widgets']

def loadAssemblyModules(assembliesDir="assemblies"):
    """
    Load all assembly modules from the assemblies directory.
    
    Args:
        assembliesDir (str): Path to the assemblies directory
        
    Returns:
        list: List of tuples (moduleName, module)
        
    Raises:
        AssertionError: If assemblies directory doesn't exist or no modules loaded
    """
    assert os.path.isdir(assembliesDir), f"Assemblies directory '{assembliesDir}' not found"
    
    loadedModules = []
    for file in os.listdir(assembliesDir):
        if not file.endswith(".py") or file.startswith("__"):
            continue
        
        moduleName = file[:-3]
        try:
            if moduleName in sys.modules:
                del sys.modules[moduleName]
            
            mod = importlib.import_module(moduleName)
            loadedModules.append((moduleName, mod))
        except Exception as e:
            raise Exception(f"Failed to import assembly '{moduleName}': {e}")
    
    assert len(loadedModules) > 0, "No assembly modules were successfully loaded"
    return loadedModules

def verifyWidgetClassAttribute(assembliesDir="assemblies"):
    for file in os.listdir(assembliesDir):
        if not file.endswith(".py") or file.startswith("__"):
            continue
        
        moduleName = file[:-3]
        try:
            if moduleName in sys.modules:
                del sys.modules[moduleName]
            
            mod = importlib.import_module(moduleName)
            assert hasattr(mod, "WIDGET_CLASS"), \
                f"Assembly '{moduleName}' does not have WIDGET_CLASS attribute"
        except AssertionError:
            raise
        except Exception as e:
            raise Exception(f"Failed to check WIDGET_CLASS in '{moduleName}': {e}")

def testWidgetInstantiation(assembliesDir="assemblies"):
    for file in os.listdir(assembliesDir):
        if not file.endswith(".py") or file.startswith("__"):
            continue
        
        moduleName = file[:-3]
        try:
            if moduleName in sys.modules:
                del sys.modules[moduleName]
            
            mod = importlib.import_module(moduleName)
            widgetClass = getattr(mod, "WIDGET_CLASS")
            
            widget = widgetClass()
            assert widget is not None, f"Failed to instantiate widget from '{moduleName}'"
            assert hasattr(widget, "name"), \
                f"Widget from '{moduleName}' does not have 'name' attribute"
        except AssertionError:
            raise
        except Exception as e:
            raise Exception(f"Failed to instantiate widget from '{moduleName}': {e}")

def verifyWidgetMethods(assembliesDir="assemblies", requiredMethods=None):

    if requiredMethods is None:
        requiredMethods = ["draw", "drawContent", "update", "tick"]
    
    for file in os.listdir(assembliesDir):
        if not file.endswith(".py") or file.startswith("__"):
            continue
        
        moduleName = file[:-3]
        try:
            if moduleName in sys.modules:
                del sys.modules[moduleName]
            
            mod = importlib.import_module(moduleName)
            widgetClass = getattr(mod, "WIDGET_CLASS")
            widget = widgetClass()
            
            for method in requiredMethods:
                assert hasattr(widget, method) and callable(getattr(widget, method)), \
                    f"Widget '{moduleName}' missing required method '{method}'"
        except AssertionError:
            raise
        except Exception as e:
            raise Exception(f"Failed to check methods for '{moduleName}': {e}")

def testWidgetDrawing(assembliesDir="assemblies", width=2, height=2):
    for file in os.listdir(assembliesDir):
        if not file.endswith(".py") or file.startswith("__"):
            continue
        
        moduleName = file[:-3]
        try:
            if moduleName in sys.modules:
                del sys.modules[moduleName]
            
            mod = importlib.import_module(moduleName)
            widgetClass = getattr(mod, "WIDGET_CLASS")
            widget = widgetClass(width=width, height=height, pos=(0, 0))
            
            testSurface = pygame.Surface((800, 600))
            testSurface.fill((0, 0, 0))
            
            try:
                widget.draw(testSurface)
            except Exception as drawError:
                raise Exception(f"Widget '{moduleName}' failed to draw: {drawError}")
            
            assert widget.surface is not None, \
                f"Widget '{moduleName}' surface is None after draw"
            assert widget.surface.get_size()[0] > 0, \
                f"Widget '{moduleName}' surface has invalid width"
            assert widget.surface.get_size()[1] > 0, \
                f"Widget '{moduleName}' surface has invalid height"
        except AssertionError:
            raise
        except Exception as e:
            raise Exception(f"Failed to test drawing for '{moduleName}': {e}")

def testWidgetTickCycle(assembliesDir="assemblies", tickCount=5, width=2, height=2):
    for file in os.listdir(assembliesDir):
        if not file.endswith(".py") or file.startswith("__"):
            continue
        
        moduleName = file[:-3]
        try:
            if moduleName in sys.modules:
                del sys.modules[moduleName]
            
            mod = importlib.import_module(moduleName)
            widgetClass = getattr(mod, "WIDGET_CLASS")
            widget = widgetClass(width=width, height=height, pos=(0, 0))
            
            testSurface = pygame.Surface((800, 600))
            testSurface.fill((0, 0, 0))
            
            for _ in range(tickCount):
                try:
                    widget.tick(testSurface)
                except Exception as tickError:
                    raise Exception(f"Widget '{moduleName}' failed during tick: {tickError}")
        except AssertionError:
            raise
        except Exception as e:
            raise Exception(f"Failed to test tick cycle for '{moduleName}': {e}")

def testWidgetSurfaceIntegrity(assembliesDir="assemblies", cycleCount=10, width=2, height=2):
    for file in os.listdir(assembliesDir):
        if not file.endswith(".py") or file.startswith("__"):
            continue
        
        moduleName = file[:-3]
        try:
            if moduleName in sys.modules:
                del sys.modules[moduleName]
            
            mod = importlib.import_module(moduleName)
            widgetClass = getattr(mod, "WIDGET_CLASS")
            widget = widgetClass(width=width, height=height, pos=(0, 0))
            
            testSurface = pygame.Surface((800, 600))
            
            for i in range(cycleCount):
                testSurface.fill((0, 0, 0))
                widget.tick(testSurface)
                
                assert widget.surface is not None, \
                    f"Widget '{moduleName}' surface became None at iteration {i}"
                assert widget.surface.get_size()[0] > 0, \
                    f"Widget '{moduleName}' surface width invalid at iteration {i}"
        except AssertionError:
            raise
        except Exception as e:
            raise Exception(f"Failed surface integrity test for '{moduleName}': {e}")

def runAllTests(assembliesDir="assemblies"):
    try:
        clearWidgetsModule()
        loadAssemblyModules(assembliesDir)
        verifyWidgetClassAttribute(assembliesDir)
        testWidgetInstantiation(assembliesDir)
        verifyWidgetMethods(assembliesDir)
        testWidgetDrawing(assembliesDir)
        testWidgetTickCycle(assembliesDir)
        testWidgetSurfaceIntegrity(assembliesDir)
        
        return None

    except Exception as e:
        return e