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
To use the graphic interface you only need to execute Learn2Slither program

```bash
  ./Learn2Slither
```

You will have a nice display menu where you can find the same flag as the terminal option one.

<div align="center">
	<img width="795" height="796" alt="menu" src="https://github.com/user-attachments/assets/c001f061-352b-41db-8ad5-38ad442a22cf" />
</div>

Moreover, you will have at the end of the training session an end menu with various stats like apple eaten in average, length, duration, etc

<div align="center">
	<img width="794" height="796" alt="end_menu" src="https://github.com/user-attachments/assets/72889c45-0ff2-4acd-b825-3863eceb4fb6" />
</div>

## Sources
- Create a q-table & use it https://youtu.be/MSrfaI1gGjI
