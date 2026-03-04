from widgets import *
import data.uiData as uiData
                
class ReadingTracker(Widget):
    name = "Reading Tracker"
    preferredSizes = [(1, 1), (2, 1), (3, 1)]

    def __init__(self, width=2, height=1, pos=(0, 0)):
        super().__init__(width, height, pos)
        self.max_pages = 500
        self.pages = 0
        # animated display value for smooth progress transitions
        self.displayPages = float(self.pages)
        self.easeSpeedLocal = 0.18
        # visual feedback timers (seconds)
        self.flashTimer = 0.0
        self.flashDuration = 0.18
        # region padding
        self.gutter = 8
        # track mouse-over for wheel handling
        self._mouseOver = False

    def setPages(self, value):
        self.pages = max(0, min(self.max_pages, int(value)))
        # ensure animated value will move toward it
        # flash for feedback
        self.flashTimer = self.flashDuration

    def increment(self, amount=1):
        self.setPages(self.pages + amount)

    def decrement(self, amount=1):
        self.setPages(self.pages - amount)

    def update(self):
        # Update displayPages toward pages for smooth progress bar animation
        if abs(self.displayPages - self.pages) > 0.01:
            self.displayPages += (self.pages - self.displayPages) * self.easeSpeedLocal
        else:
            self.displayPages = float(self.pages)

        # reduce flash timer
        if self.flashTimer > 0:
            # assume tick called at ~60fps; reduce by a small step
            # but since we don't have delta time, use a fraction tied to ease speed
            self.flashTimer -= 0.016
            if self.flashTimer < 0:
                self.flashTimer = 0

        # track mouse-over for wheel support
        mx, my = pygame.mouse.get_pos()
        px, py = self.getActualPosition()
        sx, sy = self.getActualSize()
        self._mouseOver = (px <= mx <= px + sx and py <= my <= py + sy)

    def drawContent(self):
        surf = self.surface
        w, h = surf.get_width(), surf.get_height()

        # background already handled by parent; draw interior content
        # padding
        pad = int(max(6, h * 0.08))
        inner_w = max(10, w - pad * 2)
        inner_h = max(10, h - pad * 2)

        # Title
        title_font = self.fonts[min(len(self.fonts) - 1, max(0, int(self.height - 1)))]
        small_font = self.fonts[max(0, min(len(self.fonts) - 1, int(self.height - 1)))]
        try:
            title_text = title_font.render("Reading Tracker", True, uiData.textColor)
        except Exception:
            title_text = self.fonts[0].render("Reading Tracker", True, uiData.textColor)
        title_rect = title_text.get_rect()
        title_rect.topleft = (pad, pad)
        surf.blit(title_text, title_rect)

        # Page count and percent
        percent = 0 if self.max_pages == 0 else int(round((self.displayPages / self.max_pages) * 100))
        page_text_str = f"{int(round(self.displayPages))} / {self.max_pages}  ({percent}%)"
        # use a slightly smaller font for the count
        count_font_index = max(0, min(len(self.fonts) - 1, int(self.height)))
        count_font = self.fonts[count_font_index]
        count_text = count_font.render(page_text_str, True, uiData.textColor)
        count_rect = count_text.get_rect()
        count_rect.midtop = (w // 2, pad + title_rect.height + 4)
        surf.blit(count_text, count_rect)

        # Progress bar area
        bar_top = count_rect.bottom + pad // 2
        bar_height = max(14, int(h * 0.18))
        bar_left = pad
        bar_right = w - pad
        bar_width = bar_right - bar_left

        # background of progress bar (rounded)
        bg_bar_surf = uiTools.makeRoundedSurface((bar_width, bar_height), int(bar_height / 2), (50, 50, 50, 200), 0)
        surf.blit(bg_bar_surf, (bar_left, bar_top))

        # filled portion
        fill_frac = 0.0
        if self.max_pages > 0:
            fill_frac = max(0.0, min(1.0, self.displayPages / float(self.max_pages)))
        fill_width = int(bar_width * fill_frac)
        if fill_width > 0:
            # choose a subtle progression color from uiData if available
            fill_color = getattr(uiData, "widgetBackgroundColorProgression", (80, 80, 80, 220))
            filled_surf = uiTools.makeRoundedSurface((fill_width, bar_height), int(bar_height / 2), fill_color, 0)
            surf.blit(filled_surf, (bar_left, bar_top))

        # overlay percentage text on the progress bar
        percent_str = f"{percent}%"
        percent_font = self.fonts[max(0, min(len(self.fonts) - 1, int(max(0, self.height - 1))))]

        percent_text = percent_font.render(percent_str, True, uiData.textColor)
        pct_rect = percent_text.get_rect(center=(w // 2, bar_top + bar_height // 2))
        surf.blit(percent_text, pct_rect)

        # Draw minus and plus buttons at left and right of the bar
        btn_radius = max(12, bar_height // 2 + 2)
        btn_y = bar_top + bar_height // 2
        left_btn_x = bar_left - btn_radius - 6
        right_btn_x = bar_right + btn_radius + 6 - (btn_radius * 2)  # align symmetrical

        # Left button (decrement)
        left_btn_rect = pygame.Rect(left_btn_x, btn_y - btn_radius, btn_radius * 2, btn_radius * 2)
        left_surf = uiTools.makeRoundedSurface((left_btn_rect.width, left_btn_rect.height), btn_radius, uiData.primaryTransparentColor, 0)
        surf.blit(left_surf, (left_btn_rect.x, left_btn_rect.y))
        # minus sign
        minus_font = self.fonts[0]
        minus_text = minus_font.render("-", True, uiData.textColor)
        mrect = minus_text.get_rect(center=left_btn_rect.center)
        surf.blit(minus_text, mrect)

        # Right button (increment)
        right_btn_rect = pygame.Rect(w - (left_btn_rect.width + (pad - 4)), btn_y - btn_radius, left_btn_rect.width, left_btn_rect.height)
        right_surf = uiTools.makeRoundedSurface((right_btn_rect.width, right_btn_rect.height), btn_radius, uiData.primaryTransparentColor, 0)
        surf.blit(right_surf, (right_btn_rect.x, right_btn_rect.y))
        plus_text = minus_font.render("+", True, uiData.textColor)
        prect = plus_text.get_rect(center=right_btn_rect.center)
        surf.blit(plus_text, prect)

        # subtle flash overlay when pages change
        if self.flashTimer > 0:
            alpha = int(180 * (self.flashTimer / self.flashDuration))
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, alpha // 3))
            surf.blit(overlay, (0, 0))

        # save interactive regions for click handling
        self._left_btn_rect = left_btn_rect
        self._right_btn_rect = right_btn_rect
        self._progress_rect = pygame.Rect(bar_left, bar_top, bar_width, bar_height)

    def handleEvent(self, event):
        # Handle mouse clicks inside widget with button info and handle scroll events
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            px, py = self.getActualPosition()
            sx, sy = self.getActualSize()
            if px <= mx <= px + sx and py <= my <= py + sy:
                # translate to local coords
                local_x = mx - px
                local_y = my - py
                # call internal clicked handler with button info
                self.clicked(local_x, local_y, event.button)
        elif event.type == pygame.MOUSEWHEEL:
            # allow wheel to change pages when mouse is over widget
            if self._mouseOver:
                # event.y is +1 for up, -1 for down
                if event.y > 0:
                    self.increment(amount=1)
                elif event.y < 0:
                    self.decrement(amount=1)

    def clicked(self, local_x, local_y, button=1):
        # local_x/local_y are relative to surface (0..width, 0..height)
        # Ensure interactive rects exist (they will after first drawContent call)
        # Fallback compute if not present
        w, h = self.surface.get_size()
        pad = int(max(6, h * 0.08))
        bar_left = pad
        bar_right = w - pad
        bar_height = max(14, int(h * 0.18))
        bar_top = int((h // 2) + pad // 2)
        progress_rect = getattr(self, "_progress_rect", pygame.Rect(bar_left, bar_top, bar_right - bar_left, bar_height))

        left_btn = getattr(self, "_left_btn_rect", pygame.Rect(pad - 30, bar_top - 10, 24, 24))
        right_btn = getattr(self, "_right_btn_rect", pygame.Rect(w - (pad - 4) - 24, bar_top - 10, 24, 24))

        point = (int(local_x), int(local_y))

        # Left button actions
        if left_btn.collidepoint(point):
            if button == 1:
                self.decrement(1)
            elif button == 3:
                # right-click: big step
                self.decrement(10)
            else:
                self.decrement(1)
            self.flashTimer = self.flashDuration
            return

        # Right button actions
        if right_btn.collidepoint(point):
            if button == 1:
                self.increment(1)
            elif button == 3:
                self.increment(10)
            else:
                self.increment(1)
            self.flashTimer = self.flashDuration
            return

        # Progress bar clicked: set absolute position by click percent
        if progress_rect.collidepoint(point):
            rel_x = point[0] - progress_rect.x
            frac = 0.0
            if progress_rect.width > 0:
                frac = max(0.0, min(1.0, float(rel_x) / float(progress_rect.width)))
            new_pages = int(round(frac * self.max_pages))
            # left click sets, right click toggles to min/max
            if button == 1:
                self.setPages(new_pages)
            elif button == 3:
                # right-click: jump to nearest quartile for convenience
                quart = int(round(frac * 4)) * (self.max_pages // 4)
                self.setPages(quart)
            else:
                self.setPages(new_pages)
            self.flashTimer = self.flashDuration
            return

        # Otherwise, clicking the widget body toggles small increments
        # center click increments by 1
        center_region = pygame.Rect(w // 4, h // 4, w // 2, h // 2)
        if center_region.collidepoint(point):
            if button == 1:
                self.increment(1)
            elif button == 3:
                self.decrement(1)
            self.flashTimer = self.flashDuration
            return

        # click anywhere else has no effect
        return

WIDGET_CLASS = ReadingTracker
