import random

GRID_COLS = 10
GRID_ROWS = 10

def set_grid_size(size):
    """
    Change the grid size by the given value
    
    Args:
		size: number of case
    """
    global GRID_COLS, GRID_ROWS
    GRID_COLS = size
    GRID_ROWS = size

COLOR_RESET = "\033[0m"

COLORS = {
    '0': "\033[90m",  # NOTHING
    'W': "\033[97m",  # WALL
    'R': "\033[31m",  # BAD APPLE
    'G': "\033[32m",  # GOOD APPLE
    'H': "\033[94m",  # HEAD
    'S': "\033[34m",  # SNAKE
}


class Snake():
    def __init__(self):
        self.positions = self._generate_start_body()
        self.direction = (0, 0)
        self.grow = False

    def __call__(self):
        return (self.positions)

    def _generate_start_body(self):
        """
        Randomly pick a head position + direction and build a 3-segment body,
        retrying up to a maximum limit to avoid infinite loops.
        """

        attempts = 0
        max_attempts = 1000

        while (attempts < max_attempts):
            base_pos_x = random.randint(1, GRID_COLS)
            base_pos_y = random.randint(1, GRID_ROWS)

            if (random.randint(0, 1)):
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

            if (len(set(positions)) == len(positions) and
                all(1 <= x <= GRID_COLS and
                    1 <= y <= GRID_ROWS for x, y in positions)):
                return (positions)

            attempts += 1

        raise RuntimeError("Error: Can't place the snake")


class Apple:
    def __init__(self, excluded_positions):
        self.position = self.random_position(excluded_positions)

    def __call__(self):
        return (self.position)

    def random_position(self, excluded_positions):
        """
        Create new position for the apple in a spot where no apple or snake is,
        with a safety exit if the board is full.
        """

        attempts = 0
        max_attempts = 10000

        while (attempts < max_attempts):
            position = (random.randint(1, GRID_COLS),
                        random.randint(1, GRID_ROWS))
            if (position not in excluded_positions):
                return (position)
            attempts += 1

        raise RuntimeError("Error: Can't place apple")

    def respawn(self, excluded_positions):
        self.position = self.random_position(excluded_positions)


class GoodApple(Apple):
    pass


class BadApple(Apple):
    pass


def create_board():
    """
    Create & init the snake gaming board.
    """

    rows = GRID_ROWS + 2
    cols = GRID_COLS + 2
    board = [['0' for _ in range(cols)] for _ in range(rows)]

    for row in range(len(board)):
        for col in range(len(board[row])):
            if (col == 0 or col == GRID_COLS + 1 or
               row == 0 or row == GRID_ROWS + 1):
                board[row][col] = 'W'

    return (board)


def update_board(player_pos, good_apple_pos_1,
                 good_apple_pos_2, bad_apple_pos, board):
    """
    Update Player/Snake & Apples position on the Board.
    """

    for index, (pos_x, pos_y) in enumerate(player_pos):
        if index == 0:
            board[pos_y][pos_x] = 'H'
        else:
            board[pos_y][pos_x] = 'S'

    board[good_apple_pos_1[1]][good_apple_pos_1[0]] = 'G'
    board[good_apple_pos_2[1]][good_apple_pos_2[0]] = 'G'
    board[bad_apple_pos[1]][bad_apple_pos[0]] = 'R'


def print_board(player_pos, board):
    """
    Display the board in the terminal as the Snake need to see it.
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
            color_code = COLORS.get(col, "")
            print(f"{color_code}{col}{COLOR_RESET}", end="")
        print("")

    return (vision_board)


def debug_board(board):
    """
    Display the board in the terminal.
    """

    print("")
    for row in board:
        for col in row:
            color_code = COLORS.get(col, "")
            print(f"{color_code}{col}{COLOR_RESET}", end="")
        print("")
