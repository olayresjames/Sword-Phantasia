import tkinter as tk
from tkinter import messagebox, simpledialog
import sys
from character import Character
from game_panel import GamePanel
from item import Item

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.withdraw() # Hide main window while menu is active
        self.display_menu()

    def display_menu(self):
        self.menu_win = tk.Toplevel(self.root)
        self.menu_win.title("Main Menu")
        self.menu_win.geometry("400x350")
        self.menu_win.configure(bg="#0a0a0a")
        self.menu_win.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        
        tk.Label(self.menu_win, text="SWORD PHANTASIA", font=("Helvetica", 20, "bold"), fg="#ff3333", bg="#0a0a0a").pack(pady=30)
        
        def create_menu_btn(text, command):
            btn = tk.Button(self.menu_win, text=text, command=command, bg="#7a0000", fg="#ffffff", 
                            activebackground="#b30000", activeforeground="#ffffff", relief=tk.FLAT, font=("Arial", 12, "bold"), pady=5)
            btn.bind("<Enter>", lambda e: e.widget.config(bg="#b30000"))
            btn.bind("<Leave>", lambda e: e.widget.config(bg="#7a0000"))
            btn.pack(fill=tk.X, padx=75, pady=8)
            return btn

        create_menu_btn("Play Game", self.play_game)
        create_menu_btn("Load Game", self.load_game)
        create_menu_btn("Help", self.display_help)
        create_menu_btn("Quit", lambda: sys.exit(0))

    def display_help(self):
        messagebox.showinfo(
            "Help",
            "- Choose 'Play Game' to start your adventure.\n" +
            "- Traverse the world, fight monsters, and level up.\n" +
            "- Reach level 10 to challenge Demon King Koji."
        )

    def load_game(self):
        player = Character.load_from_file()
        if player:
            self.menu_win.destroy()
            self.launch_game_window(player)
        else:
            messagebox.showinfo("Load Game", "No save file found!")

    def play_game(self):
        # Weapon Selection Simulation
        weapon_win = tk.Toplevel(self.root)
        weapon_win.title("Weapon Selection")
        weapon_win.geometry("450x150")
        weapon_win.configure(bg="#0a0a0a")
        weapon_win.grab_set()
        
        tk.Label(weapon_win, text="Choose Your Starting Weapon:", font=("Arial", 14, "bold"), fg="#ffffff", bg="#0a0a0a").pack(pady=15)
        choice_var = tk.StringVar(value="")
        
        def select_wep(w):
            choice_var.set(w)
            weapon_win.destroy()
            
        f = tk.Frame(weapon_win, bg="#0a0a0a")
        f.pack()
        
        for idx, w_name in enumerate(["Sword", "Bow", "Axe", "Cancel"]):
            btn = tk.Button(f, text=w_name, command=lambda cmd=w_name: select_wep(cmd), 
                            bg="#7a0000", fg="white", activebackground="#b30000", activeforeground="white", relief=tk.FLAT, font=("Arial", 11, "bold"), width=8)
            btn.bind("<Enter>", lambda e: e.widget.config(bg="#b30000"))
            btn.bind("<Leave>", lambda e: e.widget.config(bg="#7a0000"))
            btn.grid(row=0, column=idx, padx=10)
        
        self.root.wait_window(weapon_win)
        
        if choice_var.get() in ["Cancel", ""]:
            return
            
        self.menu_win.destroy()
        
        # Name Selection
        p_name = simpledialog.askstring("Character Creation", "Enter your character's name:", parent=self.root)
        if not p_name or not p_name.strip():
            p_name = "Hero"
            
        wep_choice = choice_var.get()
        player = Character(p_name, 1, starting_weapon=wep_choice)

        if wep_choice == "Sword":
            weapon = Item("Sword", "Sharp Blade", 10.0)
        elif wep_choice == "Bow":
            weapon = Item("Bow", "Ranged", 8.0)
        elif wep_choice == "Axe":
            weapon = Item("Axe", "Heavy Hit", 12.0)
            
        player.inventory.append(weapon)
        player.equipped_weapon = weapon

        # Start Game Frame
        self.launch_game_window(player)

    def launch_game_window(self, player):
        self.root.deiconify()
        self.root.title("Sword Phantasia")
        self.root.geometry("1024x768")
        self.root.minsize(1024, 700)
        self.root.resizable(True, True)
        try:
            self.root.state('zoomed') # Maximizes on Windows
        except tk.TclError:
            self.root.attributes('-fullscreen', True) # Fallback for Mac/Linux
        self.root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        
        game_panel = GamePanel(self.root, player)
        game_panel.pack(fill=tk.BOTH, expand=True)
