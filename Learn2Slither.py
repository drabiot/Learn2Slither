#!/usr/bin/env python3
import sys
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

from environment import (
    GRID_COLS, GRID_ROWS,
    create_board, update_board, print_board,
    Snake, GoodApple, BadApple,
)

CELL_SIZE = 40

PYGAME_COLORS = {
    '0': (40, 40, 40),
    'W': (220, 220, 220),
    'R': (200, 40, 40),
    'G': (40, 180, 40),
    'H': (250, 210, 60),
    'S': (230, 170, 30),
}

DIRS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}
OPPOSITE = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}

KEY_TO_DIRECTION = {
    pygame.K_UP: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT",
}


def initial_direction_from_snake(positions):
    """
    Figure out which way the snake is already facing at spawn time,
    from the offset between its head and the segment right behind it,
    instead of assuming an arbitrary default.
    
    Args:
		positions: position of the Snake
	
    Returns:
		str: direction of the snake 
    """
    hx, hy = positions[0]
    nx, ny = positions[1]
    dx, dy = hx - nx, hy - ny
    for name, (ddx, ddy) in DIRS.items():
        if ((ddx, ddy) == (dx, dy)):
            return (name)
    return ("RIGHT")


class Game:
    def __init__(self, visual=True, terminal_output=True):
        self.visual = visual
        self.terminal_output = terminal_output

        self.board = create_board()
        self.snake = Snake()

        occupied = set(self.snake())
        self.good_apple_1 = GoodApple(occupied)
        occupied.add(self.good_apple_1())
        self.good_apple_2 = GoodApple(occupied)
        occupied.add(self.good_apple_2())
        self.bad_apple = BadApple(occupied)
        occupied.add(self.bad_apple())

        self.current_direction = initial_direction_from_snake(self.snake())
        self.game_over = False

        self.screen = None
        self.clock = None
        if (self.visual):
            pygame.init()
            width = (GRID_COLS + 2) * CELL_SIZE
            height = (GRID_ROWS + 2) * CELL_SIZE
            self.screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("Learn2Slither")
            self.clock = pygame.time.Clock()


    def refresh_board(self):
        """
        Clear the snake & apples from the board.
        """
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if (self.board[row][col] != 'W'):
                    self.board[row][col] = '0'

        update_board(self.snake(), self.good_apple_1(), self.good_apple_2(), self.bad_apple(), self.board,)


    def compute_action(self, requested_direction):
        """
        Compute the action taken by the player to move the snake.
        If the player want to take a 360° turn, deny the move to respect sanke game movement.
        
        Args:
			requested_direction: requested direction taken by the player
        
        Returns:
			str: final decision if the move is coherent to the snake current direction
        """
        if (requested_direction == OPPOSITE[self.current_direction] and len(self.snake()) > 1):
            return (self.current_direction)
        return (requested_direction)


    def step(self, requested_direction):
        """
        Move the player accordingly to the direction he suggested if possible.
        Handle apple eating and loop mechanics wuth Game Over, when touching wall, snake part or if the snake die because of Red Apple.
        
        Args:
			requested_direction: requested direction taken by the player
        """
        if (self.game_over):
            return

        action = self.compute_action(requested_direction)
        self.current_direction = action
        dx, dy = DIRS[action]

        positions = self.snake()
        head_x, head_y = positions[0]
        new_head = (head_x + dx, head_y + dy)

        target_cell = self.board[new_head[1]][new_head[0]]
        if (target_cell == 'W'):
            self.game_over = True
            return

        will_grow = new_head in (self.good_apple_1(), self.good_apple_2())
        tail = positions[-1]
        body_ahead = positions if will_grow else positions[:-1]
        if (new_head in body_ahead and new_head != tail):
            self.game_over = True
            return

        positions.insert(0, new_head)

        if (new_head == self.good_apple_1()):
            occupied = set(positions) | {self.good_apple_2(), self.bad_apple()}
            self.good_apple_1.respawn(occupied)
        elif (new_head == self.good_apple_2()):
            occupied = set(positions) | {self.good_apple_1(), self.bad_apple()}
            self.good_apple_2.respawn(occupied)
        elif (new_head == self.bad_apple()):
            occupied = set(positions) | {self.good_apple_1(), self.good_apple_2()}
            self.bad_apple.respawn(occupied)
            positions.pop()

            if (positions):
                positions.pop()
        else:
            positions.pop()

        self.snake.positions = positions

        if (len(positions) <= 0):
            self.game_over = True


    def draw(self):
        """
        Draw the board with pygame.
        """
        if (not self.visual):
            return
        
        self.screen.fill((0, 0, 0))
        for row_idx, row in enumerate(self.board):
            for col_idx, cell in enumerate(row):
                color = PYGAME_COLORS.get(cell, (0, 0, 0))
                rect = pygame.Rect(col_idx * CELL_SIZE, row_idx * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (10, 10, 10), rect, 1)
        pygame.display.flip()


    def show_vision(self):
        """
        Display on the terminal the board the snake Agent see. 
        """
        if (self.terminal_output):
            print_board(self.snake(), self.board)


    def run_human(self):
        """
        Able human run the game to debug.
        """
        running = True

        self.refresh_board()
        self.show_vision()
        self.draw()

        while (running and not self.game_over):
            direction_pressed = None

            if (self.visual):
                for event in pygame.event.get():
                    if (event.type == pygame.QUIT):
                        running = False
                    elif (event.type == pygame.KEYDOWN):
                        if (event.key == pygame.K_ESCAPE):
                            running = False
                        elif (event.key in KEY_TO_DIRECTION):
                            direction_pressed = KEY_TO_DIRECTION[event.key]

            if (direction_pressed is None):
                if (self.visual):
                    self.draw()
                    self.clock.tick(30)
                continue

            self.step(direction_pressed)
            self.refresh_board()

            if (self.game_over):
                self.draw()
                break

            self.show_vision()
            if (self.terminal_output):
                print(f"\n{self.current_direction}\n")
            self.draw()

        if (self.visual):
            pygame.quit()


def main():
    game = Game(visual=True, terminal_output=True)
    game.run_human()
    return 0


if __name__ == "__main__":
    sys.exit(main())