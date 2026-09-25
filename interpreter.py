from environment import (
    create_board, update_board, print_board,
    Snake, GoodApple, BadApple
)

WALL = "W"
GREEN = "G"
RED = "R"
SELF = "S"

REWARDS = {
    "green": 30.0,
    "red": -10.0,
    "wall": -100.0,
    "self": -100.0,
    "starved": -100.0,
    None: -0.5,
}

DIRS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

OPPOSITES = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
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
        Move the player according to the requested direction.
        Deny 360 degre turn of the player

        Returns an event describing what happened:
            None       -> normal movement
            "green"    -> ate a green apple
            "red"      -> ate a red apple
            "wall"     -> hit a wall
            "self"     -> hit itself
            "starved"  -> snake died after eating a red apple
        """

        if (self.game_over):
            return (None)

        if (self.current_direction and
           requested_direction == OPPOSITES.get(self.current_direction)):
            action = self.current_direction
        else:
            action = requested_direction

        self.current_direction = action
        dx, dy = DIRS[action]

        positions = self.snake()
        head_x, head_y = positions[0]
        new_head = (head_x + dx, head_y + dy)

        target_cell = self.board[new_head[1]][new_head[0]]

        if (target_cell == 'W'):
            self.game_over = True
            return ("wall")

        will_grow = new_head in (
            self.good_apple_1(),
            self.good_apple_2()
        )

        tail = positions[-1]
        body_ahead = positions if will_grow else positions[:-1]

        if (new_head in body_ahead and new_head != tail):
            self.game_over = True
            return ("self")

        positions.insert(0, new_head)

        if (new_head == self.good_apple_1()):
            occupied = set(positions) | {
                self.good_apple_2(),
                self.bad_apple()
            }

            self.good_apple_1.respawn(occupied)

            self.snake.positions = positions
            return ("green")

        elif (new_head == self.good_apple_2()):
            occupied = set(positions) | {
                self.good_apple_1(),
                self.bad_apple()
            }

            self.good_apple_2.respawn(occupied)

            self.snake.positions = positions
            return ("green")

        elif (new_head == self.bad_apple()):
            occupied = set(positions) | {
                self.good_apple_1(),
                self.good_apple_2()
            }

            self.bad_apple.respawn(occupied)

            positions.pop()

            if (positions):
                positions.pop()

            self.snake.positions = positions

            if (len(positions) <= 0):
                self.game_over = True
                return ("starved")

            return ("red")

        else:
            positions.pop()

        self.snake.positions = positions

        return (None)

    def show_vision(self):
        """
        Display on the terminal the board the snake Agent see.
        """

        if (self.terminal_output):
            print_board(self.snake(), self.board)


def compute_vision(board, head):
    """
    Scan the 4 lines of sight from the head

    Args:
        board: full game board
        head: head position

    Returns:
        up: column from upper wall to head
        down: column from head to lower wall
        left: line from left wall to head
        right: line from head to right wall
    """
    hx, hy = head

    def scan(dx, dy):
        line = []
        x, y = hx + dx, hy + dy

        while (True):
            symbol = board[y][x]
            line.append(symbol)

            if (symbol == WALL or symbol == SELF):
                break

            x += dx
            y += dy

        return (line)

    return {
        "up": scan(0, -1),
        "down": scan(0, 1),
        "left": scan(-1, 0),
        "right": scan(1, 0),
    }


def summarize(line):
    """
    Return the immediate neighbour (danger check) and
    whether a green or red apple is visible anywhere along the line

    Args:
        line: neighbour case

    Returns:
        nearest: state of the neighbour
        has_green (bool): check Green Apple
        has_red (bool): check Red Apple
        has_self (bool): check Snake part
    """
    nearest = line[0]
    has_green = GREEN in line
    has_red = RED in line
    has_self = SELF in line
    return (nearest, has_green, has_red, has_self)


def vision_to_state(vision, previous_action=None):
    """
    Check for each direction the state of the board by the agent vision

    Args:
        vision: vision board of the agent
        previous_action: previous action

    Returns:
        vision_up: upper case actual state
        vision_down: down case actual state
        vision_left: left case actual state
        vision_right: right case actual state
        previous_action: previous action
    """
    return (
        summarize(vision["up"]),
        summarize(vision["down"]),
        summarize(vision["left"]),
        summarize(vision["right"]),
        previous_action,
    )


def get_state(board, head, previous_action=None):
    return (vision_to_state(compute_vision(board, head), previous_action))


def reward_for(event):
    return (REWARDS.get(event, -0.5))
