import os
import math
from environment import GRID_COLS, GRID_ROWS
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import pygame  # noqa: E402

CELL_SIZE = 40

PYGAME_COLORS = {
    '0': (40, 40, 40),
    'W': (87, 138, 52),
    'R': (200, 40, 40),
    'G': (40, 180, 40),
    'H': (78, 124, 246),
    'S': (66, 111, 227),
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


class Display:
    def __init__(self):
        pygame.init()
        width = (GRID_COLS + 2) * CELL_SIZE
        height = (GRID_ROWS + 2) * CELL_SIZE
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Learn2Slither")
        self.clock = pygame.time.Clock()

        self.current_direction = "UP"
        self.last_head_pos = None
        self.has_moved = False

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

    def draw(self, board):
        """
        Render the current board with pygame.

        Args:
            board: actual full board of the game
        """

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

    def close(self):
        pygame.quit()
