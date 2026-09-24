#!/usr/bin/env -S uv run --script
import sys
import os
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import pygame

from agent import Agent, train


class Menu:
    def __init__(self):
        pygame.init()
        self.width = self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Learn2Slither : Menu")
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 54)

        self.options = [
            {"name": "save path", "type": "str", "val": "models/my_model.txt", "edit": False},
            {"name": "load path", "type": "str", "val": "", "edit": False},
            {"name": "sessions", "type": "int", "val": 20, "edit": False},
            {"name": "max steps", "type": "int", "val": 2000, "edit": False},
            {"name": "learning", "type": "bool", "val": True, "edit": False},
            {"name": "terminal", "type": "bool", "val": False, "edit": False},
            {"name": "display", "type": "bool", "val": True, "edit": False},
            {"name": "fps", "type": "int", "val": 8, "edit": False},
            {"name": "LAUNCH", "type": "action", "val": None, "edit": False}
        ]
        self.selected_index = 0

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while (running):
            self.screen.fill((30, 30, 30))

            title_surf = self.title_font.render("Learn2Slither", True, (255, 255, 255))
            self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 50))

            left_col_x = 100
            right_col_x = 450
            start_y = 180
            y_spacing = 45

            for i, opt in enumerate(self.options):
                col = 0 if i < 4 or i == 8 else 1
                row = i if col == 0 else i -4

                if (i == 8):
                    x = self.width // 2 -100
                    y = 480
                else:
                    x = left_col_x if col == 0 else right_col_x
                    y = start_y + (row * y_spacing)

                color = (0, 255, 0) if i == self.selected_index else (200, 200, 200)
                if (opt["edit"]):
                    color = (255, 255, 0)

                if (opt["type"] == "bool"):
                    val_str = "On" if opt["val"] else "Off"
                    text = f"{opt['name']}: {val_str}"
                elif (opt["type"] == "action"):
                    text = f"-- {opt['name']} --"
                else:
                    val_str = str(opt["val"]) if opt["val"] != "" else "<none>"
                    text = f"{opt['name']}: {val_str}"

                surf = self.font.render(text, True, color)
                self.screen.blit(surf, (x, y))

            pygame.display.flip()

            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    pygame.quit()
                    sys.exit()
                elif (event.type == pygame.KEYDOWN):
                    active_opt = self.options[self.selected_index]

                    if (active_opt["edit"]):
                        if (event.key == pygame.K_RETURN):
                            active_opt["edit"] = False
                        elif (event.key == pygame.K_BACKSPACE):
                            active_opt["val"] = active_opt["val"][:-1]
                        else:
                            active_opt["val"] += event.unicode
                    else:
                        if (event.key == pygame.K_UP):
                            self.selected_index = (self.selected_index - 1) % len(self.options)
                        elif (event.key == pygame.K_DOWN):
                            self.selected_index = (self.selected_index + 1) % len(self.options)
                        elif (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT):
                            if (active_opt["type"] == "bool"):
                                active_opt["val"] = not active_opt["val"]
                            elif (active_opt["type"] == "int"):
                                delta = 1 if event.key == pygame.K_RIGHT else -1
                                if ("sessions" in active_opt["name"]):
                                    active_opt["val"] = max(1, active_opt["val"] + delta * 5)
                                else:
                                    active_opt["val"] = max(1, active_opt["val"] + delta)
                        elif (event.key == pygame.K_RETURN):
                            if (active_opt["type"] == "bool"):
                                active_opt["val"] = not active_opt["val"]
                            elif (active_opt["type"] == "str"):
                                active_opt["edit"] = True
                            elif (active_opt["name"] == "LAUNCH" or self.selected_index == len(self.options) - 1):
                                self.execute_launch()

            clock.tick(30)

    def execute_launch(self):
        config = {opt["name"]: opt["val"] for opt in self.options if opt["type"] != "action"}

        pygame.quit()

        load_path = config["load path"] if config["load path"] != "" else None
        save_path = config["save path"] if config["save path"] != "" else None
        
        if (load_path):
            agent = Agent.load(load_path)
            print(f"Load trained model from {load_path}")
        else:
            agent = Agent()

        train(
            sessions=int(config["sessions"]),
            agent=agent,
            save_path=save_path,
            learn=config["learning"],
            visual=config["display"],
            terminal_output=config["terminal"],
            fps=int(config["fps"]),
            max_steps=int(config["max steps"]),
        )

        sys.exit(main())


def main():
    menu = Menu()
    menu.run()
    return (0)


if __name__ == "__main__":
    sys.exit(main())
