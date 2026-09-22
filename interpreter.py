WALL = "W"
GREEN = "G"
RED = "R"
SELF = "S"


REWARDS = {
    "green": 30.0,
    "red": -80.0,
    "wall": -30.0,
    "self": -30.0,
    "starved": -15.0,
    None: -0.05,
}


def compute_vision(board, head):
    hx, hy = head

    def scan(dx, dy):
        line = []

        x = hx + dx
        y = hy + dy

        while True:
            symbol = board[y][x]
            line.append(symbol)

            if (symbol == WALL):
                break

            x += dx
            y += dy

        return (line)

    return ({
        "up": scan(0, -1),
        "down": scan(0, 1),
        "left": scan(-1, 0),
        "right": scan(1, 0),
    })


def distance_category(distance):
    if (distance is None):
        return ("NONE")

    if (distance <= 1):
        return ("NEAR")

    if (distance <= 4):
        return ("CLOSE")

    if (distance <= 8):
        return ("MEDIUM")

    return ("FAR")


def summarize(line):
    wall_distance = None
    green_distance = None
    self_distance = None

    for distance, symbol in enumerate(line, start=1):

        if (symbol == WALL):
            wall_distance = distance

        elif (symbol == GREEN and green_distance is None):
            green_distance = distance

        elif (symbol == SELF and self_distance is None):
            self_distance = distance

    return (
        distance_category(wall_distance),
        distance_category(green_distance),
        distance_category(self_distance),
    )


def vision_to_state(vision, previous_action=None):
    return (
        summarize(vision["up"]),
        summarize(vision["down"]),
        summarize(vision["left"]),
        summarize(vision["right"]),
        previous_action,
    )


def get_state(board, head, previous_action=None):
    return (vision_to_state(
        compute_vision(board, head),
        previous_action,
    ))


def reward_for(event):
    return (REWARDS.get(event, -0.05))


def food_distance(state):
    return (None)


def proximity_reward(old_state, new_state):
    values = {
        "NONE": 0,
        "FAR": 1,
        "MEDIUM": 2,
        "CLOSE": 3,
        "NEAR": 4,
    }

    old_best = 0
    new_best = 0

    for direction in old_state[:4]:
        food = direction[1]
        old_best = max(
            old_best,
            values[food],
        )

    for direction in new_state[:4]:
        food = direction[1]
        new_best = max(
            new_best,
            values[food],
        )

    difference = new_best - old_best

    if (difference > 0):
        return (1.5)

    if (difference < 0):
        return (-1.0)

    return (0.0)


def danger_penalty(state, action):
    direction_index = {
        "UP": 0,
        "DOWN": 1,
        "LEFT": 2,
        "RIGHT": 3,
    }

    wall_distance = state[
        direction_index[action]
    ][0]

    self_distance = state[
        direction_index[action]
    ][2]

    penalty = 0.0

    if (wall_distance) == "NEAR":
        penalty -= 4.0

    elif (wall_distance) == "CLOSE":
        penalty -= 0.5

    if (self_distance) == "NEAR":
        penalty -= 4.0

    elif (self_distance) == "CLOSE":
        penalty -= 1.0

    return (penalty)
