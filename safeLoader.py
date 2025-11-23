import importlib.util
import traceback
import pygame
import data.uiData as uiData
import uiTools

def tryLoadModule(path):
    try:
        spec = importlib.util.spec_from_file_location("newAssembly", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        print("ERROR loading AI module:", e)
        traceback.print_exc()
        return None


def validateWidgetClass(cls, baseClass):
    return issubclass(cls, baseClass) and cls is not baseClass


def testWidgetInstance(instance):

    try:
        instance.update()

        fakeScreen = pygame.Surface((400, 400), pygame.SRCALPHA)

        instance.tick(fakeScreen)

        return True

    except Exception as e:
        print("Widget instance failed test:", e)
        traceback.print_exc()
        return False
