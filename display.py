import os
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import pygame  # noqa: E402

from environment import GRID_COLS, GRID_ROWS


CELL_SIZE = 40

PYGAME_COLORS = {
    '0': (40, 40, 40),
    'W': (220, 220, 220),
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


    def draw(self, board):
        """
        Render the current board with pygame.
        
        Args:
			board: actual full board of the game
        """
        self.screen.fill((0, 0, 0))
        for row_idx, row in enumerate(board):
            for col_idx, cell in enumerate(row):
                color = PYGAME_COLORS.get(cell, (0, 0, 0))
                rect = pygame.Rect(col_idx * CELL_SIZE, row_idx * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (10, 10, 10), rect, 1)
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
