#!/usr/bin/env -S uv run --script
import sys
import os
from agent import Agent, train
import math
import pygame
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')


class Menu:
    def __init__(self):
        pygame.init()
        self.width = self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Learn2Slither : Menu")
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 54)

        try:
            self.bg_image = pygame.image.load(
                "texture/menu_background.png").convert()
            self.bg_image = pygame.transform.scale(
                self.bg_image, (self.width, self.height))

            self.title_image = pygame.image.load(
                "texture/menu_title.png").convert_alpha()
            self.launch_bar_image = pygame.image.load(
                "texture/menu_launch_bar.png").convert_alpha()
            self.launch_bar_hover_image = pygame.image.load(
                "texture/menu_launch_bar_hover.png").convert_alpha()

            self.on_switch_image = pygame.image.load(
                "texture/menu_on_switch.png").convert_alpha()
            self.off_switch_image = pygame.image.load(
                "texture/menu_off_switch.png").convert_alpha()
            self.on_switch_hover_image = pygame.image.load(
                "texture/menu_on_switch_hover.png").convert_alpha()
            self.off_switch_hover_image = pygame.image.load(
                "texture/menu_off_switch_hover.png").convert_alpha()

            self.learning_label_img = pygame.image.load(
                "texture/learning.png").convert_alpha()
            self.terminal_label_img = pygame.image.load(
                "texture/terminal.png").convert_alpha()
            self.display_label_img = pygame.image.load(
                "texture/display.png").convert_alpha()

            self.menu_int_image = pygame.image.load(
                "texture/menu_int.png").convert_alpha()
            self.menu_int_hover_image = pygame.image.load(
                "texture/menu_int_hover.png").convert_alpha()

            self.sessions_label_img = pygame.image.load(
                "texture/sessions.png").convert_alpha()
            self.max_steps_label_img = pygame.image.load(
                "texture/max_steps.png").convert_alpha()
            self.board_size_label_img = pygame.image.load(
                "texture/board_size.png").convert_alpha()
            self.fps_label_img = pygame.image.load(
                "texture/fps.png").convert_alpha()

            self.menu_path_image = pygame.image.load(
                "texture/menu_path.png").convert_alpha()
            self.menu_path_hover_image = pygame.image.load(
                "texture/menu_path_hover.png").convert_alpha()

            self.save_path_label_img = pygame.image.load(
                "texture/save_path.png").convert_alpha()
            self.load_path_label_img = pygame.image.load(
                "texture/load_path.png").convert_alpha()

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
            {"name": "save path", "type": "str", "val": "models/my_model.txt",
             "edit": False},
            {"name": "load path", "type": "str", "val": "",
             "edit": False},
            {"name": "learning", "type": "bool", "val": True,
             "edit": False},
            {"name": "terminal", "type": "bool", "val": False,
             "edit": False},
            {"name": "display", "type": "bool", "val": True,
             "edit": False},
            {"name": "sessions", "type": "int", "val": 20,
             "edit": False, "edit_buffer": ""},
            {"name": "max steps", "type": "int", "val": 2000,
             "edit": False, "edit_buffer": ""},
            {"name": "board size", "type": "int", "val": 10,
             "edit": False, "edit_buffer": ""},
            {"name": "fps", "type": "int", "val": 8,
             "edit": False, "edit_buffer": ""},
            {"name": "LAUNCH", "type": "action", "val": None,
             "edit": False}
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
                title_rect = scaled_title.get_rect(center=(
                    self.width // 2, 300 + int(offset_y)))
                self.screen.blit(scaled_title, title_rect)
            else:
                title_surf = self.title_font.render(
                    "Learn2Slither", True, (255, 255, 255))
                self.screen.blit(title_surf, (
                    self.width // 2 - title_surf.get_width() // 2, 50))

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
                    active_image = self.launch_bar_hover_image if (
                        is_hovered and self.launch_bar_hover_image) else (
                            self.launch_bar_image)

                    if (active_image):
                        base_launch_scale = 6.6
                        bw, bh = active_image.get_size()

                        scaled_launch = pygame.transform.scale(
                            active_image,
                            (int(bw * base_launch_scale), int(
                                bh * base_launch_scale))
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
                    if (i < 5):
                        col = 0
                        row = i
                    else:
                        col = 1
                        row = i - 4

                    x = left_col_x if col == 0 else right_col_x
                    y = start_y + (row * y_spacing)

                    color = ((0, 255, 0)
                             if i == self.selected_index
                             else (200, 200, 200))
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
                            switch_img = (self.on_switch_hover_image
                                          if opt["val"]
                                          else self.off_switch_hover_image)
                            if (not switch_img):
                                switch_img = (self.on_switch_image
                                              if opt["val"]
                                              else self.off_switch_image)
                        else:
                            switch_img = (self.on_switch_image
                                          if opt["val"]
                                          else self.off_switch_image)

                        if (label_img and switch_img):
                            label_scale = 2.5
                            snake_scale = 4.0

                            lw, lh = label_img.get_size()
                            scaled_label = pygame.transform.scale(
                                label_img, (int(lw * label_scale),
                                            int(lh * label_scale)))
                            label_rect = scaled_label.get_rect(topleft=(x, y))
                            self.screen.blit(scaled_label, label_rect)

                            sw, sh = switch_img.get_size()
                            scaled_switch = pygame.transform.scale(
                                switch_img, (int(sw * snake_scale),
                                             int(sh * snake_scale)))

                            switch_rect = scaled_switch.get_rect(
                                topleft=(x, label_rect.bottom + 5))
                            self.screen.blit(scaled_switch, switch_rect)

                            total_width = max(label_rect.width,
                                              switch_rect.width)
                            total_height = (label_rect.height
                                            + 5 + switch_rect.height)
                            rect = pygame.Rect(x, y, total_width, total_height)
                        else:
                            val_str = "On" if opt["val"] else "Off"
                            surf = (self.font.render(
                                f"{opt['name']}: {val_str}", True, color))
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
                        switch_img = (self.menu_int_hover_image
                                      if (is_hovered and
                                          self.menu_int_hover_image)
                                      else self.menu_int_image)

                        if (label_img and switch_img):
                            label_scale = 2.5
                            snake_scale = 4.0

                            lw, lh = label_img.get_size()
                            scaled_label = pygame.transform.scale(
                                label_img, (int(lw * label_scale),
                                            int(lh * label_scale)))
                            label_rect = scaled_label.get_rect(topleft=(x, y))
                            self.screen.blit(scaled_label, label_rect)

                            sw, sh = switch_img.get_size()
                            scaled_switch = pygame.transform.scale(
                                switch_img, (int(sw * snake_scale),
                                             int(sh * snake_scale)))

                            switch_rect = scaled_switch.get_rect(
                                topleft=(x, label_rect.bottom + 5))
                            self.screen.blit(scaled_switch, switch_rect)

                            val_str = (opt["edit_buffer"]
                                       if opt["edit"]
                                       else str(opt["val"]))
                            outline_color = (0, 0, 0)
                            text_color = ((255, 255, 0)
                                          if opt["edit"]
                                          else (255, 255, 255))

                            val_center = (switch_rect.centerx -
                                          15, switch_rect.centery)

                            outline_surf = self.pixel_font.render(
                                val_str, True, outline_color)
                            for dx, dy in [(-2, 0), (2, 0), (0, -2),
                                           (0, 2), (-2, -2), (2, -2),
                                           (-2, 2), (2, 2)]:
                                outline_rect = outline_surf.get_rect(
                                    center=(val_center[0] + dx,
                                            val_center[1] + dy))
                                self.screen.blit(outline_surf, outline_rect)

                            val_surf = self.pixel_font.render(
                                val_str, True, text_color)
                            val_rect = val_surf.get_rect(center=val_center)
                            self.screen.blit(val_surf, val_rect)

                            total_width = max(label_rect.width,
                                              switch_rect.width)
                            total_height = (label_rect.height
                                            + 5 + switch_rect.height)
                            rect = pygame.Rect(x, y, total_width, total_height)
                        else:
                            val_str = (opt["edit_buffer"]
                                       if opt["edit"]
                                       else str(opt["val"]))
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
                        switch_img = (self.menu_path_hover_image
                                      if (is_hovered and
                                          self.menu_path_hover_image)
                                      else self.menu_path_image)

                        if (label_img and switch_img):
                            label_scale = 2.5
                            snake_scale = 4.0

                            lw, lh = label_img.get_size()
                            scaled_label = pygame.transform.scale(
                                label_img, (int(lw * label_scale),
                                            int(lh * label_scale)))
                            label_rect = scaled_label.get_rect(topleft=(x, y))
                            self.screen.blit(scaled_label, label_rect)

                            sw, sh = switch_img.get_size()
                            scaled_switch = pygame.transform.scale(
                                switch_img, (int(sw * snake_scale),
                                             int(sh * snake_scale)))

                            switch_rect = scaled_switch.get_rect(
                                topleft=(x, label_rect.bottom + 5))
                            self.screen.blit(scaled_switch, switch_rect)

                            display_str = (os.path.basename(opt["val"])
                                           if opt["val"] else "<none>")
                            if (len(display_str) > 15):
                                display_str = display_str[:23] + "..."
                            outline_color = (0, 0, 0)
                            text_color = (255, 255, 255)

                            val_center = (switch_rect.centerx -
                                          15, switch_rect.centery)

                            outline_surf = (self.pixel_font.render(
                                display_str, True, outline_color))
                            for dx, dy in [(-2, 0), (2, 0), (0, -2),
                                           (0, 2), (-2, -2), (2, -2),
                                           (-2, 2), (2, 2)]:
                                outline_rect = (outline_surf.get_rect(
                                    center=(val_center[0] + dx,
                                            val_center[1] + dy)))
                                self.screen.blit(outline_surf, outline_rect)

                            val_surf = self.pixel_font.render(display_str,
                                                              True, text_color)
                            val_rect = val_surf.get_rect(center=val_center)
                            self.screen.blit(val_surf, val_rect)

                            total_width = max(label_rect.width,
                                              switch_rect.width)
                            total_height = (label_rect.height +
                                            5 + switch_rect.height)
                            rect = pygame.Rect(x, y, total_width, total_height)
                        else:
                            val_str = (os.path.basename(opt["val"])
                                       if opt["val"] != "" else "<none>")
                            if (len(val_str) > 15):
                                val_str = val_str[:23] + "..."
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
                    hovered_idx = None
                    for idx, rect in option_rects:
                        if (rect.collidepoint(mouse_pos)):
                            hovered_idx = idx
                            hovered_any = True

                    for idx, o in enumerate(self.options):
                        if (o["type"] == "int" and o["edit"]
                           and idx != hovered_idx):
                            self.commit_int_edit(o)

                    self.selected_index = hovered_idx if hovered_any else None

                elif (event.type == pygame.MOUSEBUTTONDOWN):
                    if (event.button == 1):
                        mouse_pos = pygame.mouse.get_pos()
                        clicked_any = False
                        for o in self.options:
                            if (o["type"] == "int" and o["edit"]):
                                self.commit_int_edit(o)
                        for idx, rect in option_rects:
                            if (rect.collidepoint(mouse_pos)):
                                clicked_any = True
                                self.selected_index = idx
                                active_opt = self.options[idx]
                                if (active_opt["type"] == "bool"):
                                    active_opt["val"] = not active_opt["val"]
                                elif (active_opt["type"] == "int"):
                                    active_opt["edit"] = True
                                    active_opt["edit_buffer"] = (
                                        str(active_opt["val"]))
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
                                    active_opt["val"] = min(
                                        999999, max(1, active_opt["val"]
                                                    + delta))
                                elif "board size" in active_opt["name"]:
                                    active_opt["val"] = min(
                                        999999, max(3, active_opt["val"]
                                                    + delta))
                                else:
                                    active_opt["val"] = min(
                                        999999, max(1, active_opt["val"]
                                                    + delta))

                elif (event.type == pygame.KEYDOWN):
                    if (self.selected_index is None):
                        self.selected_index = 0
                        continue

                    active_opt = self.options[self.selected_index]

                    if (active_opt["type"] == "int" and active_opt["edit"]):
                        if (event.key == pygame.K_RETURN):
                            self.commit_int_edit(active_opt)
                        elif (event.key == pygame.K_ESCAPE):
                            active_opt["edit"] = False
                        elif (event.key == pygame.K_BACKSPACE):
                            active_opt["edit_buffer"] = (
                                active_opt["edit_buffer"][:-1])
                        elif (event.unicode.isdigit()):
                            new_buffer = (active_opt["edit_buffer"]
                                          + event.unicode)
                            if (int(new_buffer) <= 999999):
                                active_opt["edit_buffer"] = new_buffer
                        continue

                    if (event.key == pygame.K_UP):
                        self.selected_index = ((self.selected_index - 1)
                                               % len(self.options))
                    elif (event.key == pygame.K_DOWN):
                        self.selected_index = ((self.selected_index + 1)
                                               % len(self.options))
                    elif (event.key == pygame.K_LEFT
                          or event.key == pygame.K_RIGHT):
                        if (active_opt["type"] == "bool"):
                            active_opt["val"] = not active_opt["val"]
                        elif (active_opt["type"] == "int"):
                            delta = 1 if event.key == pygame.K_RIGHT else -1
                            if ("sessions" in active_opt["name"]):
                                active_opt["val"] = min(999999,
                                                        max(1,
                                                            active_opt["val"]
                                                            + delta))
                            elif "board size" in active_opt["name"]:
                                active_opt["val"] = min(999999,
                                                        max(5,
                                                            active_opt["val"]
                                                            + delta))
                            else:
                                active_opt["val"] = min(999999,
                                                        max(1,
                                                            active_opt["val"]
                                                            + delta))
                    elif (event.key == pygame.K_RETURN):
                        if (active_opt["type"] == "bool"):
                            active_opt["val"] = not active_opt["val"]
                        elif (active_opt["type"] == "int"):
                            active_opt["edit"] = True
                            active_opt["edit_buffer"] = str(active_opt["val"])
                        elif (active_opt["type"] == "str"):
                            self.open_file_dialog(active_opt)
                        elif (active_opt["name"] == "LAUNCH"):
                            self.execute_launch()

            clock.tick(30)

    def commit_int_edit(self, opt):
        buffer = opt["edit_buffer"]
        if (buffer != ""):
            new_val = int(buffer)
            new_val = min(999999, new_val)
            if ("sessions" in opt["name"]):
                new_val = max(1, new_val)
            elif "board size" in opt["name"]:
                new_val = max(3, new_val)
            else:
                new_val = max(1, new_val)
            opt["val"] = new_val
        opt["edit"] = False

    def open_file_dialog(self, opt):
        models_dir = os.path.join(os.getcwd(), "models")
        os.makedirs(models_dir, exist_ok=True)

        is_save = (opt["name"] == "save path")
        clock = pygame.time.Clock()
        selecting = True
        input_text = (os.path.basename(opt["val"])
                      if opt["val"] else "my_model.txt")

        scroll_offset = 0
        max_visible_files = 10
        dragging_scrollbar = False

        sb_x = 575
        sb_y = 100
        sb_w = 12
        sb_h = max_visible_files * 40 - 5

        def draw_outlined_text(text, pos, font_obj,
                               text_color=(255, 255, 255), align="topleft"):
            outline_color = (0, 0, 0)
            outline_surf = font_obj.render(text, True, outline_color)
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2),
                           (-2, -2), (2, -2), (-2, 2), (2, 2)]:
                if align == "center":
                    orect = outline_surf.get_rect(center=(
                        pos[0] + dx, pos[1] + dy))
                else:
                    orect = outline_surf.get_rect(topleft=(
                        pos[0] + dx, pos[1] + dy))
                self.screen.blit(outline_surf, orect)

            text_surf = font_obj.render(text, True, text_color)
            if align == "center":
                trect = text_surf.get_rect(center=pos)
            else:
                trect = text_surf.get_rect(topleft=pos)
            self.screen.blit(text_surf, trect)

        while selecting:
            if hasattr(self, "bg_image") and self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
            else:
                self.screen.fill((30, 30, 30))

            draw_outlined_text(f"Choose a File (\
{'Save' if is_save else 'Load'})",
                               (70, 30), self.font,
                               (255, 255, 255), "topleft")

            try:
                all_files = [f for f in os.listdir(models_dir)
                             if f.endswith(".txt")]
            except Exception:
                all_files = []

            max_scroll = max(0, len(all_files) - max_visible_files)
            scroll_offset = max(0, min(scroll_offset, max_scroll))
            visible_files = all_files[scroll_offset: scroll_offset +
                                      max_visible_files]

            def update_scroll_from_mouse(my):
                nonlocal scroll_offset
                if (max_scroll > 0):
                    rel_y = max(0, min(my - sb_y, sb_h))
                    fraction = rel_y / sb_h
                    scroll_offset = round(fraction * max_scroll)
                    scroll_offset = max(0, min(scroll_offset, max_scroll))

            file_rects = []
            for idx, file in enumerate(visible_files):
                f_rect = pygame.Rect(70, 100 + (idx * 40), 500, 35)
                is_hover = f_rect.collidepoint(pygame.mouse.get_pos())
                color = (60, 60, 90) if is_hover else (40, 40, 40)

                pygame.draw.rect(self.screen, color, f_rect)
                pygame.draw.rect(self.screen, (100, 100, 100), f_rect, 1)

                draw_outlined_text(file, (f_rect.x + 10, f_rect.y + 5),
                                   self.font, (255, 255, 255), "topleft")
                real_idx = scroll_offset + idx
                file_rects.append((f_rect, os.path.join(
                    models_dir, all_files[real_idx])))

            if len(all_files) > max_visible_files:
                pygame.draw.rect(self.screen, (40, 40, 40),
                                 (sb_x, sb_y, sb_w, sb_h))

                thumb_h = max(30, sb_h * (max_visible_files / len(all_files)))
                thumb_y = sb_y + (sb_h - thumb_h) * (
                    scroll_offset / max_scroll) if max_scroll > 0 else sb_y
                pygame.draw.rect(self.screen, (150, 150, 150),
                                 (sb_x, thumb_y, sb_w, thumb_h))

            if (is_save):
                input_rect = pygame.Rect(70, 550, 500, 40)
                pygame.draw.rect(self.screen, (50, 50, 50), input_rect)
                pygame.draw.rect(self.screen, (255, 255, 0), input_rect, 2)

                draw_outlined_text(input_text, (
                    input_rect.x + 10, input_rect.y + 8),
                    self.font, (255, 255, 0), "topleft")

                save_btn_rect = pygame.Rect(600, 550, 100, 40)
                pygame.draw.rect(self.screen, (0, 150, 0), save_btn_rect)
                draw_outlined_text("Save", (
                    save_btn_rect.x + 20, save_btn_rect.y + 8),
                    self.font, (255, 255, 255), "topleft")
            else:
                save_btn_rect = None

            cancel_rect = pygame.Rect(600, 610, 100, 40)
            pygame.draw.rect(self.screen, (150, 100, 0), cancel_rect)
            draw_outlined_text("Cancel", (cancel_rect.x + 10,
                                          cancel_rect.y + 8),
                               self.font, (255, 255, 255),
                               "topleft")

            none_rect = pygame.Rect(600, 670, 100, 40)
            pygame.draw.rect(self.screen, (150, 0, 0), none_rect)
            draw_outlined_text("None", none_rect.center, self.font,
                               (255, 255, 255), "center")

            pygame.display.flip()

            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    pygame.quit()
                    sys.exit()

                elif (event.type == pygame.MOUSEWHEEL):
                    scroll_offset -= event.y

                elif (event.type == pygame.MOUSEBUTTONDOWN):
                    if (event.button == 1):
                        mouse_pos = pygame.mouse.get_pos()
                        sb_rect = pygame.Rect(sb_x, sb_y, sb_w, sb_h)

                        if (len(all_files) > max_visible_files
                           and sb_rect.collidepoint(mouse_pos)):
                            dragging_scrollbar = True
                            update_scroll_from_mouse(mouse_pos[1])
                        else:
                            for f_rect, full_path in file_rects:
                                if (f_rect.collidepoint(mouse_pos)):
                                    if (not is_save):
                                        opt["val"] = full_path
                                        selecting = False
                                    else:
                                        input_text = os.path.basename(
                                            full_path)

                            if (is_save and save_btn_rect and
                               save_btn_rect.collidepoint(mouse_pos)):
                                if (input_text):
                                    if (not input_text.endswith(".txt")):
                                        input_text += ".txt"
                                    opt["val"] = os.path.join(
                                        models_dir, input_text)
                                    selecting = False

                            if (cancel_rect.collidepoint(mouse_pos)):
                                selecting = False

                            if (none_rect.collidepoint(mouse_pos)):
                                opt["val"] = ""
                                selecting = False

                elif (event.type == pygame.MOUSEBUTTONUP):
                    if (event.button == 1):
                        dragging_scrollbar = False

                elif (event.type == pygame.MOUSEMOTION):
                    if (dragging_scrollbar):
                        mouse_pos = pygame.mouse.get_pos()
                        update_scroll_from_mouse(mouse_pos[1])

                elif (event.type == pygame.KEYDOWN and is_save):
                    if (event.key == pygame.K_RETURN):
                        if (input_text):
                            if (not input_text.endswith(".txt")):
                                input_text += ".txt"
                            opt["val"] = os.path.join(models_dir, input_text)
                            selecting = False
                    elif (event.key == pygame.K_BACKSPACE):
                        input_text = input_text[:-1]
                    elif (event.unicode):
                        input_text += event.unicode

            clock.tick(30)

    def execute_launch(self):
        config = {opt["name"]: opt["val"] for opt in self.options if
                  (opt["type"] != "action")}

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
