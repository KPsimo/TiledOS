import pygame

def makeRoundedSurface(size, radius, color):
    scale = 3
    big = pygame.Surface((size[0] * scale, size[1] * scale), pygame.SRCALPHA)
    big.fill((0,0,0,0))
    pygame.draw.rect(big, color=color, rect=big.get_rect(), border_radius=radius * scale)
    return pygame.transform.smoothscale(big, size)

def interpolateColors(startColor, endColor, t):
    r = int(startColor[0] + (endColor[0] - startColor[0]) * t)
    g = int(startColor[1] + (endColor[1] - startColor[1]) * t)
    b = int(startColor[2] + (endColor[2] - startColor[2]) * t)

    return (r, g, b)