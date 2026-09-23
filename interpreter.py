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