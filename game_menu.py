import tkinter as tk
from tkinter import messagebox, simpledialog
import sys
from character import Character
from game_panel import GamePanel

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.withdraw() # Hide main window while menu is active
        self.display_menu()

    def display_menu(self):
        self.menu_win = tk.Toplevel(self.root)
        self.menu_win.title("Main Menu")
        self.menu_win.geometry("300x200")
        self.menu_win.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        
        tk.Label(self.menu_win, text="Welcome to Sword Phantasia", font=("Arial", 12, "bold")).pack(pady=20)
        tk.Button(self.menu_win, text="Play Game", command=self.play_game).pack(fill=tk.X, padx=50, pady=5)
        tk.Button(self.menu_win, text="Help", command=self.display_help).pack(fill=tk.X, padx=50, pady=5)
        tk.Button(self.menu_win, text="Quit", command=lambda: sys.exit(0)).pack(fill=tk.X, padx=50, pady=5)

    def display_help(self):
        messagebox.showinfo(
            "Help",
            "- Choose 'Play Game' to start your adventure.\n" +
            "- Traverse the world, fight monsters, and level up.\n" +
            "- Reach level 10 to challenge Demon King Koji."
        )

    def play_game(self):
        # Weapon Selection Simulation
        weapon_win = tk.Toplevel(self.root)
        weapon_win.title("Weapon Selection")
        weapon_win.geometry("300x100")
        weapon_win.grab_set()
        
        tk.Label(weapon_win, text="Choose Your Weapon").pack(pady=10)
        choice_var = tk.StringVar(value="")
        
        def select_wep(w):
            choice_var.set(w)
            weapon_win.destroy()
            
        f = tk.Frame(weapon_win)
        f.pack()
        tk.Button(f, text="Sword", command=lambda: select_wep("Sword")).grid(row=0, column=0, padx=5)
        tk.Button(f, text="Bow", command=lambda: select_wep("Bow")).grid(row=0, column=1, padx=5)
        tk.Button(f, text="Axe", command=lambda: select_wep("Axe")).grid(row=0, column=2, padx=5)
        tk.Button(f, text="Cancel", command=lambda: select_wep("Cancel")).grid(row=0, column=3, padx=5)
        
        self.root.wait_window(weapon_win)
        
        if choice_var.get() in ["Cancel", ""]:
            return
            
        self.menu_win.destroy()
        
        # Name Selection
        p_name = simpledialog.askstring("Character Creation", "Enter your character's name:", parent=self.root)
        if not p_name or not p_name.strip():
            p_name = "Hero"
            
        player = Character(p_name, 1)
        
        # Start Game Frame
        self.root.deiconify()
        self.root.title("Sword Phantasia")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        
        game_panel = GamePanel(self.root, player)
        game_panel.pack(fill=tk.BOTH, expand=True)