import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import random
import sys
import threading
import os
from item import Item

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

try:
    import pygame
    pygame.mixer.init()
    def play_sound(action):
        try:
            if action == "attack":
                pygame.mixer.Sound(resource_path("assets/audio/attack.mp3")).play()
            elif action == "skill":
                pygame.mixer.Sound(resource_path("assets/audio/skill.mp3")).play()
            elif action == "damage":
                pygame.mixer.Sound(resource_path("assets/audio/damage.mp3")).play()
        except (FileNotFoundError, pygame.error):
            pass
            
    def play_bgm(start=True):
        try:
            if start:
                pygame.mixer.music.load(resource_path("assets/audio/bgm_battle.mp3"))
                pygame.mixer.music.play(-1) # -1 tells Pygame to loop indefinitely
            else:
                pygame.mixer.music.stop()
        except (FileNotFoundError, pygame.error):
            pass
except ImportError:
    def play_sound(action):
        pass
    def play_bgm(start=True):
        pass

class BattlePanel(tk.Toplevel):
    def __init__(self, parent, player, is_boss=False):
        super().__init__(parent)
        self.player = player
        self.is_boss = is_boss
        
        self.title("Battle!" if not is_boss else "Final Battle!")
        self.geometry("800x600")
        self.configure(bg="#0a0a0a")
        self.grab_set()
        try:
            self.state('zoomed')
        except tk.TclError:
            self.attributes('-fullscreen', True)
        
        if self.is_boss:
            self.monster_name = "Demon King Koji"
            self.monster_max_hp = 500
            self.monster_hp = self.monster_max_hp
            self.monster_attack = 45
        else:
            monster_names = ["Slime", "Goblin", "Skeleton"]
            self.monster_name = random.choice(monster_names)
            
            level_bonus_hp = (self.player.level - 1) * 15
            level_bonus_atk = (self.player.level - 1) * 3
            self.monster_max_hp = random.randint(30, 79) + level_bonus_hp
            self.monster_hp = self.monster_max_hp
            self.monster_attack = random.randint(5, 14) + level_bonus_atk
            
        # JRPG Layout: Top 60% is Scene, Bottom 40% is UI
        scene_frame = tk.Frame(self, bg="#0a0a0a")
        scene_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Enemy Info (Top Left)
        enemy_frame = tk.Frame(scene_frame, bg="#141414", bd=3, relief=tk.RIDGE)
        enemy_frame.place(relx=0.05, rely=0.05, relwidth=0.35, relheight=0.20)
        self.m_name_lbl = tk.Label(enemy_frame, font=("Arial", 16, "bold"), fg="#ff3333", bg="#141414")
        self.m_name_lbl.pack(anchor="w", padx=15, pady=(10, 0))
        self.m_hp_lbl = tk.Label(enemy_frame, font=("Arial", 12, "bold"), fg="#ffffff", bg="#141414")
        self.m_hp_lbl.pack(anchor="w", padx=15)
        self.m_hp_bar = ttk.Progressbar(enemy_frame, style="Red.Horizontal.TProgressbar", orient="horizontal", mode="determinate")
        self.m_hp_bar.pack(fill=tk.X, padx=15, pady=5)
        
        # Enemy Sprite (Center Right)
        sprites = {"Slime": "(~_~)", "Goblin": "(\\>/)", "Skeleton": "[x_x]", "Demon King Koji": "\\m/ (>_<) \\m/"}
        sprite_text = sprites.get(self.monster_name, "???")
        self.m_sprite = tk.Label(scene_frame, text=sprite_text, font=("Consolas", 60, "bold"), fg="#ff3333", bg="#0a0a0a")
        self.m_sprite.place(relx=0.55, rely=0.15, relwidth=0.4, relheight=0.3)
        
        # Player Info (Bottom Right)
        player_frame = tk.Frame(scene_frame, bg="#141414", bd=3, relief=tk.RIDGE)
        player_frame.place(relx=0.60, rely=0.65, relwidth=0.35, relheight=0.25)
        self.p_name_lbl = tk.Label(player_frame, font=("Arial", 16, "bold"), fg="#ffffff", bg="#141414")
        self.p_name_lbl.pack(anchor="w", padx=15, pady=(10, 0))
        self.p_hp_lbl = tk.Label(player_frame, font=("Arial", 12, "bold"), fg="#ff3333", bg="#141414")
        self.p_hp_lbl.pack(anchor="w", padx=15)
        self.p_hp_bar = ttk.Progressbar(player_frame, style="Red.Horizontal.TProgressbar", orient="horizontal", mode="determinate")
        self.p_hp_bar.pack(fill=tk.X, padx=15, pady=2)
        self.p_mana_lbl = tk.Label(player_frame, font=("Arial", 12, "bold"), fg="#3388ff", bg="#141414")
        self.p_mana_lbl.pack(anchor="w", padx=15)
        self.p_mana_bar = ttk.Progressbar(player_frame, style="Blue.Horizontal.TProgressbar", orient="horizontal", mode="determinate")
        self.p_mana_bar.pack(fill=tk.X, padx=15, pady=2)
        
        # Player Sprite (Bottom Left)
        self.p_sprite = tk.Label(scene_frame, text="\\o/", font=("Consolas", 50, "bold"), fg="#3388ff", bg="#0a0a0a")
        self.p_sprite.place(relx=0.10, rely=0.65, relwidth=0.3, relheight=0.3)
        
        # UI Bottom Frame
        ui_frame = tk.Frame(self, bg="#141414", bd=4, relief=tk.RAISED)
        ui_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10, ipady=5)
        
        log_frame = tk.Frame(ui_frame, bg="#000000")
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.battle_log = tk.Text(log_frame, state=tk.DISABLED, wrap=tk.WORD, bg="#000000", fg="#e0e0e0", font=("Consolas", 14), relief=tk.FLAT, insertbackground="white", height=6)
        self.battle_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.append_text(f"A wild {self.monster_name} appears! (HP: {self.monster_hp})")
        
        btn_frame = tk.Frame(ui_frame, bg="#141414")
        btn_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        
        def make_action_btn(text, command, r, c, col_span=1):
            btn = tk.Button(btn_frame, text=text, command=command, bg="#7a0000", fg="#ffffff", 
                            activebackground="#b30000", activeforeground="#ffffff", disabledforeground="#888888",
                            relief=tk.FLAT, font=("Arial", 14, "bold"), pady=15, width=12)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#b30000") if b['state'] != tk.DISABLED else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#7a0000") if b['state'] != tk.DISABLED else None)
            btn.grid(row=r, column=c, columnspan=col_span, sticky="nsew", padx=5, pady=5)
            btn_frame.grid_columnconfigure(c, weight=1)
            btn_frame.grid_rowconfigure(r, weight=1)
            return btn
            
        self.atk_btn = make_action_btn("Attack", self.player_attack, 0, 0)
        self.item_btn = make_action_btn("Item", self.player_item, 0, 1)
        self.def_btn = make_action_btn("Defend", self.player_defend, 1, 0)
        self.run_btn = make_action_btn("Run", self.player_run, 1, 1)
        self.skill_btn = make_action_btn("Skill (20 MP)", self.player_skill, 2, 0, 2)
        
        self.update_player_stats()
        self.update_monster_stats()
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        play_bgm(True)
        self.wait_window(self)

    def destroy(self):
        play_bgm(False)
        super().destroy()

    def update_player_stats(self):
        self.p_name_lbl.config(text=f"{self.player.name} (Lv. {self.player.level})")
        self.p_hp_lbl.config(text=f"HP: {self.player.hp} / {self.player.max_hp}")
        self.p_hp_bar['maximum'] = self.player.max_hp
        self.p_hp_bar['value'] = self.player.hp
        self.p_mana_lbl.config(text=f"MP: {self.player.mana} / 100")
        self.p_mana_bar['maximum'] = 100
        self.p_mana_bar['value'] = self.player.mana
        
        # Dynamic Buttons
        can_skill = self.player.mana >= 20
        self.skill_btn.config(state=tk.NORMAL if can_skill else tk.DISABLED, bg="#7a0000" if can_skill else "#333333")
        
        consumables = [item for item in self.player.inventory if getattr(item, 'is_consumable', False)]
        can_item = len(consumables) > 0
        self.item_btn.config(state=tk.NORMAL if can_item else tk.DISABLED, bg="#7a0000" if can_item else "#333333")

    def update_monster_stats(self):
        self.m_name_lbl.config(text=self.monster_name)
        self.m_hp_lbl.config(text=f"HP: {self.monster_hp} / {self.monster_max_hp}")
        self.m_hp_bar['maximum'] = self.monster_max_hp
        self.m_hp_bar['value'] = self.monster_hp

    def append_text(self, text):
        self.battle_log.config(state=tk.NORMAL)
        self.battle_log.insert(tk.END, text + "\n")
        self.battle_log.see(tk.END)
        self.battle_log.config(state=tk.DISABLED)

    def player_attack(self):
        play_sound("attack")
        weapon_dmg = self.player.equipped_weapon.additional_damage if getattr(self.player, 'equipped_weapon', None) else 0
        damage = 15 + (self.player.level * 5) + int(weapon_dmg) + random.randint(0, 9)
        self.monster_hp -= damage
        self.append_text(f"You attacked the {self.monster_name} for {damage} damage!")
        self.update_monster_stats()
        
        if self.monster_hp <= 0:
            self.append_text(f"You defeated the {self.monster_name}!")
            self.reward_player()
            self.destroy()
            return
            
        self.monster_turn()

    def player_defend(self):
        self.append_text("You brace yourself for an attack.")
        play_sound("damage")
        armor_def = self.player.equipped_armor.defense_bonus if getattr(self.player, 'equipped_armor', None) else 0
        reduced = max(0, self.monster_attack - random.randint(0, 4) - 5 - int(armor_def))
        self.player.hp -= reduced
        self.append_text(f"The {self.monster_name} attacked, but you only took {reduced} damage!")
        self.update_player_stats()
        
        if self.player.hp <= 0:
            self.player_defeated()

    def player_skill(self):
        if self.player.mana >= 20:
            play_sound("skill")
            skill_dmg = 40 + random.randint(0, 19)
            self.player.use_mana(20)
            self.monster_hp -= skill_dmg
            self.append_text(f"You used a powerful skill and dealt {skill_dmg} damage!")
            self.update_monster_stats()
            self.update_player_stats()
            
            if self.monster_hp <= 0:
                self.append_text(f"You defeated the {self.monster_name}!")
                self.reward_player()
                self.destroy()
                return
        else:
            self.append_text("Not enough mana to use skill!")
            return
            
        self.monster_turn()

    def player_run(self):
        if random.randint(0, 99) < 50:
            self.append_text(f"You successfully ran away from the {self.monster_name}!")
            self.destroy()
        else:
            self.append_text("You failed to escape!")
            self.monster_turn()

    def player_item(self):
        consumables = [item for item in self.player.inventory if getattr(item, 'is_consumable', False)]
        if not consumables:
            self.append_text("You don't have any usable items!")
            return
            
        item_win = tk.Toplevel(self)
        item_win.title("Use Item")
        item_win.geometry("350x250")
        item_win.configure(bg="#0a0a0a")
        item_win.grab_set()
        
        tk.Label(item_win, text="Select an item to use:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#0a0a0a").pack(pady=10)
        listbox = tk.Listbox(item_win, bg="#141414", fg="#ffffff", font=("Consolas", 11), selectbackground="#7a0000")
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for item in consumables:
            listbox.insert(tk.END, f"{item.item_name} (Heals {item.heal_amount} HP)")
            
        def on_use():
            selection = listbox.curselection()
            if selection:
                used_item = consumables[selection[0]]
                self.player.inventory.remove(used_item)
                self.player.hp = min(self.player.hp + used_item.heal_amount, self.player.max_hp)
                self.append_text(f"You used {used_item.item_name} and recovered {used_item.heal_amount} HP!")
                self.update_player_stats()
                item_win.destroy()
                self.monster_turn()
                
        use_btn = tk.Button(item_win, text="Use Item", command=on_use, bg="#7a0000", fg="white", activebackground="#b30000", activeforeground="white", relief=tk.FLAT, font=("Arial", 11, "bold"))
        use_btn.bind("<Enter>", lambda e: e.widget.config(bg="#b30000"))
        use_btn.bind("<Leave>", lambda e: e.widget.config(bg="#7a0000"))
        use_btn.pack(pady=10, padx=20, fill=tk.X)

    def monster_turn(self):
        play_sound("damage")
        armor_def = self.player.equipped_armor.defense_bonus if getattr(self.player, 'equipped_armor', None) else 0
        taken = max(0, self.monster_attack + random.randint(0, 4) - int(armor_def))
        self.player.hp -= taken
        self.append_text(f"The {self.monster_name} attacked you for {taken} damage!")
        self.update_player_stats()
        
        if self.player.hp <= 0:
            self.player_defeated()

    def player_defeated(self):
        self.append_text(f"You were defeated by the {self.monster_name}!")
        messagebox.showinfo("Game Over!", "You have been defeated!")
        sys.exit(0)

    def reward_player(self):
        exp = random.randint(20, 49)
        coins = random.randint(10, 29)
        self.player.add_experience(exp)
        self.player.add_coins(coins)
        
        msg = f"{self.player.name} gained {exp} EXP and {coins} coins!"
        
        if not self.is_boss and random.randint(0, 99) < 30:
            loot_pool = [
                Item("Rusty Dagger", "Basic", 8.0),
                Item("Bone Club", "Crude", 11.0),
                Item("Slime Sword", "Sticky", 13.0)
            ]
            dropped_item = random.choice(loot_pool)
            self.player.inventory.append(dropped_item)
            msg += f"\n\nThe monster dropped a {dropped_item.item_name}!"
            
        messagebox.showinfo("Victory!", msg)