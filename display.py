import os
import math
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import pygame  # noqa: E402

from environment import GRID_COLS, GRID_ROWS


CELL_SIZE = 40

PYGAME_COLORS = {
    '0': (40, 40, 40),
    'W': (87, 138, 52),
    'R': (200, 40, 40),
    'G': (40, 180, 40),
    'H': (250, 210, 60),
    'S': (230, 170, 30),
}

KEY_TO_DIRECTION = {
    pygame.K_UP: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT",
}


class Display:
    def __init__(self):
        pygame.init()
        width = (GRID_COLS + 2) * CELL_SIZE
        height = (GRID_ROWS + 2) * CELL_SIZE
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Learn2Slither")
        self.clock = pygame.time.Clock()

        try:
            self.raw_textures = {
                'R': pygame.image.load("texture/red_apple.png").convert_alpha(),
                'G': pygame.image.load("texture/green_apple.png").convert_alpha()
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

                if (cell in self.raw_textures):
                    current_size = int(CELL_SIZE * pulse_factor)
                    scaled_img = pygame.transform.smoothscale(self.raw_textures[cell], (current_size, current_size))

                    img_rect = scaled_img.get_rect()
                    img_rect.center = rect.center
                    
                    self.screen.blit(scaled_img, img_rect)
                    
                elif (cell != '0'):
                    color = PYGAME_COLORS.get(cell, (0, 0, 0))
                    pygame.draw.rect(self.screen, color, rect)

        pygame.display.flip()


    def poll_direction(self, idle_fps=30):
        """
        Process the pygame event queue once and report what happened.

        Returns:
        	tuple: Direction & action like window closing
        """
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                return ("quit", None)
            elif (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_ESCAPE):
                    return ("quit", None)
                elif (event.key in KEY_TO_DIRECTION):
                    return ("direction", KEY_TO_DIRECTION[event.key])

        self.clock.tick(idle_fps)
        return (None, None)


    def close(self):
        pygame.quit()
