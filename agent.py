#!/usr/bin/env -S uv run --script

import argparse
import pickle
import random
import sys
from collections import deque

from Learn2Slither import Game

from interpreter import (
    compute_vision,
    vision_to_state,
    reward_for,
    proximity_reward,
    danger_penalty,
)


ACTIONS = (
    "UP",
    "DOWN",
    "LEFT",
    "RIGHT",
)


DIRECTION_INDEX = {
    "UP": 0,
    "DOWN": 1,
    "LEFT": 2,
    "RIGHT": 3,
}


OPPOSITE = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}


class Agent:

    def __init__(
        self,
        alpha=0.10,
        gamma=0.95,
        epsilon=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.9999,
    ):
        self.q_table = {}

        self.alpha = alpha
        self.gamma = gamma

        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

    def _ensure(self, state):

        if( state not in self.q_table):
            self.q_table[state] = {
                action: 0.0
                for action in ACTIONS
            }


    def _safe_actions(self, state, previous_action=None):
        safe = []

        for action in ACTIONS:

            if previous_action is not None:
                if action == OPPOSITE[previous_action]:
                    continue

            index = DIRECTION_INDEX[action]

            wall_distance = state[index][0]
            self_distance = state[index][2]

            if (wall_distance == "NEAR"):
                continue
            if (self_distance == "NEAR"):
                continue

            safe.append(action)

        return (safe)

    def choose_action(self, state, learn=True):
        self._ensure(state)

        previous_action = state[4]

        safe_actions = self._safe_actions(state, previous_action)

        if (not safe_actions):
            safe_actions = [
                action
                for action in ACTIONS
                if (
                    previous_action is None
                    or action != OPPOSITE[previous_action]
                )
            ]

        if (not safe_actions):
            safe_actions = list(ACTIONS)

        if (learn and random.random() < self.epsilon):
            return (random.choice(
                safe_actions
            ))

        values = self.q_table[state]

        best_value = max(
            values[action]
            for action in safe_actions
        )

        best_actions = [
            action
            for action in safe_actions
            if values[action] == best_value
        ]

        return (random.choice(best_actions))

    def update(self, state, action, reward, next_state, done):
        self._ensure(state)
        self._ensure(next_state)

        current = self.q_table[state][action]

        if (done):
            future = 0.0
        else:
            safe_actions = self._safe_actions(
                next_state,
                next_state[4],
            )
            if (safe_actions):
                future = max(
                    self.q_table[next_state][a]
                    for a in safe_actions
                )
            else:
                future = max(
                    self.q_table[next_state].values()
                )

        target = (reward + self.gamma * future)

        self.q_table[state][action] += (
            self.alpha
            * (target - current)
        )


    def decay_epsilon(self):
        self.epsilon = max(
            self.epsilon_min,
            self.epsilon * self.epsilon_decay,
        )

    def save(self, path):
        with open(path, "wb") as file:
            pickle.dump(
                {
                    "q_table": self.q_table,
                    "alpha": self.alpha,
                    "gamma": self.gamma,
                    "epsilon": self.epsilon,
                    "epsilon_min": self.epsilon_min,
                    "epsilon_decay": self.epsilon_decay,
                },
                file,
            )

    @classmethod
    def load(cls, path):

        with open(path, "rb") as file:
            data = pickle.load(file)

        agent = cls(
            alpha=data["alpha"],
            gamma=data["gamma"],
            epsilon=data["epsilon"],
            epsilon_min=data["epsilon_min"],
            epsilon_decay=data["epsilon_decay"],
        )

        agent.q_table = data["q_table"]

        return (agent)

def play_epoch(agent, learn=True, visual=False, terminal_output=False, display=None, fps=8, max_steps=2000):
    game = Game(terminal_output=terminal_output)
    game.refresh_board()
    max_length = len(game.snake())
    steps = 0
    food_eaten = 0
    previous_action = None
    recent_positions = deque(maxlen=30)

    if (game.snake()):
        recent_positions.append(
            game.snake()[0]
        )

    if (visual):
        display.draw(
            game.board
        )

    while (not game.game_ove and steps < max_steps):
        state = vision_to_state(
            compute_vision(
                game.board,
                game.snake()[0],
            ),
            previous_action,
        )

        if (terminal_output):
            game.show_vision()

        action = agent.choose_action(
            state,
            learn=learn,
        )

        event = game.step(
            action
        )

        game.refresh_board()

        steps += 1


        if (game.snake()):
            current_length = len(
                game.snake()
            )

            max_length = max(
                max_length,
                current_length,
            )

            recent_positions.append(
                game.snake()[0]
            )

        if (event == "green"):
            food_eaten += 1

        if (game.game_over):
            next_state = state

        else:
            next_state = vision_to_state(
                compute_vision(
                    game.board,
                    game.snake()[0],
                ),
                action,
            )

        reward = reward_for(event)

        if (event != "green"):
            reward += proximity_reward(
                state,
                next_state,
            )
            reward += danger_penalty(
                state,
                action,
            )

        if (len(recent_positions) >= 15):
            unique_positions = len(
                set(recent_positions)
            )
            if (unique_positions <= 4):
                reward -= 0.5

        if (learn):
            agent.update(
                state=state,
                action=action,
                reward=reward,
                next_state=next_state,
                done=game.game_over,
            )

        if (terminal_output):

            print(f"\nAction  : {action}")
            print(f"Event   : {event}")
            print(f"Reward  : {reward:.2f}")
            print(f"Length  : {len(game.snake())}")

        if (visual):
            display.draw(game.board)

            if (display.pump_quit()):
                game.game_over = True

            display.tick(fps)

        previous_action = action

    if (learn):
        agent.decay_epsilon()

    return {
        "max_length": max_length,
        "food_eaten": food_eaten,
        "duration": steps,
    }


def train(sessions, agent, save_path=None, learn=True, visual=False, terminal_output=False, fps=8, max_steps=2000):
    display = None

    if (visual):
        from display import Display

        display = Display()

    total_food = 0
    total_length = 0
    total_steps = 0

    best_length = 0

    for session in range(1, sessions + 1):

        stats = play_epoch(
            agent=agent,
            learn=learn,
            visual=visual,
            terminal_output=terminal_output,
            display=display,
            fps=fps,
            max_steps=max_steps,
        )

        total_food += stats["food_eaten"]
        total_length += stats["max_length"]
        total_steps += stats["duration"]
        best_length = max(best_length, stats["max_length"])
        avg_length = (total_length / session)
        avg_food = (total_food / session)
        avg_steps = (total_steps / session)

        print(
            f"Session {session:6d}/{sessions} | "
            f"length={stats['max_length']:3d} | "
            f"food={stats['food_eaten']:2d} | "
            f"steps={stats['duration']:4d} | "
            f"avg_length={avg_length:6.2f} | "
            f"avg_food={avg_food:5.2f} | "
            f"epsilon={agent.epsilon:.4f} | "
            f"states={len(agent.q_table)}"
        )

    if visual and display:
        display.close()

    print()
    print("=" * 70)
    print("TRAINING FINISHED")
    print("=" * 70)
    print(
        f"Best length : {best_length}"
    )
    print(
        f"Q states    : {len(agent.q_table)}"
    )
    print(
        f"Epsilon     : {agent.epsilon:.4f}"
    )

    if save_path:

        agent.save(
            save_path
        )

        print(
            f"Saved model : {save_path}"
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description=("Learn2Slither Q-learning agent")
        )
    parser.add_argument("-sessions", type=int, default=10000)
    parser.add_argument("-save", type=str, default=None)
    parser.add_argument("-load", type=str, default=None)
    parser.add_argument("-visual", choices=["on", "off"], default="off")
    parser.add_argument("-dontlearn", action="store_true")
    parser.add_argument("-terminal", choices=["on", "off"], default="off")
    parser.add_argument("-fps", type=int, default=8)
    parser.add_argument("-max-steps", type=int, default=2000, dest="max_steps")

    return parser.parse_args()


def main():
    args = parse_args()

    if (args.load):
        agent = Agent.load(args.load)
        print(f"Model loaded: {args.load}")
        print(f"Q states: {len(agent.q_table)}")
        print(f"Epsilon: {agent.epsilon:.4f}")
    else:
        agent = Agent()
        print("New Q-learning agent")

    train(
        sessions = args.sessions,
        agent = agent,
        save_path = args.save,
        learn = not args.dontlearn,
        visual = (args.visual == "on"),
        terminal_output = (args.terminal == "on"),
        fps = args.fps,
        max_steps = args.max_steps,
    )

    return (0)


if __name__ == "__main__":
    sys.exit(main())
