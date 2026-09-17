#!/usr/bin/env -S uv run --script
import random

GRID_COLS = 10
GRID_ROWS = 10

class Snake():
    """
    Snake game structure
    """
    
    def __init__(self):
        self.positions = self._generate_start_body()
        self.direction = (0, 0)
        self.grow = False

    
    def __call__(self):
        return (self.positions)


    def _generate_start_body(self):
        """
        Randomly pick a head position + direction and build a 3-segment
        body, retrying until the whole body fits on the grid.
        """
        while True:
            base_pos_x = random.randint(1, GRID_COLS)
            base_pos_y = random.randint(1, GRID_ROWS)

            if random.randint(0, 1):
                base_dir_x = 0
                base_dir_y = random.choice((1, -1))
            else:
                base_dir_x = random.choice((1, -1))
                base_dir_y = 0

            positions = [
                (base_pos_x, base_pos_y),
                (base_pos_x - base_dir_x, base_pos_y - base_dir_y),
                (base_pos_x - (base_dir_x * 2), base_pos_y - (base_dir_y * 2)),
            ]

            if len(set(positions)) == len(positions) and all(
                1 <= x <= GRID_COLS and 1 <= y <= GRID_ROWS for x, y in positions
            ):
                return (positions)


def create_board():
    """
    Create a snake gaming board
    """
    rows = GRID_ROWS + 2
    cols = GRID_COLS + 2
    board = [['0' for _ in range(cols)] for _ in range(rows)]

    for row in range(len(board)):
        for col in range(len(board[row])):
            if (col == 0 or col == GRID_COLS + 1 or row == 0 or row == GRID_ROWS + 1):
                board[row][col] = 'W'

    return (board)


def update_board(player_pos, board):
    """
    Update Player/Snake & Apples positon
    """
    for index, (pos_x, pos_y) in enumerate(player_pos):
        if index == 0:
            board[pos_y][pos_x] = 'H'
        else:
            board[pos_y][pos_x] = 'S'


def print_board(player_pos, board):
    """
    Display the board as the Snake need to see it
    """
    head_x, head_y = player_pos[0]

    rows = len(board)
    cols = len(board[0])
    vision_board = [[' ' for _ in range(cols)] for _ in range(rows)]

    for row in range(rows):
        vision_board[row][head_x] = board[row][head_x]

    for col in range(cols):
        vision_board[head_y][col] = board[head_y][col]

    for row in vision_board:
        for col in row:
            print(col, end="")
        print("")

    return (vision_board)


def main():
    playing_board = create_board()
    player = Snake()

    update_board(player(), playing_board)
    print_board(player(), playing_board)

    return (0)


if __name__ == "__main__":
    main()
