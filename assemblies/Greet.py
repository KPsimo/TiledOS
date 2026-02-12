
from widgets import *
import data.uiData as uiData
                
class Greet(Widget):
    name = "Greet"
    preferredSizes = [(3, 1), (2, 1), (3, 2), (1, 1)]

    def __init__(self, width=3, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)

        # A small set of friendly greetings
        self.greetings = [
            "Hello!", "Hi there!", "Hey!", "Good day!", "Howdy!",
            "Welcome!", "Greetings!", "What's up?", "Nice to see you!",
            "Yo!", "Hi friend!", "Salutations!"
        ]

        # optional subtitle lines to add variety
        self.subs = [
            "Have a great day.", "You're doing great.", "Keep going!",
            "Stay curious.", "Make something awesome.", "Breathe. Smile."
        ]

        # pick an initial greeting based on time so it's varied on each start
        t = int(time.time() * 1000)
        self.index = t % len(self.greetings)
        self.subIndex = (t // 1000) % len(self.subs)

        # timing for automatic rotation
        self.lastChange = time.time()
        self.changeInterval = 10.0  # seconds

        # simple pulse animation when greeting changes or clicked
        self.pulse = 0.0
        self.pulseSpeed = 3.5
        self.pulseActive = False

        # visual accents
        self.palette = [
            (96, 156, 255),  # blue
            (120, 220, 130), # green
            (255, 165, 120), # orange
            (200, 120, 255), # purple
            (255, 105, 180)  # pink
        ]

        # a small counter to vary selection without using random module
        self.counter = int(t % 10000)

        # precalc sizes used for clickable "New" button area (logical pixels)
        self._button_margin = 8
        self._button_w = 80
        self._button_h = 30

    def _pickNext(self):
        # deterministic but varied selection using a counter and time
        self.counter += 1
        self.index = (self.index + (self.counter % 3) + 1) % len(self.greetings)
        self.subIndex = (self.subIndex + (self.counter % 2) + 1) % len(self.subs)
        self.lastChange = time.time()
        self.pulseActive = True
        self.pulse = 1.0  # start a visible pulse

    def update(self):
        # automatic rotation
        now = time.time()
        if now - self.lastChange >= self.changeInterval:
            self._pickNext()

        # pulse decay
        if self.pulseActive:
            # reduce pulse smoothly
            self.pulse -= (1.0 / self.pulseSpeed) * (1.0 / 60.0) * 60.0 * 0.016
            if self.pulse <= 0.0:
                self.pulse = 0.0
                self.pulseActive = False

    def drawContent(self):
        surf = self.surface
        w, h = surf.get_width(), surf.get_height()

        # choose an accent color from palette
        accent = self.palette[self.index % len(self.palette)]

        # draw a subtle accent bar on the left
        bar_w = max(8, int(w * 0.06))
        bar_surf = pygame.Surface((bar_w, h), pygame.SRCALPHA)
        # gradient-ish: two rects with different alpha
        bar_surf.fill((0, 0, 0, 0))
        pygame.draw.rect(bar_surf, accent + (220,), (0, 0, bar_w, h))
        surf.blit(bar_surf, (0, 0))

        # draw a translucent overlay strip at top for light effect
        overlay = pygame.Surface((w - bar_w, h // 3), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 12))
        surf.blit(overlay, (bar_w, 0))

        # prepare text
        # choose base font index by widget height like other widgets expect
        font_index = max(0, min(len(self.fonts) - 1, int(self.height - 1)))
        big_font = self.fonts[font_index]
        # a smaller font for the subtitle and small UI elements
        small_index = max(0, font_index - 2)
        small_font = self.fonts[small_index]

        # apply a pulse scale to make events feel lively
        pulse_scale = 1.0 + (0.08 * (self.pulse if self.pulseActive else 0.0))

        greeting = self.greetings[self.index]
        sub = self.subs[self.subIndex]

        # render greeting text
        # to keep text fitting, we may reduce font size by choosing smaller font if too wide
        text_surf = big_font.render(greeting, True, uiData.textColor)
        # scale text surface slightly for pulse effect
        if pulse_scale != 1.0:
            tw, th = text_surf.get_size()
            text_surf = pygame.transform.smoothscale(text_surf, (int(tw * pulse_scale), int(th * pulse_scale)))

        tx, ty = text_surf.get_size()
        # position greeting centrally but offset to account for left accent bar
        center_x = bar_w + (w - bar_w) // 2
        center_y = h // 2 - 10
        text_rect = text_surf.get_rect(center=(center_x, center_y))
        surf.blit(text_surf, text_rect)

        # render subtitle
        sub_surf = small_font.render(sub, True, tuple(max(0, c - 20) for c in uiData.textColor))
        sub_rect = sub_surf.get_rect(center=(center_x, center_y + max(24, int(h * 0.18))))
        surf.blit(sub_surf, sub_rect)

        # Draw "New" button at bottom-right
        # compute scaled button size relative to widget pixels
        scale = uiData.quickScale if hasattr(uiData, "quickScale") else 1
        btn_w = int(self._button_w * scale)
        btn_h = int(self._button_h * scale)
        btn_margin = int(self._button_margin * scale)
        btn_x = w - btn_margin - btn_w
        btn_y = h - btn_margin - btn_h

        # button background with rounded-ish rectangle (simple rect with border)
        btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        # slightly darker background
        bg_col = (accent[0], accent[1], accent[2], 220)
        pygame.draw.rect(btn_surf, bg_col, (0, 0, btn_w, btn_h), border_radius=max(4, btn_h // 4))
        # subtle border
        border_col = tuple(min(255, c + 30) for c in accent) + (180,)
        pygame.draw.rect(btn_surf, border_col, (0, 0, btn_w, btn_h), width=2, border_radius=max(4, btn_h // 4))

        # draw "New" label centered
        label_font = small_font
        label = label_font.render("New", True, (255, 255, 255))
        lbl_rect = label.get_rect(center=(btn_w // 2, btn_h // 2))
        btn_surf.blit(label, lbl_rect)

        surf.blit(btn_surf, (btn_x, btn_y))

        # optionally draw a tiny accent circle near top-left of content area (after bar)
        dot_r = max(4, int(h * 0.03))
        dot_pos = (bar_w + 12, 12 + dot_r)
        pygame.draw.circle(surf, accent, dot_pos, dot_r)
        pygame.draw.circle(surf, (255, 255, 255, 48), dot_pos, max(1, dot_r // 2))

        # store button rect in logical surface coordinates for click detection
        self._button_rect = (btn_x, btn_y, btn_w, btn_h)

    def clicked(self, mx, my):
        # Convert to local widget coords
        px, py = self.getActualPosition()
        local_x = mx - px
        local_y = my - py

        # if we don't yet have a button rect, ignore (shouldn't happen)
        if hasattr(self, "_button_rect"):
            bx, by, bw, bh = self._button_rect
            if bx <= local_x <= bx + bw and by <= local_y <= by + bh:
                # clicked the "New" button
                self._pickNext()
                return

        # otherwise clicking anywhere in the widget also triggers a new greeting and pulse
        w, h = self.getActualSize()
        if 0 <= local_x <= w and 0 <= local_y <= h:
            self._pickNext()

WIDGET_CLASS = Greet
