#!/usr/bin/env -S uv run --script
import sys

from environment import (
    GRID_COLS, GRID_ROWS,
    create_board, update_board, print_board,
    Snake, GoodApple, BadApple
)
from display import Display


DIRS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}


class Game:
    def __init__(self, terminal_output=True):
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

        self.current_direction = None
        self.game_over = False

    def refresh_board(self):
        """
        Clear the snake & apples from the board.
        """
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if (self.board[row][col] != 'W'):
                    self.board[row][col] = '0'

        update_board(self.snake(), self.good_apple_1(),
                     self.good_apple_2(), self.bad_apple(), self.board)

    def step(self, requested_direction):
        """
        Move the player accordingly to the direction he suggested if possible.
        Handle apple eating and loop mechanics wuth Game Over,
        when touching wall,
        snake part or if the snake die because of Red Apple.

        Args:
            requested_direction: requested direction taken by the player
        """
        if (self.game_over):
            return

        action = requested_direction
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
            occupied = set(positions) | (
                {self.good_apple_2(), self.bad_apple()})
            self.good_apple_1.respawn(occupied)
        elif (new_head == self.good_apple_2()):
            occupied = set(positions) | (
                {self.good_apple_1(), self.bad_apple()})
            self.good_apple_2.respawn(occupied)
        elif (new_head == self.bad_apple()):
            occupied = set(positions) | (
                {self.good_apple_1(), self.good_apple_2()})
            self.bad_apple.respawn(occupied)
            positions.pop()

            if (positions):
                positions.pop()
        else:
            positions.pop()

        self.snake.positions = positions

        if (len(positions) <= 0):
            self.game_over = True

    def show_vision(self):
        """
        Display on the terminal the board the snake Agent see.
        """

        if (self.terminal_output):
            print_board(self.snake(), self.board)


def run_human_pygame(game):
    """
    """

    display = Display()
    game.refresh_board()
    game.show_vision()
    display.draw(game.board)

    running = True
    while running and not game.game_over:
        kind, value = display.poll_direction()

        if kind == "quit":
            running = False
            continue
        if kind != "direction":
            display.draw(game.board)
            continue

        game.step(value)
        game.refresh_board()

        if game.game_over:
            display.draw(game.board)
            break

        if game.terminal_output:
            print(f"\n{game.current_direction}\n")
        game.show_vision()
        display.draw(game.board)

    display.close()


def main():
    game = Game(terminal_output=True)
    run_human_pygame(game)
    return 0


if __name__ == "__main__":
    sys.exit(main())
