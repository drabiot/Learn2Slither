import os
import math
from environment import GRID_COLS, GRID_ROWS
import pygame
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

CELL_SIZE = 40
BOARD_SIZE = 800
PANEL_WIDTH = 300
WINDOW_WIDTH = BOARD_SIZE + PANEL_WIDTH
WINDOW_HEIGHT = BOARD_SIZE

MIN_FPS = 1
MAX_FPS = 120

BUTTON_WIDTH = 120
KEY_WIDTH = 60
METER_WIDTH = PANEL_WIDTH - 20
SLIDER_PAD = 5
TICK_OFFSET_Y = 13
PANEL_SHIFT = 0

OUTLINE_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)]

PYGAME_COLORS = {
    '0': (40, 40, 40),
    'W': (87, 138, 52),
    'R': (200, 40, 40),
    'G': (40, 180, 40),
    'H': (78, 124, 246),
    'S': (66, 111, 227),
    'P': (74, 117, 44),
}

KEY_TO_DIRECTION = {
    pygame.K_UP: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT",
}

DIRECTION_ANGLES = {
    "UP": 90,
    "LEFT": 180,
    "DOWN": 270,
    "RIGHT": 0,
}

KEY_SPRITES = {
    "UP": "up",
    "DOWN": "bot",
    "LEFT": "left",
    "RIGHT": "right",
}


class Display:
    def __init__(self, fps=8, step_by_step=False):
        pygame.init()
        width = (GRID_COLS + 2) * CELL_SIZE
        height = (GRID_ROWS + 2) * CELL_SIZE
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.screen = pygame.Surface((width, height))
        pygame.display.set_caption("Learn2Slither")
        self.clock = pygame.time.Clock()

        self.current_direction = "UP"
        self.last_head_pos = None
        self.has_moved = False

        self.fps = max(MIN_FPS, min(MAX_FPS, fps))
        self.step_by_step = step_by_step
        self.paused = False
        self.dragging = False
        self.step_requested = False
        self.quit_requested = False
        self.stats = {"session": 0, "total": 0, "best": 0, "avg": 0.0,
                      "green": 0, "red": 0}

        try:
            self.raw_textures = {
                'R': pygame.image.load(
                    "texture/red_apple.png").convert_alpha(),
                'G': pygame.image.load(
                    "texture/green_apple.png").convert_alpha(),
                'H': pygame.image.load(
                    "texture/snake_head.png").convert_alpha(),
            }
        except pygame.error as e:
            print(f"Error when loading textures : {e}")
            self.raw_textures = {}

        self._load_panel()

    def _load(self, name, width):
        try:
            img = pygame.image.load(f"texture/{name}.png").convert_alpha()
        except (pygame.error, FileNotFoundError):
            img = pygame.Surface((width, width // 2))
            img.fill((90, 90, 90))
            return img
        height = round(img.get_height() * width / img.get_width())
        return pygame.transform.scale(img, (width, height))

    def _load_panel(self):
        cx = BOARD_SIZE + PANEL_WIDTH // 2 - PANEL_SHIFT

        try:
            self.font = pygame.font.Font("texture/pixel_font.ttf", 16)
        except FileNotFoundError:
            self.font = pygame.font.Font(None, 20)

        self.panel_bg = pygame.Surface((PANEL_WIDTH, WINDOW_HEIGHT))
        self.panel_bg.fill(PYGAME_COLORS['P'])

        self.next_img = self._load("next_step_key", BUTTON_WIDTH)
        self.next_hover = self._load("next_step_key_hover", BUTTON_WIDTH)
        self.next_rect = self.next_img.get_rect(center=(cx, 250))

        self.pause_img = self._load("pause_key", BUTTON_WIDTH)
        self.pause_hover = self._load("pause_key_hover", BUTTON_WIDTH)
        self.pause_rect = self.pause_img.get_rect(center=(cx, 350))

        self.keys = {}
        self.keys_press = {}
        self.key_rects = {}
        centers = {"UP": (cx, 470), "LEFT": (cx - 54, 530),
                   "DOWN": (cx, 530), "RIGHT": (cx + 54, 530)}
        for direction, sprite in KEY_SPRITES.items():
            self.keys[direction] = self._load(f"{sprite}_key", KEY_WIDTH)
            self.keys_press[direction] = self._load(
                f"{sprite}_key_press", KEY_WIDTH)
            self.key_rects[direction] = self.keys[direction].get_rect(
                center=centers[direction])

        self.meter_img = self._load("fps_meter", METER_WIDTH)
        self.meter_rect = self.meter_img.get_rect(center=(cx, 690))
        meter_raw_width = pygame.image.load(
            "texture/fps_meter.png").get_width()
        tick_raw = pygame.image.load("texture/fps_tick.png").convert_alpha()
        factor = METER_WIDTH / meter_raw_width
        self.tick_img = pygame.transform.scale(
            tick_raw, (round(tick_raw.get_width() * factor),
                       round(tick_raw.get_height() * factor)))
        self.track_left = self.meter_rect.left + SLIDER_PAD
        self.track_right = self.meter_rect.right - SLIDER_PAD

    def _text(self, text, pos, center=False):
        anchor = "center" if center else "topleft"
        outline = self.font.render(text, True, (0, 0, 0))
        for dx, dy in OUTLINE_OFFSETS:
            self.window.blit(outline, outline.get_rect(
                **{anchor: (pos[0] + dx, pos[1] + dy)}))
        surf = self.font.render(text, True, (255, 255, 255))
        self.window.blit(surf, surf.get_rect(**{anchor: pos}))

    def _draw_panel(self):
        mouse = pygame.mouse.get_pos()
        x = BOARD_SIZE + 30

        self.window.blit(self.panel_bg, (BOARD_SIZE, 0))

        s = self.stats
        lines = [
            f"session: {s['session']}/{s['total']}",
            "",
            f"max length: {s['best']}",
            f"avg length: {s['avg']:.1f}",
            f"green apple: {s['green']}",
            f"red apple: {s['red']}",
        ]
        for i, line in enumerate(lines):
            self._text(line, (x, 10 + i * 24))

        if (self.step_by_step):
            self._text("Step by step",
                       (self.next_rect.centerx, self.next_rect.top - 25),
                       center=True)
            img = (self.next_hover if self.next_rect.collidepoint(mouse)
                   else self.next_img)
            self.window.blit(img, self.next_rect)

        img = (self.pause_hover
               if (self.paused or self.pause_rect.collidepoint(mouse))
               else self.pause_img)
        self.window.blit(img, self.pause_rect)

        active = self.current_direction if self.has_moved else None
        for direction, rect in self.key_rects.items():
            img = (self.keys_press[direction] if direction == active
                   else self.keys[direction])
            self.window.blit(img, rect)

        self.window.blit(self.meter_img, self.meter_rect)
        ratio = (self.fps - MIN_FPS) / (MAX_FPS - MIN_FPS)
        cur_x = self.track_left + ratio * (self.track_right - self.track_left)
        cur_y = self.meter_rect.centery + TICK_OFFSET_Y
        self.window.blit(self.tick_img,
                         self.tick_img.get_rect(center=(cur_x, cur_y)))
        self._text(f"speed: {self.fps}",
                   (self.meter_rect.centerx, self.meter_rect.bottom + 20),
                   center=True)

    def _set_fps_from_x(self, x):
        ratio = (x - self.track_left) / (self.track_right - self.track_left)
        ratio = max(0.0, min(1.0, ratio))
        self.fps = MIN_FPS + round(ratio * (MAX_FPS - MIN_FPS))

    def _process_events(self):
        """Handle all pending events. Return True if the user wants to quit."""
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                return (True)
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_ESCAPE):
                    return (True)
                self.step_requested = True
            elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                if (self.step_by_step
                        and self.next_rect.collidepoint(event.pos)):
                    self.step_requested = True
                elif (self.pause_rect.collidepoint(event.pos)):
                    self.paused = not self.paused
                elif (self.meter_rect.inflate(0, 30).collidepoint(event.pos)):
                    self.dragging = True
                    self._set_fps_from_x(event.pos[0])
            elif (event.type == pygame.MOUSEBUTTONUP and event.button == 1):
                self.dragging = False
            elif (event.type == pygame.MOUSEMOTION and self.dragging):
                self._set_fps_from_x(event.pos[0])
        return (False)

    def draw(self, board):
        """
        Render the current board with pygame.

        Args:
            board: actual full board of the game
        """

        self.last_board = board
        size = (len(board[0]) * CELL_SIZE, len(board) * CELL_SIZE)
        if self.screen.get_size() != size:
            self.screen = pygame.Surface(size)

        head_pos = None
        for r_idx, row in enumerate(board):
            for c_idx, cell in enumerate(row):
                if (cell == 'H'):
                    head_pos = (r_idx, c_idx)
                    break
            if (head_pos):
                break

        if (head_pos):
            if self.last_head_pos and self.last_head_pos != head_pos:
                dr = head_pos[0] - self.last_head_pos[0]
                dc = head_pos[1] - self.last_head_pos[1]

                if (abs(dr) + abs(dc) == 1):
                    if (dr == -1):
                        self.current_direction = "UP"
                    elif (dr == 1):
                        self.current_direction = "DOWN"
                    elif (dc == -1):
                        self.current_direction = "LEFT"
                    elif (dc == 1):
                        self.current_direction = "RIGHT"

                self.has_moved = True
            self.last_head_pos = head_pos

        time_ms = pygame.time.get_ticks()
        pulse_factor = 1.0 + 0.15 * math.sin(time_ms * 0.005)

        for row_idx, row in enumerate(board):
            for col_idx, cell in enumerate(row):
                x = col_idx * CELL_SIZE
                y = row_idx * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                if (row_idx + col_idx) % 2 == 0:
                    bg_color = (170, 215, 81)
                else:
                    bg_color = (162, 209, 73)
                pygame.draw.rect(self.screen, bg_color, rect)

        for row_idx, row in enumerate(board):
            for col_idx, cell in enumerate(row):
                if (cell == 'H'):
                    continue

                x = col_idx * CELL_SIZE
                y = row_idx * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                if (cell in self.raw_textures):
                    img = self.raw_textures[cell]
                    current_size = int(CELL_SIZE * pulse_factor)
                    scaled_img = pygame.transform.scale(
                        img, (current_size, current_size))
                    img_rect = scaled_img.get_rect()
                    img_rect.center = rect.center
                    self.screen.blit(scaled_img, img_rect)
                elif (cell != '0'):
                    color = PYGAME_COLORS.get(cell, (0, 0, 0))
                    pygame.draw.rect(self.screen, color, rect)

        if (head_pos):
            r_idx, col_idx = head_pos
            x = col_idx * CELL_SIZE
            y = r_idx * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            base_color = PYGAME_COLORS.get('H', (78, 124, 246))
            pygame.draw.rect(self.screen, base_color, rect)

            if (self.has_moved and 'H' in self.raw_textures):
                img = self.raw_textures['H']
                angle = DIRECTION_ANGLES.get(self.current_direction, 0)
                img = pygame.transform.rotate(img, angle)

                current_size = int(CELL_SIZE * 2)
                scaled_img = pygame.transform.scale(
                    img, (current_size, current_size))
                img_rect = scaled_img.get_rect()
                img_rect.center = rect.center

                self.screen.blit(scaled_img, img_rect)

        self.window.blit(pygame.transform.scale(
            self.screen, (BOARD_SIZE, BOARD_SIZE)), (0, 0))
        self._draw_panel()
        pygame.display.flip()

    def poll_direction(self, idle_fps=30):
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                return ("quit", None)
            elif (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_ESCAPE):
                    return ("quit", None)
                elif (event.key in KEY_TO_DIRECTION):
                    direction = KEY_TO_DIRECTION[event.key]
                    self.current_direction = direction
                    return ("direction", direction)

        self.clock.tick(idle_fps)
        return (None, None)

    def pump_quit(self):
        if (self.quit_requested or self._process_events()):
            self.quit_requested = False
            return (True)
        return (False)

    def wait_for_step(self, idle_fps=30):
        self.step_requested = False
        while (True):
            if (self._process_events()):
                return (False)
            if (self.step_requested):
                return (True)
            self.draw(self.last_board)
            self.clock.tick(idle_fps)

    def tick(self, fps=None):
        """
        Wait one frame at the speed chosen with the slider (the fps argument
        is ignored). Events are still handled while waiting, so the slider,
        the pause button and the window stay responsive even at 1 fps.
        """
        effective_fps = 120 if self.step_by_step else self.fps

        frame_ms = 1000 / effective_fps
        start = pygame.time.get_ticks()
        while (self.paused or pygame.time.get_ticks() - start < frame_ms):
            if (self._process_events()):
                self.quit_requested = True
                return
            if (self.paused or frame_ms > 50):
                self.draw(self.last_board)
            remaining = frame_ms - (pygame.time.get_ticks() - start)
            pygame.time.wait(15 if self.paused
                             else max(1, min(15, int(remaining))))

    def close(self):
        pygame.quit()
