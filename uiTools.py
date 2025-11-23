import pygame

def makeRoundedSurface(size, radius, color):
    scale = 3
    big = pygame.Surface((size[0] * scale, size[1] * scale), pygame.SRCALPHA)
    big.fill((0,0,0,0))
    pygame.draw.rect(big, color=color, rect=big.get_rect(), border_radius=radius * scale)
    return pygame.transform.smoothscale(big, size)

def interpolateColors(startColor, endColor, t):
    # Clamp t to [0,1]
    if t < 0: t = 0
    if t > 1: t = 1

    # Determine how many channels to produce (support RGB or RGBA inputs)
    max_len = max(len(startColor), len(endColor))

    out = []
    for i in range(max_len):
        # default missing components: for alpha (index 3) default to 255 (opaque), else 0
        default = 255 if i == 3 else 0
        s = startColor[i] if i < len(startColor) else default
        e = endColor[i] if i < len(endColor) else default
        val = int(round(s + (e - s) * t))
        # clamp channel to valid byte range
        val = max(0, min(255, val))
        out.append(val)

    return tuple(out)