import pygame

# Cache for rounded surfaces to avoid recreating them every frame
_rounded_surface_cache = {}

def makeRoundedSurface(size, radius, color, outlineWidth):
    """Create a rounded rectangle surface. Results are cached for performance."""
    # Create cache key from parameters
    cache_key = (size, radius, color, outlineWidth)
    
    # Return cached surface if available
    if cache_key in _rounded_surface_cache:
        return _rounded_surface_cache[cache_key]
    
    scale = 3
    big = pygame.Surface((size[0] * scale, size[1] * scale), pygame.SRCALPHA)
    big.fill((0,0,0,0))
    pygame.draw.rect(big, color=color, rect=big.get_rect(), border_radius=radius * scale, width=outlineWidth * scale)
    result = pygame.transform.smoothscale(big, size)
    
    # Cache the result
    _rounded_surface_cache[cache_key] = result
    
    return result

def clear_rounded_surface_cache():
    """Clear the cache if needed (e.g., on resolution change)"""
    global _rounded_surface_cache
    _rounded_surface_cache.clear()

def interpolateColors(startColor, endColor, t):
    # Clamp t to [0,1]
    t = max(0.0, min(1.0, float(t)))

    sC = tuple(startColor)
    eC = tuple(endColor)

    # If either color has alpha, produce RGBA output; otherwise RGB
    target_len = 4 if (len(sC) == 4 or len(eC) == 4) else 3

    out = []
    for i in range(target_len):
        default = 255 if i == 3 else 0
        s = sC[i] if i < len(sC) else default
        e = eC[i] if i < len(eC) else default

        # Accept float channels in 0.0-1.0 by scaling to 0-255
        if isinstance(s, float) and 0.0 <= s <= 1.0:
            s = int(round(s * 255))
        if isinstance(e, float) and 0.0 <= e <= 1.0:
            e = int(round(e * 255))

        val = int(round(s + (e - s) * t))
        val = max(0, min(255, val))
        out.append(val)

    return tuple(out)

def wrapText(text, maxCharacters):
    lines = text.splitlines()
    result = []

    for originalLine in lines:
        words = originalLine.split()
        line = ""
        
        for word in words:
            if len(line) + len(word) + (1 if line else 0) > maxCharacters:
                result.append(line)
                line = word
            else:
                line += (" " if line else "") + word

        if line:
            result.append(line)
        elif not words:
            result.append("")

    return result
