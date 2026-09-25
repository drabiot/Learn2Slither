#!/usr/bin/env -S uv run --script
import sys
import os
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import pygame
import math
import tkinter as tk
from tkinter import filedialog

from agent import Agent, train


class Menu:
    def __init__(self):
        pygame.init()
        self.width = self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Learn2Slither : Menu")
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 54)

        try:
            self.bg_image = pygame.image.load("texture/menu_background.png").convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (self.width, self.height))

            self.title_image = pygame.image.load("texture/menu_title.png").convert_alpha()
            self.launch_bar_image = pygame.image.load("texture/menu_launch_bar.png").convert_alpha()
            self.launch_bar_hover_image = pygame.image.load("texture/menu_launch_bar_hover.png").convert_alpha()
            
            self.on_switch_image = pygame.image.load("texture/menu_on_switch.png").convert_alpha()
            self.off_switch_image = pygame.image.load("texture/menu_off_switch.png").convert_alpha()
            self.on_switch_hover_image = pygame.image.load("texture/menu_on_switch_hover.png").convert_alpha()
            self.off_switch_hover_image = pygame.image.load("texture/menu_off_switch_hover.png").convert_alpha()

            self.learning_label_img = pygame.image.load("texture/learning.png").convert_alpha()
            self.terminal_label_img = pygame.image.load("texture/terminal.png").convert_alpha()
            self.display_label_img = pygame.image.load("texture/display.png").convert_alpha()

            self.menu_int_image = pygame.image.load("texture/menu_int.png").convert_alpha()
            self.menu_int_hover_image = pygame.image.load("texture/menu_int_hover.png").convert_alpha()

            self.sessions_label_img = pygame.image.load("texture/sessions.png").convert_alpha()
            self.max_steps_label_img = pygame.image.load("texture/max_steps.png").convert_alpha()
            self.board_size_label_img = pygame.image.load("texture/board_size.png").convert_alpha()
            self.fps_label_img = pygame.image.load("texture/fps.png").convert_alpha()

            self.menu_path_image = pygame.image.load("texture/menu_path.png").convert_alpha()
            self.menu_path_hover_image = pygame.image.load("texture/menu_path_hover.png").convert_alpha()

            self.save_path_label_img = pygame.image.load("texture/save_path.png").convert_alpha()
            self.load_path_label_img = pygame.image.load("texture/load_path.png").convert_alpha()
        except FileNotFoundError:
            self.bg_image = None
            self.launch_bar_image = None
            self.launch_bar_hover_image = None
            self.on_switch_image = None
            self.off_switch_image = None
            self.on_switch_hover_image = None
            self.off_switch_hover_image = None
            self.learning_label_img = None
            self.terminal_label_img = None
            self.display_label_img = None

            self.menu_int_image = None
            self.menu_int_hover_image = None
            self.sessions_label_img = None
            self.max_steps_label_img = None
            self.board_size_label_img = None
            self.fps_label_img = None

            self.menu_path_image = None
            self.menu_path_hover_image = None
            self.save_path_label_img = None
            self.load_path_label_img = None

        try:
            self.pixel_font = pygame.font.Font("texture/pixel_font.ttf", 30)
        except FileNotFoundError:
            self.pixel_font = pygame.font.Font(None, 30)

        self.options = [
            {"name": "save path", "type": "str", "val": "models/my_model.txt", "edit": False},
            {"name": "load path", "type": "str", "val": "", "edit": False},
            {"name": "learning", "type": "bool", "val": True, "edit": False},
            {"name": "terminal", "type": "bool", "val": False, "edit": False},
            {"name": "display", "type": "bool", "val": True, "edit": False},
            {"name": "sessions", "type": "int", "val": 20, "edit": False},
            {"name": "max steps", "type": "int", "val": 2000, "edit": False},
            {"name": "board size", "type": "int", "val": 10, "edit": False},
            {"name": "fps", "type": "int", "val": 8, "edit": False},
            {"name": "LAUNCH", "type": "action", "val": None, "edit": False}
        ]
        self.selected_index = None 

    def run(self):
        clock = pygame.time.Clock()
        running = True
        start_time = pygame.time.get_ticks()

        while (running):
            if (hasattr(self, "bg_image") and self.bg_image):
                self.screen.blit(self.bg_image, (0, 0))
            else:
                self.screen.fill((30, 30, 30))

            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
            if (hasattr(self, "title_image") and self.title_image):
                base_scale = 5.0 
                offset_y = math.sin(elapsed_time * 3) * 4
                pulse_scale = base_scale + (math.sin(elapsed_time * 4) * 0.1)
                
                base_w, base_h = self.title_image.get_size()
                scaled_title = pygame.transform.scale(
                    self.title_image, 
                    (int(base_w * pulse_scale), int(base_h * pulse_scale))
                )
                title_rect = scaled_title.get_rect(center=(self.width // 2, 300 + int(offset_y)))
                self.screen.blit(scaled_title, title_rect)
            else:
                title_surf = self.title_font.render("Learn2Slither", True, (255, 255, 255))
                self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 50))

            left_col_x = 135
            right_col_x = 548
            start_y = 150
            y_spacing = 85

            option_rects = []

            for i, opt in enumerate(self.options):
                is_launch = (opt["name"] == "LAUNCH")

                if (is_launch):
                    x = self.width // 2
                    y = 635
                    
                    is_hovered = (i == self.selected_index)
                    active_image = self.launch_bar_hover_image if (is_hovered and self.launch_bar_hover_image) else self.launch_bar_image

                    if (active_image):
                        base_launch_scale = 6.6
                        bw, bh = active_image.get_size()
                        
                        scaled_launch = pygame.transform.scale(
                            active_image, 
                            (int(bw * base_launch_scale), int(bh * base_launch_scale))
                        )
                        rect = scaled_launch.get_rect(center=(x, y))
                        self.screen.blit(scaled_launch, rect)
                    else:
                        rect = pygame.Rect(0, 0, 200, 40)
                        rect.center = (x, y)
                        color = (0, 255, 0) if is_hovered else (200, 200, 200)
                        surf = self.font.render("-- LAUNCH --", True, color)
                        self.screen.blit(surf, rect)
                else:
                    if i < 5:
                        col = 0
                        row = i
                    else:
                        col = 1
                        row = i - 4

                    x = left_col_x if col == 0 else right_col_x
                    y = start_y + (row * y_spacing)

                    color = (0, 255, 0) if i == self.selected_index else (200, 200, 200)
                    if (opt["edit"]):
                        color = (255, 255, 0)

                    if (opt["type"] == "bool"):
                        label_img = None
                        if (opt["name"] == "learning"):
                            label_img = self.learning_label_img
                        elif (opt["name"] == "terminal"):
                            label_img = self.terminal_label_img
                        elif (opt["name"] == "display"):
                            label_img = self.display_label_img

                        is_hovered = (i == self.selected_index)

                        if (is_hovered):
                            switch_img = self.on_switch_hover_image if opt["val"] else self.off_switch_hover_image
                            if (not switch_img):
                                switch_img = self.on_switch_image if opt["val"] else self.off_switch_image
                        else:
                            switch_img = self.on_switch_image if opt["val"] else self.off_switch_image

                        if (label_img and switch_img):
                            label_scale = 2.5
                            snake_scale = 4.0

                            lw, lh = label_img.get_size()
                            scaled_label = pygame.transform.scale(label_img, (int(lw * label_scale), int(lh * label_scale)))
                            label_rect = scaled_label.get_rect(topleft=(x, y))
                            self.screen.blit(scaled_label, label_rect)

                            sw, sh = switch_img.get_size()
                            scaled_switch = pygame.transform.scale(switch_img, (int(sw * snake_scale), int(sh * snake_scale)))
                            
                            switch_rect = scaled_switch.get_rect(topleft=(x, label_rect.bottom + 5))
                            self.screen.blit(scaled_switch, switch_rect)

                            total_width = max(label_rect.width, switch_rect.width)
                            total_height = label_rect.height + 5 + switch_rect.height
                            rect = pygame.Rect(x, y, total_width, total_height)
                        else:
                            val_str = "On" if opt["val"] else "Off"
                            surf = self.font.render(f"{opt['name']}: {val_str}", True, color)
                            rect = surf.get_rect(topleft=(x, y))
                            self.screen.blit(surf, rect)
                    elif (opt["type"] == "int"):
                        label_img = None
                        if (opt["name"] == "sessions"):
                            label_img = self.sessions_label_img
                        elif (opt["name"] == "max steps"):
                            label_img = self.max_steps_label_img
                        elif (opt["name"] == "board size"):
                            label_img = self.board_size_label_img
                        elif (opt["name"] == "fps"):
                            label_img = self.fps_label_img

                        is_hovered = (i == self.selected_index)
                        switch_img = self.menu_int_hover_image if (is_hovered and self.menu_int_hover_image) else self.menu_int_image

                        if (label_img and switch_img):
                            label_scale = 2.5
                            snake_scale = 4.0

                            lw, lh = label_img.get_size()
                            scaled_label = pygame.transform.scale(label_img, (int(lw * label_scale), int(lh * label_scale)))
                            label_rect = scaled_label.get_rect(topleft=(x, y))
                            self.screen.blit(scaled_label, label_rect)

                            sw, sh = switch_img.get_size()
                            scaled_switch = pygame.transform.scale(switch_img, (int(sw * snake_scale), int(sh * snake_scale)))

                            switch_rect = scaled_switch.get_rect(topleft=(x, label_rect.bottom + 5))
                            self.screen.blit(scaled_switch, switch_rect)

                            val_str = str(opt["val"])
                            outline_color = (0, 0, 0)
                            text_color = (255, 255, 255)

                            val_center = (switch_rect.centerx - 15, switch_rect.centery)

                            outline_surf = self.pixel_font.render(val_str, True, outline_color)
                            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, -2), (-2, 2), (2, 2)]:
                                outline_rect = outline_surf.get_rect(center=(val_center[0] + dx, val_center[1] + dy))
                                self.screen.blit(outline_surf, outline_rect)

                            val_surf = self.pixel_font.render(val_str, True, text_color)
                            val_rect = val_surf.get_rect(center=val_center)
                            self.screen.blit(val_surf, val_rect)

                            total_width = max(label_rect.width, switch_rect.width)
                            total_height = label_rect.height + 5 + switch_rect.height
                            rect = pygame.Rect(x, y, total_width, total_height)
                        else:
                            val_str = str(opt["val"])
                            text = f"{opt['name']}: {val_str}"
                            surf = self.font.render(text, True, color)
                            rect = surf.get_rect(topleft=(x, y))
                            self.screen.blit(surf, rect)
                    else:
                        label_img = None
                        if (opt["name"] == "save path"):
                            label_img = self.save_path_label_img
                        elif (opt["name"] == "load path"):
                            label_img = self.load_path_label_img

                        is_hovered = (i == self.selected_index)
                        switch_img = self.menu_path_hover_image if (is_hovered and self.menu_path_hover_image) else self.menu_path_image

                        if (label_img and switch_img):
                            label_scale = 2.5
                            snake_scale = 4.0

                            lw, lh = label_img.get_size()
                            scaled_label = pygame.transform.scale(label_img, (int(lw * label_scale), int(lh * label_scale)))
                            label_rect = scaled_label.get_rect(topleft=(x, y))
                            self.screen.blit(scaled_label, label_rect)

                            sw, sh = switch_img.get_size()
                            scaled_switch = pygame.transform.scale(switch_img, (int(sw * snake_scale), int(sh * snake_scale)))

                            switch_rect = scaled_switch.get_rect(topleft=(x, label_rect.bottom + 5))
                            self.screen.blit(scaled_switch, switch_rect)

                            display_str = os.path.basename(opt["val"]) if opt["val"] else "<none>"
                            outline_color = (0, 0, 0)
                            text_color = (255, 255, 255)

                            val_center = (switch_rect.centerx - 15, switch_rect.centery)

                            outline_surf = self.pixel_font.render(display_str, True, outline_color)
                            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, -2), (-2, 2), (2, 2)]:
                                outline_rect = outline_surf.get_rect(center=(val_center[0] + dx, val_center[1] + dy))
                                self.screen.blit(outline_surf, outline_rect)

                            val_surf = self.pixel_font.render(display_str, True, text_color)
                            val_rect = val_surf.get_rect(center=val_center)
                            self.screen.blit(val_surf, val_rect)

                            total_width = max(label_rect.width, switch_rect.width)
                            total_height = label_rect.height + 5 + switch_rect.height
                            rect = pygame.Rect(x, y, total_width, total_height)
                        else:
                            val_str = os.path.basename(opt["val"]) if opt["val"] != "" else "<none>"
                            text = f"{opt['name']}: {val_str}"
                            surf = self.font.render(text, True, color)
                            rect = surf.get_rect(topleft=(x, y))
                            self.screen.blit(surf, rect)

                option_rects.append((i, rect))

            pygame.display.flip()

            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    pygame.quit()
                    sys.exit()

                elif (event.type == pygame.MOUSEMOTION):
                    mouse_pos = pygame.mouse.get_pos()
                    hovered_any = False
                    for idx, rect in option_rects:
                        if (rect.collidepoint(mouse_pos)):
                            self.selected_index = idx
                            hovered_any = True
                    if (not hovered_any):
                        self.selected_index = None

                elif (event.type == pygame.MOUSEBUTTONDOWN):
                    if (event.button == 1):
                        mouse_pos = pygame.mouse.get_pos()
                        clicked_any = False
                        for idx, rect in option_rects:
                            if (rect.collidepoint(mouse_pos)):
                                clicked_any = True
                                self.selected_index = idx
                                active_opt = self.options[idx]
                                if (active_opt["type"] == "bool"):
                                    active_opt["val"] = not active_opt["val"]
                                elif (active_opt["type"] == "str"):
                                    self.open_file_dialog(active_opt)
                                elif (active_opt["name"] == "LAUNCH"):
                                    self.execute_launch()
                        if not clicked_any:
                            self.selected_index = None

                    elif event.button in (4, 5):
                        if self.selected_index is not None:
                            active_opt = self.options[self.selected_index]
                            if active_opt["type"] == "int":
                                delta = 1 if event.button == 4 else -1
                                if "sessions" in active_opt["name"]:
                                    active_opt["val"] = max(1, active_opt["val"] + delta * 5)
                                elif "board size" in active_opt["name"]:
                                    active_opt["val"] = max(3, active_opt["val"] + delta)
                                else:
                                    active_opt["val"] = max(1, active_opt["val"] + delta)

                elif (event.type == pygame.KEYDOWN):
                    if (self.selected_index is None):
                        self.selected_index = 0
                        continue

                    active_opt = self.options[self.selected_index]

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
                            elif "board size" in active_opt["name"]:
                                active_opt["val"] = max(5, active_opt["val"] + delta)
                            else:
                                active_opt["val"] = max(1, active_opt["val"] + delta)
                    elif (event.key == pygame.K_RETURN):
                        if (active_opt["type"] == "bool"):
                            active_opt["val"] = not active_opt["val"]
                        elif (active_opt["type"] == "str"):
                            self.open_file_dialog(active_opt)
                        elif (active_opt["name"] == "LAUNCH"):
                            self.execute_launch()

            clock.tick(30)

    def open_file_dialog(self, opt):
        models_dir = os.path.join(os.getcwd(), "models")
        os.makedirs(models_dir, exist_ok=True)

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        try:
            if (opt["name"] == "save path"):
                path = filedialog.asksaveasfilename(
                    initialdir=models_dir,
                    title="Choisir où exporter le modèle",
                    defaultextension=".txt",
                    filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
                )
            else:
                path = filedialog.askopenfilename(
                    initialdir=models_dir,
                    title="Choisir un modèle à importer",
                    filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
                )
        finally:
            root.destroy()

        if (path):
            opt["val"] = path

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
            board_size=int(config["board size"]),
        )

        sys.exit(main())


def main():
    menu = Menu()
    menu.run()
    return (0)


if __name__ == "__main__":
    sys.exit(main())
