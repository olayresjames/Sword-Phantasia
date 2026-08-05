import os
import sys
import math
import tkinter as tk

from battle_panel import resource_path
from audio_manager import audio_manager
from character import Character
from game_panel import GamePanel
from game_settings import apply_display_mode, apply_fullscreen
from game_settings import settings
from item import Item
from ui_dialogs import alert, confirm, show_guide


class MainMenu:
    BG = "#070a11"
    SURFACE = "#101621"
    SURFACE_ALT = "#151d2b"
    BORDER = "#2a354b"
    TEXT = "#f2f5ff"
    MUTED = "#8793ac"
    GOLD = "#ffd166"
    RED = "#d64352"
    BLUE = "#4ca8ff"
    PURPLE = "#a977e8"

    WEAPONS = {
        "Sword": {"class": "Vanguard", "description": "Balanced offense and defense", "damage": 10.0, "attributes": "Sharp Blade", "sprite": "assets/hero-sprites/sword.png"},
        "Bow": {"class": "Ranger", "description": "Multi-hit volleys and evasion", "damage": 8.0, "attributes": "Ranged", "sprite": "assets/hero-sprites/bow.png"},
        "Axe": {"class": "Berserker", "description": "Overwhelming burst damage", "damage": 12.0, "attributes": "Heavy Hit", "sprite": "assets/hero-sprites/axe.png"},
    }

    def __init__(self, root):
        self.root = root
        self.root.deiconify()
        self.menu_images = {}
        audio_manager.configure(settings.get("music_volume"), settings.get("sfx_volume"))
        audio_manager.play_music("menu")
        self.display_menu()

    def display_menu(self):
        self.menu_win = self.root
        for child in self.menu_win.winfo_children():
            child.destroy()
        self.menu_win.title("Sword Phantasia")
        width = self.menu_win.winfo_screenwidth()
        height = self.menu_win.winfo_screenheight()
        self.menu_win.geometry(f"{width}x{height}+0+0")
        self.menu_win.resizable(False, False)
        apply_fullscreen(self.menu_win)
        self.menu_win.configure(bg=self.BG)
        self.menu_win.protocol("WM_DELETE_WINDOW", self.quit_game)
        self._center_window(self.menu_win, width, height)
        self.menu_win.grid_rowconfigure(0, weight=1)
        # Preserve the original 570:390 artwork/menu split inside the 16:10 window.
        self.menu_win.grid_columnconfigure(0, weight=19, uniform="title")
        self.menu_win.grid_columnconfigure(1, weight=13, uniform="title")

        self.showcase = tk.Canvas(self.menu_win, bg="#090e18", highlightthickness=0)
        self.showcase.grid(row=0, column=0, sticky="nsew")
        self._scaled_title_art = None
        self._title_art_zoom = 0
        self._scaled_menu_images = {}
        self._menu_image_zoom = 0
        try:
            self.title_art = tk.PhotoImage(file=resource_path("assets/environments/title.png"))
        except (tk.TclError, OSError):
            self.title_art = None
        for weapon, data in self.WEAPONS.items():
            try:
                self.menu_images[weapon] = tk.PhotoImage(file=resource_path(data["sprite"]))
            except (tk.TclError, OSError):
                self.menu_images[weapon] = None
        self.showcase.bind("<Configure>", self._draw_title_showcase)

        menu = tk.Frame(self.menu_win, bg=self.SURFACE, highlightbackground=self.BORDER, highlightthickness=1)
        menu.grid(row=0, column=1, sticky="nsew")
        menu.pack_propagate(False)
        tk.Label(menu, text="MAIN MENU", font=("Arial", 9, "bold"), fg=self.MUTED, bg=self.SURFACE).pack(anchor="w", padx=38, pady=(62, 8))
        tk.Label(menu, text="Begin your journey", font=("Georgia", 22, "bold"), fg=self.TEXT, bg=self.SURFACE).pack(anchor="w", padx=38, pady=(0, 25))

        self._menu_button(menu, "NEW JOURNEY", self.play_game, self.RED, "#f05a68")
        self.continue_btn = self._menu_button(menu, "CONTINUE", self.load_game, "#283550", "#3a4a6d")
        self._menu_button(menu, "GUIDE & CONTROLS", self.display_help, self.SURFACE_ALT, "#253149")
        self._menu_button(menu, "QUIT", self.quit_game, "#251a22", "#4b252f")

        save_preview = tk.Frame(menu, bg="#0c111b", highlightbackground="#242e41", highlightthickness=1)
        save_preview.pack(side=tk.BOTTOM, fill=tk.X, padx=28, pady=28)
        tk.Label(save_preview, text="CONTINUE DATA", font=("Arial", 8, "bold"), fg=self.MUTED, bg="#0c111b").pack(anchor="w", padx=14, pady=(12, 4))
        self.save_preview_lbl = tk.Label(save_preview, justify=tk.LEFT, font=("Consolas", 9, "bold"), fg="#bac4d8", bg="#0c111b")
        self.save_preview_lbl.pack(anchor="w", padx=14, pady=(0, 12))
        self._refresh_save_preview()

        tk.Label(menu, text="v1.0  •  LOCAL ADVENTURE", font=("Arial", 8, "bold"), fg="#536078", bg=self.SURFACE).pack(side=tk.BOTTOM, pady=(0, 4))
        self.menu_win.bind("<KeyPress-n>", lambda _event: self.play_game())
        self.menu_win.bind("<KeyPress-c>", lambda _event: self.load_game() if self.continue_btn["state"] != tk.DISABLED else None)
        self.menu_win.bind("<Escape>", lambda _event: self.quit_game())
        self.menu_win.focus_set()

    def _draw_title_showcase(self, event=None):
        canvas = self.showcase
        width = max(1, event.width if event else canvas.winfo_width())
        height = max(1, event.height if event else canvas.winfo_height())
        scale_x = width / 570.0
        scale_y = height / 600.0
        scale = min(scale_x, scale_y)

        def point(x, y):
            return x * scale_x, y * scale_y

        def points(*coordinates):
            transformed = []
            for index in range(0, len(coordinates), 2):
                transformed.extend(point(coordinates[index], coordinates[index + 1]))
            return transformed

        def font(family, size, weight=None, maximum=None):
            scaled = max(7, int(round(size * scale)))
            if maximum is not None:
                scaled = min(maximum, scaled)
            return (family, scaled, weight) if weight else (family, scaled)

        canvas.delete("all")
        if self.title_art:
            art_zoom = max(1, math.ceil(max(width / self.title_art.width(), height / self.title_art.height())))
            if art_zoom != self._title_art_zoom:
                self._scaled_title_art = self.title_art.zoom(art_zoom, art_zoom)
                self._title_art_zoom = art_zoom
            canvas.create_image(width / 2, height / 2, image=self._scaled_title_art)
        else:
            canvas.create_rectangle(0, 0, width, height, fill="#0e1626", outline="")
        canvas.create_rectangle(*points(28, 35, 535, 248), fill="#080b13", outline="#3d4860", width=max(1, int(scale)), stipple="gray50")
        canvas.create_rectangle(*points(0, 468, 570, 600), fill="#080b13", outline="", stipple="gray50")

        canvas.create_text(*point(52, 72), text="SWORD", anchor="w", font=font("Georgia", 40, "bold", 54), fill=self.TEXT)
        canvas.create_text(*point(52, 122), text="PHANTASIA", anchor="w", font=font("Georgia", 33, "bold", 45), fill=self.GOLD)
        canvas.create_text(*point(55, 166), text="A REALM AT THE EDGE OF DARKNESS", anchor="w", font=font("Segoe UI", 9, "bold", 13), fill=self.PURPLE)
        canvas.create_text(*point(55, 196), text="Choose your path. Break the three seals. Face the king beyond the veil.", anchor="nw", width=max(240, int(420 * scale_x)), font=font("Segoe UI", 10, maximum=16), fill="#bdc8dc")

        positions = {"Sword": (125, 525), "Bow": (285, 525), "Axe": (445, 525)}
        image_zoom = max(1, int(round(scale)))
        if image_zoom != self._menu_image_zoom:
            self._scaled_menu_images = {
                name: image.zoom(image_zoom, image_zoom) if image else None
                for name, image in self.menu_images.items()
            }
            self._menu_image_zoom = image_zoom
        for weapon, (x, y) in positions.items():
            x_pos, y_pos = point(x, y)
            canvas.create_oval(*points(x - 58, y + 37, x + 58, y + 56), fill="#111827", outline="#41506c", width=max(1, int(scale)))
            image = self._scaled_menu_images.get(weapon)
            if image:
                canvas.create_image(x_pos, y_pos, image=image)
            else:
                canvas.create_text(x_pos, y_pos, text=weapon[0], font=font("Georgia", 34, "bold"), fill=self.BLUE)
            canvas.create_text(*point(x, 583), text=self.WEAPONS[weapon]["class"].upper(), anchor="center", font=font("Segoe UI", 8, "bold"), fill="#b9c5da")

    @staticmethod
    def _title_window_size(window):
        screen_width = max(640, window.winfo_screenwidth())
        screen_height = max(400, window.winfo_screenheight())
        available_width = int(screen_width * 0.94)
        available_height = int(screen_height * 0.88)
        width = min(1200, available_width)
        height = int(round(width * 5 / 8))
        if height > available_height:
            height = available_height
            width = int(round(height * 8 / 5))
        return max(640, width), max(400, height)

    def _menu_button(self, parent, text, command, color, hover):
        button = tk.Button(parent, text=text, command=command, bg=color, fg=self.TEXT, activebackground=hover, activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Segoe UI", 11, "bold"), cursor="hand2", pady=13, anchor="w", padx=20, highlightthickness=2, highlightbackground=color, highlightcolor=self.GOLD)
        button.base_color = color
        button.hover_color = hover
        button.bind("<Enter>", lambda event: event.widget.config(bg=event.widget.hover_color) if event.widget["state"] != tk.DISABLED else None)
        button.bind("<Leave>", lambda event: event.widget.config(bg=event.widget.base_color) if event.widget["state"] != tk.DISABLED else None)
        button.pack(fill=tk.X, padx=38, pady=6)
        return button

    def _refresh_save_preview(self):
        if not os.path.exists("savegame.json"):
            self.save_preview_lbl.config(text="No saved journey found.", fg=self.MUTED)
            self.continue_btn.config(state=tk.DISABLED, text="CONTINUE  •  NO SAVE", bg="#191e2a", fg="#5f687a")
            return
        try:
            player = Character.load_from_file()
        except (OSError, ValueError, KeyError):
            player = None
        if not player:
            self.save_preview_lbl.config(text="Save data could not be read.", fg=self.RED)
            self.continue_btn.config(state=tk.DISABLED, text="CONTINUE  •  INVALID SAVE", bg="#191e2a", fg="#5f687a")
            return
        weapon = player.equipped_weapon.item_name if player.equipped_weapon else "Unarmed"
        self.save_preview_lbl.config(text=f"{player.name.upper()}  •  LEVEL {player.level}\n{weapon}  •  {player.coins} GOLD", fg="#bac4d8")
        self.continue_btn.config(state=tk.NORMAL, text="CONTINUE", bg=self.continue_btn.base_color, fg=self.TEXT)

    def display_help(self):
        show_guide(self.menu_win)

    def load_game(self):
        player = Character.load_from_file()
        if player:
            self._clear_menu()
            self.launch_game_window(player)
        else:
            alert(self.menu_win, "Load Game", "No valid save file was found.", accent=self.RED)

    def play_game(self):
        weapon_win = tk.Toplevel(self.menu_win)
        weapon_win.title("Choose Your Weapon")
        weapon_win.geometry("760x430")
        weapon_win.resizable(False, False)
        weapon_win.configure(bg=self.BG)
        weapon_win.transient(self.menu_win)
        weapon_win.grab_set()
        apply_fullscreen(weapon_win)

        weapon_content = tk.Frame(weapon_win, bg=self.BG, width=1040, height=650)
        weapon_content.place(relx=.5, rely=.5, anchor="center")
        weapon_content.pack_propagate(False)
        tk.Label(weapon_content, text="CHOOSE YOUR PATH", font=("Georgia", 28, "bold"), fg=self.TEXT, bg=self.BG).pack(pady=(30, 4))
        tk.Label(weapon_content, text="Your first weapon defines your representative battle sprite.", font=("Segoe UI", 11), fg=self.MUTED, bg=self.BG).pack()
        choice_var = tk.StringVar(value="")
        cards = tk.Frame(weapon_content, bg=self.BG)
        cards.pack(fill=tk.BOTH, expand=True, padx=26, pady=24)
        weapon_images = []

        def select_weapon(name):
            choice_var.set(name)
            weapon_win.destroy()

        for column, (name, data) in enumerate(self.WEAPONS.items()):
            card = tk.Frame(cards, bg=self.SURFACE, highlightbackground=self.BORDER, highlightthickness=1)
            card.grid(row=0, column=column, sticky="nsew", padx=8)
            cards.grid_columnconfigure(column, weight=1, uniform="weapon")
            try:
                image = tk.PhotoImage(file=resource_path(data["sprite"]))
                weapon_images.append(image)
            except (tk.TclError, OSError):
                image = ""
            button = tk.Button(card, image=image, text=f"{data['class'].upper()}\n{name}  •  {data['description']}\n+{data['damage']:.0f} starting damage", compound=tk.TOP, command=lambda weapon=name: select_weapon(weapon), bg=self.SURFACE, fg=self.TEXT, activebackground="#243149", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Arial", 10, "bold"), cursor="hand2", padx=12, pady=16, wraplength=190, justify=tk.CENTER)
            button.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            button.bind("<Enter>", lambda event: event.widget.config(bg="#243149"))
            button.bind("<Leave>", lambda event: event.widget.config(bg=self.SURFACE))
        weapon_win.weapon_images = weapon_images
        tk.Button(weapon_content, text="CANCEL", command=weapon_win.destroy, bg=self.BG, fg=self.MUTED, activebackground="#251a22", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Segoe UI", 9, "bold"), cursor="hand2", padx=18, pady=8).pack(pady=(0, 18))
        weapon_win.bind("<Escape>", lambda _event: weapon_win.destroy())
        self.root.wait_window(weapon_win)

        weapon_choice = choice_var.get()
        if not weapon_choice:
            return

        player_name = self._ask_hero_name()
        if not player_name or not player_name.strip():
            player_name = "Hero"
        player_name = player_name.strip()
        data = self.WEAPONS[weapon_choice]
        player = Character(player_name, 1, starting_weapon=weapon_choice)
        weapon = Item(weapon_choice, data["attributes"], data["damage"])
        player.add_item(weapon, auto_salvage=False)
        player.equipped_weapon = weapon
        self._clear_menu()
        self.launch_game_window(player)

    def _clear_menu(self):
        audio_manager.stop_music()
        for child in self.root.winfo_children():
            child.destroy()

    def _ask_hero_name(self):
        result = {"name": ""}
        window = tk.Toplevel(self.menu_win)
        window.title("Name Your Hero")
        window.geometry("500x270")
        window.resizable(False, False)
        window.configure(bg=self.BG)
        window.transient(self.menu_win)
        window.grab_set()
        apply_fullscreen(window)
        name_content = tk.Frame(window, bg=self.BG, width=620, height=360, highlightbackground=self.BORDER, highlightthickness=1)
        name_content.place(relx=.5, rely=.5, anchor="center")
        name_content.pack_propagate(False)
        header = tk.Frame(name_content, bg=self.SURFACE, height=96, highlightbackground=self.BORDER, highlightthickness=1)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="NAME YOUR HERO", font=("Georgia", 21, "bold"), fg=self.TEXT, bg=self.SURFACE).pack(anchor="w", padx=26, pady=(17, 0))
        tk.Label(header, text="This name will be written into the chronicles.", font=("Segoe UI", 9), fg=self.MUTED, bg=self.SURFACE).pack(anchor="w", padx=26)
        name_var = tk.StringVar()
        entry = tk.Entry(name_content, textvariable=name_var, bg="#0b1019", fg="#ffffff", insertbackground="#ffffff", relief=tk.FLAT, font=("Segoe UI", 15), justify=tk.CENTER, highlightthickness=2, highlightbackground=self.BORDER, highlightcolor=self.BLUE)
        entry.pack(fill=tk.X, padx=34, pady=(28, 18), ipady=8)

        def submit():
            result["name"] = name_var.get().strip()
            window.destroy()

        tk.Button(name_content, text="BEGIN JOURNEY", command=submit, bg=self.RED, fg="#ffffff", activebackground="#f05a68", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Segoe UI", 10, "bold"), pady=11).pack(fill=tk.X, padx=34)
        entry.bind("<Return>", lambda _event: submit())
        window.bind("<Escape>", lambda _event: window.destroy())
        entry.focus_set()
        self.root.wait_window(window)
        return result["name"]

    def launch_game_window(self, player):
        audio_manager.configure(settings.get("music_volume"), settings.get("sfx_volume"))
        self.root.deiconify()
        self.root.title("Sword Phantasia")
        self.root.geometry("1200x760")
        self.root.minsize(1024, 700)
        self.root.resizable(True, True)
        apply_display_mode(self.root)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)
        game_panel = GamePanel(self.root, player)
        game_panel.pack(fill=tk.BOTH, expand=True)

    def quit_game(self):
        parent = self.root
        menu = getattr(self, "menu_win", None)
        try:
            if menu and menu.winfo_exists():
                parent = menu
        except tk.TclError:
            pass
        if confirm(parent, "Leave Sword Phantasia?", "Quit the game?", confirm_text="QUIT GAME", accent=self.RED, danger=True):
            self.root.destroy()

    @staticmethod
    def _center_window(window, width, height):
        window.update_idletasks()
        x = max(0, (window.winfo_screenwidth() - width) // 2)
        y = max(0, (window.winfo_screenheight() - height) // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    @staticmethod
    def _center_over_parent(window, parent, width, height):
        parent.update_idletasks()
        x = parent.winfo_rootx() + max(0, (parent.winfo_width() - width) // 2)
        y = parent.winfo_rooty() + max(0, (parent.winfo_height() - height) // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
