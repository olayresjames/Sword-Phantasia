import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog

from battle_panel import resource_path
from character import Character
from game_panel import GamePanel
from item import Item


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
        self.root.withdraw()
        self.menu_images = []
        self.display_menu()

    def display_menu(self):
        self.menu_win = tk.Toplevel(self.root)
        self.menu_win.title("Sword Phantasia")
        self.menu_win.geometry("960x600")
        self.menu_win.resizable(False, False)
        self.menu_win.configure(bg=self.BG)
        self.menu_win.protocol("WM_DELETE_WINDOW", self.quit_game)
        self._center_window(self.menu_win, 960, 600)

        showcase = tk.Canvas(self.menu_win, width=570, height=600, bg="#090e18", highlightthickness=0)
        showcase.pack(side=tk.LEFT, fill=tk.BOTH)
        showcase.create_polygon(0, 0, 570, 0, 570, 600, 405, 600, 175, 0, fill="#0e1626", outline="")
        showcase.create_polygon(0, 600, 0, 300, 300, 600, fill="#111b2c", outline="")
        showcase.create_line(48, 455, 510, 455, fill="#35415a")
        showcase.create_line(95, 466, 465, 466, fill="#202b3e")
        for x, y, size in ((55, 70, 2), (160, 105, 1), (470, 88, 2), (410, 180, 1), (92, 265, 1), (510, 325, 2)):
            showcase.create_oval(x, y, x + size, y + size, fill="#657596", outline="")

        showcase.create_text(52, 72, text="SWORD", anchor="w", font=("Georgia", 42, "bold"), fill=self.TEXT)
        showcase.create_text(52, 121, text="PHANTASIA", anchor="w", font=("Georgia", 35, "bold"), fill=self.GOLD)
        showcase.create_text(55, 164, text="A REALM AT THE EDGE OF DARKNESS", anchor="w", font=("Arial", 9, "bold"), fill=self.PURPLE)
        showcase.create_text(55, 192, text="Choose your weapon. Shape your legend.\nDefeat the primordial king.", anchor="nw", font=("Arial", 11), fill="#aab5ca")

        positions = {"Sword": (140, 370), "Bow": (285, 350), "Axe": (430, 370)}
        for weapon, (x, y) in positions.items():
            try:
                image = tk.PhotoImage(file=resource_path(self.WEAPONS[weapon]["sprite"]))
                self.menu_images.append(image)
                showcase.create_oval(x - 66, y + 46, x + 66, y + 70, fill="#141f31", outline="#33425f")
                showcase.create_image(x, y, image=image)
            except (tk.TclError, OSError):
                showcase.create_text(x, y, text=weapon[0], font=("Georgia", 34, "bold"), fill=self.BLUE)
        showcase.create_text(55, 545, text="THREE PATHS  •  ONE DESTINY", anchor="w", font=("Arial", 9, "bold"), fill="#66738c")

        menu = tk.Frame(self.menu_win, bg=self.SURFACE, width=390, highlightbackground=self.BORDER, highlightthickness=1)
        menu.pack(side=tk.RIGHT, fill=tk.BOTH)
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

    def _menu_button(self, parent, text, command, color, hover):
        button = tk.Button(parent, text=text, command=command, bg=color, fg=self.TEXT, activebackground=hover, activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Arial", 11, "bold"), cursor="hand2", pady=13, anchor="w", padx=20)
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
        messagebox.showinfo(
            "Sword Phantasia — Guide & Controls",
            "ADVENTURE\n"
            "WASD / Arrow Keys — Move\nI — Inventory\nE — Equipment\nEscape — Options & full guide\n\n"
            "BATTLE\n"
            "A — Attack    D — Defend    I — Item\nS — Skill    R — Escape\n\n"
            "Defeat monsters to earn EXP and gold. Reach level 10 to challenge Demon King Koji.",
            parent=self.menu_win,
        )

    def load_game(self):
        player = Character.load_from_file()
        if player:
            self.menu_win.destroy()
            self.launch_game_window(player)
        else:
            messagebox.showinfo("Load Game", "No valid save file was found.", parent=self.menu_win)

    def play_game(self):
        weapon_win = tk.Toplevel(self.menu_win)
        weapon_win.title("Choose Your Weapon")
        weapon_win.geometry("760x430")
        weapon_win.resizable(False, False)
        weapon_win.configure(bg=self.BG)
        weapon_win.transient(self.menu_win)
        weapon_win.grab_set()
        self._center_over_parent(weapon_win, self.menu_win, 760, 430)

        tk.Label(weapon_win, text="CHOOSE YOUR PATH", font=("Georgia", 24, "bold"), fg=self.TEXT, bg=self.BG).pack(pady=(30, 4))
        tk.Label(weapon_win, text="Your first weapon defines your representative battle sprite.", font=("Arial", 10), fg=self.MUTED, bg=self.BG).pack()
        choice_var = tk.StringVar(value="")
        cards = tk.Frame(weapon_win, bg=self.BG)
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
        tk.Button(weapon_win, text="CANCEL", command=weapon_win.destroy, bg=self.BG, fg=self.MUTED, activebackground="#251a22", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Arial", 9, "bold"), cursor="hand2", padx=18, pady=8).pack(pady=(0, 18))
        self.root.wait_window(weapon_win)

        weapon_choice = choice_var.get()
        if not weapon_choice:
            return

        player_name = simpledialog.askstring("Character Creation", "Name your hero:", parent=self.menu_win)
        if not player_name or not player_name.strip():
            player_name = "Hero"
        player_name = player_name.strip()
        data = self.WEAPONS[weapon_choice]
        player = Character(player_name, 1, starting_weapon=weapon_choice)
        weapon = Item(weapon_choice, data["attributes"], data["damage"])
        player.inventory.append(weapon)
        player.equipped_weapon = weapon
        self.menu_win.destroy()
        self.launch_game_window(player)

    def launch_game_window(self, player):
        self.root.deiconify()
        self.root.title("Sword Phantasia")
        self.root.geometry("1200x760")
        self.root.minsize(1024, 700)
        self.root.resizable(True, True)
        try:
            self.root.state("zoomed")
        except tk.TclError:
            self.root.attributes("-fullscreen", True)
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
        if messagebox.askyesno("Leave Sword Phantasia?", "Quit the game?", parent=parent):
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
