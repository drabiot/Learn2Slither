<div align="center">
  <h1> 🐍 Learn2Slither
  </h1>
</div>

---

Reinforcment Learning.<br>
In this project, we need to teach a snake to collect as many fruit as possible without dying.

![Static Badge](https://img.shields.io/badge/language-python_3-yellow)

## Summary

- [Installation](#installation)
- [Usage](#usage)
  - [Terminal](#terminal)
  - [Graphic](#graphic)
- [Agent](#agent)
- [Agent Usage](#agent-usage)
- [Sources](#sources)


## Installation

Clone the project

```bash
  git clone https://github.com/drabiot/Learn2Slither.git
```

Go to the project directory

```bash
  cd Learn2Slither
```

Generate the environment

```bash
  ./setup.sh
```

## Usage
You have two way on how to use this project:
 - Terminal is for person who knows what they want quickly for debugg for example
 - Display is for person who discover the project or want beautiful interfaces and informations

### Terminal
To use the terminal quickly you'll need to execute agent.py program with or without the flags.

```bash
  ./agent.py <flags>
```

| Flag | Utility | Default | Type | Example |
| ---- | ------- | :-----: | :--: | ------- |
| -sessions | Number of run the agent will make in one go | 1 | int | -sessions=1 |
| -save | Saving path where the agent Q-table will be saved | None | str | -save models/my_model.txt |
| -load | Loading path of a Q-table | None | str | -load models/my_model.txt |
| -dontlearn | Disable learning & randomness of the agent during the training | Off | bool | -dontlearn |
| -visual | Show visual display (may slow the training) | Off | bool | -visual off |
| -terminal | Show vision of the agent (may slow the training) | Off | bool | -terminal off |
| -step-by-step | Able step-by-step movement instead of a full continue movement | None | bool | -step-by-step |
| -fps | Change speed of the agent (lower is the value, more he will take his time) | 8 | int | -fps=8 |
| -max-steps | Total step he can do before a game over (for infinite looping behaviour) | 2000 | int | -max-steps=2000 |
| -board-size | Size of the board | 10 | int | -board-size=10 |

For example here a prompt that will create 100 sessions with the Q-table in my_model.txt, where he don't learn, with the display at 120 fps.
The max steps is at 2000, the terminal is off, etc
```bash
  ./agent.py -sessions=100 -load models/my_model.txt -dontlearn -visual on -fps=120
```

### Graphic
To use the graphic interface you only need to execute Learn2Slither program.
(Disclaimer: All the texture in this project except the Red apple are drawn by me. You are free to use them in your project too if you want too)

```bash
  ./Learn2Slither
```

You will have a nice display menu where you can find the same flags as in the terminal options.
Moreover, at the end of the training session, you will have an end menu with various stats like average apples eaten, length, duration, etc.

<p align="center">
  <img width="48%" alt="menu" src="https://github.com/user-attachments/assets/c001f061-352b-41db-8ad5-38ad442a22cf" />
  <img width="48%" alt="end_menu" src="https://github.com/user-attachments/assets/51e982b8-9f99-47a2-bc06-2d296f8539a8" />
</p>

## Agent

<p align="center">
  <img width="90%" alt="test_snake" src="https://github.com/user-attachments/assets/9f867ac2-0d65-4a2e-b5f8-ee8c6fc738e9" />
</p>

The Agent uses a Q-table to choose his actions.

Before a showcase, we need to train our agent by making random decisions to explore the board he is on. This is called greedy exploration reinforcement learning.
He will make a lot of bad decisions to prevent making them later.

At the start of a training session, he will load a Q-table (blank or a real Q-table with the load flag), and every time he steps into a new cell, he will write a value to see if it is a good choice or not. He will analyze what is on the right, left, top, and bottom of his head and come up with combinations. For example, if there is a wall on top and a green apple on the left. The left position will have a huge score, the top a really bad score, and the other positions a neutral bad score.

The agent needs a lot of training to become relevant and do real things by himself. By turning off his learning, he will only choose the best tile to move to and will not perform random actions anymore, preventing him from killing himself by accident.

## Agent Usage

You can change Agent speed mid training, pause the agent.

If you activate step-by-step option you will have a button to change the state of the agent step-by-step. (You can also click on whatever key you want to change his step-by-step state)

The Agent Panel will display:
- Current session he is in out of the max session
- Max length he achieve during the training
- Average length on the training
- Green apple he eat during the session he is in
- Red apple he eat during the session he is in

<p align="center">
  <img width="48%" alt="test_buttons" src="https://github.com/user-attachments/assets/8120dd83-24c1-4aac-9c95-ac3c0838666b" />
  <img width="48%" alt="stepbystep" src="https://github.com/user-attachments/assets/6d25db3e-9f80-4914-bd4d-b4e1d195cb59" />
</p>

## Sources
- Create a q-table & use it https://youtu.be/MSrfaI1gGjI
