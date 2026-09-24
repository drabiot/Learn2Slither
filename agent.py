#!/usr/bin/env -S uv run --script
import argparse
import pickle
import random
import sys
from collections import deque

from environment import set_grid_size
from interpreter import compute_vision, vision_to_state, reward_for, Game

ACTIONS = ("UP", "DOWN", "LEFT", "RIGHT")
DIRECTIONS = {"UP":0, "DOWN":1, "LEFT":2, "RIGHT":3}

LOOP_WINDOW = 30
LOOP_MIN_UNIQUE = 5
LOOP_PENALTY = -5.0


class Agent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=1.0,
                 epsilon_min=0.001, epsilon_decay=0.999):
        self.q_table = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

    def _ensure(self, state):
        if (state not in self.q_table):
            self.q_table[state] = {a: 0.0 for a in ACTIONS}

    def choose_action(self, state, learn=True):
        """
        Choose an action for the given state using an epsilon-greedy policy.
        
        During learning, the agent explores by randomly selecting an action
        with probability epsilon. The random action is selected only among
        safe actions to prevent the agent from deliberately choosing
        a suicidal or invalid action.
        
        Otherwise, the agent exploits the Q-table by selecting one
        of the actions with the highest Q-value.
        If several actions have the same maximum Q-value,
        one of them is selected randomly.

        Args:
            state: current state of the environment
            learn: whether the agent is currently learning
            If True, epsilon is used to balance exploration and exploitation
            If False, the agent always selects an action based on the Q-table
            
        Returns:
            action: action selected by the agent
        """
        self._ensure(state)

        safe_actions = [
            action for action in ACTIONS
            if state[DIRECTIONS[action]][0] not in ()
        ]

        if (not safe_actions):
            safe_actions = list(ACTIONS)

        if (learn and random.random() < self.epsilon):
            return (random.choice(safe_actions))

        safe_values = {a: self.q_table[state][a] for a in safe_actions}
        best = max(safe_values.values())
        best_actions = [a for a, v in safe_values.items() if v == best]

        return (random.choice(best_actions))

    def update(self, state, action, reward, next_state, done):
        """
        Update the state of our agent by the Q-table

        Args:
            state: current state of the environment
            action: action taken by the agent in the current state
            reward: reward received after taking the action
            next_state: state reached after taking the action
            done: Whether the episode has ended after this transition
        """
        self._ensure(state)
        self._ensure(next_state)
        current = self.q_table[state][action]
        future = 0.0 if done else max(self.q_table[next_state].values())
        target = reward + self.gamma * future
        self.q_table[state][action] += self.alpha * (target - current)

    def decay_epsilon(self, session=None, total_sessions=None):
        """
        Decay the percentage of randomness allowed for the agent 
        based on the training progress (sessions).
        """
        if not hasattr(self, "episode_count"):
            self.episode_count = 0
        self.episode_count += 1

        s = session if session is not None else self.episode_count
        t = total_sessions if total_sessions is not None else getattr(self, "total_sessions", 1000)

        progress = min(1.0, s / t)
        self.epsilon = max(
            self.epsilon_min,
            1.0 - (1.0 - self.epsilon_min) * progress
        )

    def save(self, path):
        """
        Save in a Q-table the stats

        Args:
            path: path where we want the Q-table to be saved
        """
        with open(path, "wb") as f:
            pickle.dump({
                "q_table": self.q_table,
                "alpha": self.alpha,
                "gamma": self.gamma,
                "epsilon": self.epsilon,
                "epsilon_min": self.epsilon_min,
                "epsilon_decay": self.epsilon_decay,
            }, f)

    @classmethod
    def load(cls, path):
        """
        Load a Q-table

        Args:
            cls: class Agent
            path: path of the Q-table to load

        Returns:
            agent: the agent with the loaded Q-table
        """
        with open(path, "rb") as f:
            data = pickle.load(f)

        agent = cls(
            alpha=data["alpha"], gamma=data["gamma"],
            epsilon=data["epsilon"], epsilon_min=data["epsilon_min"],
            epsilon_decay=data["epsilon_decay"],
        )
        agent.q_table = data["q_table"]

        return (agent)


def play_epoch(agent, learn=True, visual=False, terminal_output=False,
                 display=None, fps=8, max_steps=2000, session=1, session_max=100):
    """
    Train sessions by session our agent

    Args:
        agent: AI that train
        learn (bool): disable or not the agent learning
        visual (bool): (on | off) display graphically the full board
        terminal_output (bool): (on | off) display the agent board vision
        in terminal
        display: graphic interface that show the board
        fps (int): frame per second to accelerate or not the speed of the agent
        max_steps (int): max step the agent can do before dying 
        to prevent infinite loop

    Returns:
        max_length (int): maximum size the agent being in one session
        max_duration (int): maximum step the agent do in one session
    """
    game = Game(terminal_output=terminal_output)
    game.refresh_board()

    max_length = len(game.snake())
    steps = 0
    previous_action = None

    recent_positions = deque(maxlen=LOOP_WINDOW)
    if game.snake():
        recent_positions.append(game.snake()[0])

    if (visual):
        display.draw(game.board)

    while (not game.game_over and steps < max_steps):
        state = vision_to_state(
            compute_vision(game.board, game.snake()[0]), previous_action
        )

        if (terminal_output):
            game.show_vision()

        action = agent.choose_action(state, learn=learn)
        event = game.step(action)
        game.refresh_board()
        steps += 1

        if (game.snake()):
            max_length = max(max_length, len(game.snake()))
            recent_positions.append(game.snake()[0])

        if (terminal_output):
            print(f"\n{action}\n")
        if (visual):
            display.draw(game.board)
            if (display.pump_quit()):
                game.game_over = True
            display.tick(fps)

        reward = reward_for(event)
        if len(recent_positions) == LOOP_WINDOW:
            if len(set(recent_positions)) <= LOOP_MIN_UNIQUE:
                reward += LOOP_PENALTY

        if (game.game_over):
            next_state = state
        else:
            next_state = vision_to_state(
                compute_vision(game.board, game.snake()[0]), action
            )

        if (learn):
            agent.update(state, action, reward, next_state, game.game_over)

        previous_action = action

    if (learn):
        agent.decay_epsilon(session, session_max)

    return ({"max_length": max_length, "duration": steps})


def train(sessions, agent, save_path=None, learn=True, visual=False,
          terminal_output=False, fps=8, max_steps=2000, board_size=10):
    """
    Train our Agent and display stats about the training

    Args:
        sessions (int): number of session the agent need to do
        agent: AI that train
        save_path (str): path where we need to save the created Q-table
        learn (bool): disable or not the agent learning
        visual (bool): (on | off) display graphically the full board
        terminal_output (bool): (on | off) display the agent board vision
        in terminal
        fps (int): frame per second to accelerate or not the speed of the agent
        max_steps (int): max step the agent can do before dying
        to prevent infinite loop
    """
    set_grid_size(board_size)
    display = None

    if (visual):
        from display import Display
        display = Display()

    best_length = 0
    length_mean = 0

    for session in range(1, sessions + 1):
        stats = play_epoch(
            agent, learn=learn, visual=visual,
            terminal_output=terminal_output, display=display, fps=fps,
            max_steps=max_steps, session=session, session_max=sessions
        )
        best_length = max(best_length, stats["max_length"])
        length_mean = length_mean + stats["max_length"]

        print(
            f"Session {session}/{sessions} - "
            f"max length = {stats['max_length']}, "
            f"duration = {stats['duration']}, "
            f"best so far = {best_length}, "
            f"lenght average = {length_mean / session}"
        )

    if (visual):
        display.close()

    if (save_path):
        agent.save(save_path)
        print(f"Save learning state in {save_path}")


def parse_args():
    """
    Parse given argument to modify agent behaviour

    Returns:
        sessions (int): number of session the agent need to do
        save (path | str): save in the given Q-table
        load (path | str): load the given Q-table 
        visual (bool): (on | off) display graphically the full board
        dontlearn (bool): disable the agent learning
        terminal (bool): (on | off) display the agent board vision in terminal
        fps (int): frame per second to accelerate or not the speed of the agent
        max-steps (int): max step the agent can do before dying 
        to prevent infinite loop
    """
    parser = argparse.ArgumentParser(description="Learn2Slither Q-learning agent")
    parser.add_argument("-sessions", type=int, default=1)
    parser.add_argument("-save", type=str, default=None)
    parser.add_argument("-load", type=str, default=None)
    parser.add_argument("-visual", choices=["on", "off"], default="off")
    parser.add_argument("-dontlearn", action="store_true")
    parser.add_argument("-terminal", choices=["on", "off"], default="off")
    parser.add_argument("-fps", type=int, default=8)
    parser.add_argument("-max-steps", type=int, default=2000, dest="max_steps")
    return (parser.parse_args())


def main():
    args = parse_args()

    if (args.load):
        agent = Agent.load(args.load)
        print(f"Load trained model from {args.load}")
    else:
        agent = Agent()

    train(
        sessions=args.sessions,
        agent=agent,
        save_path=args.save,
        learn=not args.dontlearn,
        visual=(args.visual == "on"),
        terminal_output=(args.terminal == "on"),
        fps=args.fps,
        max_steps=args.max_steps,
    )
    return (0)


if __name__ == "__main__":
    sys.exit(main())