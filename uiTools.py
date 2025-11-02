import pygame

def makeRoundedSurface(size, radius, color):
    scale = 3
    big = pygame.Surface((size[0] * scale, size[1] * scale), pygame.SRCALPHA)
    big.fill((0,0,0,0))
    pygame.draw.rect(big, color=color, rect=big.get_rect(), border_radius=radius * scale)
    return pygame.transform.smoothscale(big, size)