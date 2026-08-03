import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import random
import sys
import threading
import os
from item import Item

HERO_SPRITES = {
    "sword": "assets/hero-sprites/sword.png",
    "bow": "assets/hero-sprites/bow.png",
    "axe": "assets/hero-sprites/axe.png",
}

MONSTER_SPRITES = {
    "Slime": "assets/monster-sprites/slime.png",
    "Goblin": "assets/monster-sprites/goblin.png",
    "Skeleton": "assets/monster-sprites/skeleton.png",
    "Demon King Koji": "assets/monster-sprites/demon-king-koji.png",
}

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def hero_sprite_path(player):
    """Return the sprite for the character's original weapon choice."""
    weapon_name = getattr(player, "starting_weapon", None)
    if not weapon_name:
        equipped_weapon = getattr(player, "equipped_weapon", None)
        weapon_name = getattr(equipped_weapon, "item_name", "")

    normalized_name = str(weapon_name).lower()
    for weapon_type, sprite_path in HERO_SPRITES.items():
        if weapon_type in normalized_name:
            return resource_path(sprite_path)
    return None

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


class VictoryScreen(tk.Toplevel):
    """JRPG-inspired battle results screen."""

    def __init__(self, parent, player, monster_name, exp, coins, loot=None, leveled_up=False):
        super().__init__(parent)
        self.player = player
        self.is_final_victory = monster_name == "Demon King Koji"
        self._animation_jobs = []
        self._particles = []
        self.title("Victory!")
        self.geometry("900x620")
        self.minsize(760, 540)
        self.resizable(False, False)
        self.configure(bg="#080b13")
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.update_idletasks()
        x = parent.winfo_rootx() + max(0, (parent.winfo_width() - 900) // 2)
        y = parent.winfo_rooty() + max(0, (parent.winfo_height() - 620) // 2)
        self.geometry(f"900x620+{x}+{y}")

        banner = tk.Canvas(self, height=205, bg="#0c1120", highlightthickness=0)
        banner.pack(fill=tk.X)
        self.banner = banner
        banner.create_rectangle(0, 0, 900, 205, fill="#0c1120", outline="")
        banner.create_polygon(0, 205, 320, 0, 430, 0, 165, 205, fill="#111a2c", outline="")
        banner.create_polygon(900, 205, 580, 0, 470, 0, 735, 205, fill="#111a2c", outline="")
        banner.create_line(80, 166, 820, 166, fill="#8c6b25", width=1)
        banner.create_line(170, 174, 730, 174, fill="#3d3528", width=1)

        sprite_path = hero_sprite_path(player)
        self.hero_image = None
        if sprite_path:
            try:
                self.hero_image = tk.PhotoImage(file=sprite_path)
            except (tk.TclError, OSError):
                pass
        if self.hero_image:
            banner.create_image(125, 108, image=self.hero_image)

        banner.create_text(450, 55, text="VICTORY", font=("Georgia", 36, "bold"), fill="#ffd66b")
        victory_subtitle = "THE PRIMORDIAL THRONE HAS FALLEN" if self.is_final_victory else f"{monster_name.upper()} DEFEATED"
        banner.create_text(450, 101, text=victory_subtitle, font=("Arial", 12, "bold"), fill="#d9e0f2")
        banner.create_text(450, 134, text="BATTLE RESULTS", font=("Arial", 9, "bold"), fill="#77839f")

        if leveled_up:
            banner.create_text(760, 70, text="LEVEL UP!", font=("Arial", 13, "bold"), fill="#080b13", tags="level_badge")
            banner.create_rectangle(696, 51, 824, 89, fill="#ffd166", outline="#fff0a8", width=2, tags="level_badge_bg")
            banner.tag_raise("level_badge")

        body = tk.Frame(self, bg="#080b13")
        body.pack(fill=tk.BOTH, expand=True, padx=34, pady=22)

        results = tk.Frame(body, bg="#111724", highlightbackground="#303b55", highlightthickness=1)
        results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        tk.Label(results, text="REWARDS", font=("Arial", 10, "bold"), fg="#8794af", bg="#111724").pack(anchor="w", padx=22, pady=(18, 10))

        self.exp_reward_lbl = self._reward_row(results, "EXP EARNED", "0", "#79dda8")
        self.coin_reward_lbl = self._reward_row(results, "GOLD ACQUIRED", "0", "#ffd166")
        loot_name = loot.item_name if loot else "No item dropped"
        loot_color = "#c49cff" if loot else "#68738c"
        self._reward_row(results, "TREASURE", loot_name, loot_color)

        progress = tk.Frame(body, bg="#111724", highlightbackground="#303b55", highlightthickness=1, width=330)
        progress.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        progress.pack_propagate(False)
        tk.Label(progress, text="ADVENTURER", font=("Arial", 10, "bold"), fg="#8794af", bg="#111724").pack(anchor="w", padx=22, pady=(18, 8))
        tk.Label(progress, text=player.name, font=("Arial", 22, "bold"), fg="#f4f6ff", bg="#111724").pack(anchor="w", padx=22)
        level_color = "#ffd166" if leveled_up else "#62b4ff"
        tk.Label(progress, text=f"LEVEL {player.level}", font=("Arial", 13, "bold"), fg=level_color, bg="#111724").pack(anchor="w", padx=22, pady=(4, 22))

        xp_style = ttk.Style(self)
        try:
            xp_style.theme_use("clam")
        except tk.TclError:
            pass
        xp_style.configure("VictoryXP.Horizontal.TProgressbar", troughcolor="#282f40", background="#ffd166", bordercolor="#282f40", lightcolor="#ffd166", darkcolor="#ffd166", thickness=12)
        xp_header = tk.Frame(progress, bg="#111724")
        xp_header.pack(fill=tk.X, padx=22)
        tk.Label(xp_header, text="NEXT LEVEL", font=("Arial", 9, "bold"), fg="#8794af", bg="#111724").pack(side=tk.LEFT)
        tk.Label(xp_header, text=f"{player.experience} / 100 EXP", font=("Consolas", 9, "bold"), fg="#dce3f4", bg="#111724").pack(side=tk.RIGHT)
        xp_bar = ttk.Progressbar(progress, style="VictoryXP.Horizontal.TProgressbar", maximum=100, value=player.experience)
        xp_bar.pack(fill=tk.X, padx=22, pady=(7, 22), ipady=3)

        if self.is_final_victory:
            status_text = "Demon King Koji is no more. The realm is free."
        elif leveled_up:
            status_text = "Your strength has reached a new height."
        else:
            status_text = "The journey continues."
        tk.Label(progress, text=status_text, wraplength=275, justify=tk.LEFT, font=("Arial", 10), fg="#9ca7bd", bg="#111724").pack(anchor="w", padx=22)

        continue_btn = tk.Button(
            self,
            text="COMPLETE JOURNEY  ›" if self.is_final_victory else "CONTINUE  ›",
            command=self.destroy,
            bg="#b1832e",
            fg="#ffffff",
            activebackground="#d6a943",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            font=("Arial", 12, "bold"),
            cursor="hand2",
            padx=36,
            pady=12,
        )
        continue_btn.pack(side=tk.BOTTOM, pady=(0, 22))
        continue_btn.bind("<Enter>", lambda event: event.widget.config(bg="#d6a943"))
        continue_btn.bind("<Leave>", lambda event: event.widget.config(bg="#b1832e"))
        self.bind("<Return>", lambda _event: self.destroy())
        self.bind("<space>", lambda _event: self.destroy())
        self.focus_set()

        self._create_particles()
        self._animate_particles()
        self._count_reward(self.exp_reward_lbl, exp, " EXP")
        self._count_reward(self.coin_reward_lbl, coins, " G")
        self.wait_window(self)

    def _reward_row(self, parent, title, value, color):
        row = tk.Frame(parent, bg="#171e2d", height=65)
        row.pack(fill=tk.X, padx=18, pady=5)
        row.pack_propagate(False)
        tk.Frame(row, bg=color, width=4).pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(row, text=title, font=("Arial", 9, "bold"), fg="#8591aa", bg="#171e2d").pack(side=tk.LEFT, padx=16)
        value_label = tk.Label(row, text=value, font=("Consolas", 14, "bold"), fg=color, bg="#171e2d")
        value_label.pack(side=tk.RIGHT, padx=18)
        return value_label

    def _create_particles(self):
        rng = random.Random(23)
        colors = ("#ffd166", "#fff0a8", "#b98d38", "#6f5b32")
        for _ in range(28):
            x = rng.randint(18, 882)
            y = rng.randint(-180, 190)
            size = rng.choice((2, 3, 4))
            speed = rng.choice((1, 1, 2))
            item = self.banner.create_polygon(x, y - size, x + size, y, x, y + size, x - size, y, fill=rng.choice(colors), outline="")
            self._particles.append((item, speed))

    def _animate_particles(self):
        if not self.winfo_exists():
            return
        for item, speed in self._particles:
            self.banner.move(item, 0, speed)
            coords = self.banner.coords(item)
            if coords and min(coords[1::2]) > 205:
                self.banner.move(item, 0, -390)
        self._animation_jobs.append(self.after(45, self._animate_particles))

    def _count_reward(self, label, total, suffix):
        steps = min(24, max(1, total))

        def update(step=0):
            if not label.winfo_exists():
                return
            value = total if step >= steps else int(total * step / steps)
            label.config(text=f"+{value}{suffix}")
            if step < steps:
                self._animation_jobs.append(self.after(28, lambda: update(step + 1)))

        update()

    def destroy(self):
        for job in self._animation_jobs:
            try:
                self.after_cancel(job)
            except (tk.TclError, ValueError):
                pass
        self._animation_jobs.clear()
        try:
            self.grab_release()
        except tk.TclError:
            pass
        super().destroy()


class BattlePanel(tk.Toplevel):
    def __init__(self, parent, player, is_boss=False):
        super().__init__(parent)
        self.player = player
        self.is_boss = is_boss
        self._animation_jobs = []
        self.accent = "#b26cff" if is_boss else "#ff4d5a"
        self.scene_bg = "#090d16"
        self._scene_width = 1
        self._scene_height = 1
        self._idle_offset = 0
        self._sprite_hit_shift = {"player": 0, "monster": 0}
        
        self.title("Battle!" if not is_boss else "Final Battle!")
        self.geometry("1100x720")
        self.minsize(900, 680)
        self.configure(bg="#070910")
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
            
        self._configure_battle_styles()

        # Arena header
        header = tk.Frame(self, bg="#111624", height=58, highlightbackground="#293149", highlightthickness=1)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="⚔  BATTLE ARENA", font=("Arial", 16, "bold"), fg="#f3f5ff", bg="#111624").pack(side=tk.LEFT, padx=24)
        encounter_text = "FINAL ENCOUNTER  •  PRIMORDIAL THRONE" if is_boss else "WILD ENCOUNTER  •  FRONTIER"
        tk.Label(header, text=encounter_text, font=("Arial", 10, "bold"), fg=self.accent, bg="#111624").pack(side=tk.LEFT, padx=12)
        self.turn_badge = tk.Label(header, text="YOUR TURN", font=("Arial", 10, "bold"), fg="#08100c", bg="#55e6a5", padx=16, pady=7)
        self.turn_badge.pack(side=tk.RIGHT, padx=24, pady=12)

        # Command deck sits at a stable height so it cannot clip the status cards.
        ui_frame = tk.Frame(self, bg="#0d111c", height=250, highlightbackground="#30394f", highlightthickness=1)
        ui_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=(0, 12))
        ui_frame.pack_propagate(False)

        # Atmospheric battle scene.
        scene_frame = tk.Canvas(self, bg=self.scene_bg, highlightthickness=0)
        scene_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=10)
        self.scene_frame = scene_frame
        scene_frame.bind("<Configure>", self._draw_arena)

        # Enemy Info (Top Left)
        enemy_frame = tk.Frame(scene_frame, bg="#141a27", highlightbackground=self.accent, highlightthickness=2)
        enemy_frame.place(relx=0.035, rely=0.06, relwidth=0.34, height=118)
        tk.Label(enemy_frame, text="TARGET", font=("Arial", 8, "bold"), fg="#8e9ab5", bg="#141a27").pack(anchor="w", padx=16, pady=(10, 0))
        self.m_name_lbl = tk.Label(enemy_frame, font=("Arial", 17, "bold"), fg=self.accent, bg="#141a27")
        self.m_name_lbl.pack(anchor="w", padx=16)
        enemy_vitals = tk.Frame(enemy_frame, bg="#141a27")
        enemy_vitals.pack(fill=tk.X, padx=16, pady=(4, 0))
        self.m_hp_lbl = tk.Label(enemy_vitals, font=("Consolas", 10, "bold"), fg="#f4f6ff", bg="#141a27")
        self.m_hp_lbl.pack(side=tk.LEFT)
        self.m_hp_percent_lbl = tk.Label(enemy_vitals, font=("Consolas", 10, "bold"), fg="#ff8c94", bg="#141a27")
        self.m_hp_percent_lbl.pack(side=tk.RIGHT)
        self.m_hp_bar = ttk.Progressbar(enemy_frame, style="Enemy.Horizontal.TProgressbar", orient="horizontal", mode="determinate")
        self.m_hp_bar.pack(fill=tk.X, padx=16, pady=(3, 10), ipady=3)
        
        # Enemy Sprite (Center Right)
        self.monster_sprite_image = None
        monster_sprite = MONSTER_SPRITES.get(self.monster_name)
        if monster_sprite:
            try:
                self.monster_sprite_image = tk.PhotoImage(file=resource_path(monster_sprite))
            except (tk.TclError, OSError):
                self.monster_sprite_image = None

        if self.monster_sprite_image:
            self.m_sprite = scene_frame.create_image(0, 0, image=self.monster_sprite_image, anchor="center", tags=("sprite", "monster_sprite"))
        else:
            sprite_text = {"Slime": "(~_~)", "Goblin": "(\\>/)", "Skeleton": "[x_x]", "Demon King Koji": "\\m/ (>_<) \\m/"}.get(self.monster_name, "???")
            self.m_sprite = scene_frame.create_text(0, 0, text=sprite_text, font=("Consolas", 60, "bold"), fill=self.accent, tags=("sprite", "monster_sprite"))
        
        # Player Info (Bottom Right)
        player_frame = tk.Frame(scene_frame, bg="#141a27", highlightbackground="#45a7ff", highlightthickness=2)
        player_frame.place(relx=0.965, rely=0.94, anchor="se", relwidth=0.355, height=154)
        player_header = tk.Frame(player_frame, bg="#141a27")
        player_header.pack(fill=tk.X, padx=16, pady=(10, 2))
        self.p_name_lbl = tk.Label(player_header, font=("Arial", 16, "bold"), fg="#f3f6ff", bg="#141a27")
        self.p_name_lbl.pack(side=tk.LEFT)
        weapon = getattr(getattr(self.player, "equipped_weapon", None), "item_name", "UNARMED")
        tk.Label(player_header, text=str(weapon).upper(), font=("Arial", 8, "bold"), fg="#8ebde8", bg="#202a3d", padx=9, pady=4).pack(side=tk.RIGHT)
        self.p_hp_lbl = tk.Label(player_frame, font=("Consolas", 10, "bold"), fg="#ff8089", bg="#141a27")
        self.p_hp_lbl.pack(anchor="w", padx=16)
        self.p_hp_bar = ttk.Progressbar(player_frame, style="PlayerHP.Horizontal.TProgressbar", orient="horizontal", mode="determinate")
        self.p_hp_bar.pack(fill=tk.X, padx=16, pady=(2, 5), ipady=3)
        self.p_mana_lbl = tk.Label(player_frame, font=("Consolas", 10, "bold"), fg="#72baff", bg="#141a27")
        self.p_mana_lbl.pack(anchor="w", padx=16)
        self.p_mana_bar = ttk.Progressbar(player_frame, style="Mana.Horizontal.TProgressbar", orient="horizontal", mode="determinate")
        self.p_mana_bar.pack(fill=tk.X, padx=16, pady=(2, 10), ipady=3)
        
        # Player Sprite (Bottom Left), based on the weapon chosen at character creation.
        self.player_sprite_image = None
        sprite_path = hero_sprite_path(self.player)
        if sprite_path:
            try:
                self.player_sprite_image = tk.PhotoImage(file=sprite_path)
            except (tk.TclError, OSError):
                self.player_sprite_image = None

        if self.player_sprite_image:
            self.p_sprite = scene_frame.create_image(0, 0, image=self.player_sprite_image, anchor="center", tags=("sprite", "player_sprite"))
        else:
            self.p_sprite = scene_frame.create_text(0, 0, text="\\o/", font=("Consolas", 50, "bold"), fill="#45a7ff", tags=("sprite", "player_sprite"))
        
        log_frame = tk.Frame(ui_frame, bg="#090c13", highlightbackground="#293149", highlightthickness=1)
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 6), pady=12)
        tk.Label(log_frame, text="COMBAT FEED", font=("Arial", 9, "bold"), fg="#8895b2", bg="#090c13").pack(anchor="w", padx=16, pady=(10, 3))
        self.battle_log = tk.Text(log_frame, state=tk.DISABLED, wrap=tk.WORD, bg="#090c13", fg="#dce3f5", font=("Consolas", 12), relief=tk.FLAT, insertbackground="white", height=6, padx=14, pady=6, spacing1=3, spacing3=5)
        self.battle_log.pack(fill=tk.BOTH, expand=True)
        self.battle_log.tag_configure("system", foreground="#aeb8d2")
        self.battle_log.tag_configure("player", foreground="#67dca5")
        self.battle_log.tag_configure("enemy", foreground="#ff7b86")
        self.battle_log.tag_configure("skill", foreground="#b994ff")
        self.battle_log.tag_configure("reward", foreground="#ffd166")
        self.append_text(f"A wild {self.monster_name} enters the arena.  HP {self.monster_hp}", "system")
        
        btn_frame = tk.Frame(ui_frame, bg="#0d111c", width=390)
        btn_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(6, 12), pady=12)
        btn_frame.pack_propagate(False)
        command_header = tk.Frame(btn_frame, bg="#0d111c")
        command_header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 7))
        tk.Label(command_header, text="COMMAND", font=("Arial", 10, "bold"), fg="#f2f5ff", bg="#0d111c").pack(side=tk.LEFT)
        tk.Label(command_header, text="A / D / I / R / S", font=("Consolas", 8, "bold"), fg="#68738d", bg="#0d111c").pack(side=tk.RIGHT)
        
        def make_action_btn(text, command, r, c, col_span=1, color="#273149", hover="#35425f"):
            btn = tk.Button(btn_frame, text=text, command=command, bg=color, fg="#f7f8ff",
                            activebackground=hover, activeforeground="#ffffff", disabledforeground="#626b80",
                            relief=tk.FLAT, bd=0, font=("Arial", 11, "bold"),
                            cursor="hand2", padx=12, pady=10)
            btn.base_color = color
            btn.hover_color = hover
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=b.hover_color) if b['state'] != tk.DISABLED else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=b.base_color) if b['state'] != tk.DISABLED else None)
            btn.grid(row=r, column=c, columnspan=col_span, sticky="nsew", padx=5, pady=5)
            return btn
            
        self.atk_btn = make_action_btn("[A]  ATTACK", self.player_attack, 1, 0, color="#9f2532", hover="#d13a48")
        self.item_btn = make_action_btn("[I]  ITEM", self.player_item, 1, 1)
        self.def_btn = make_action_btn("[D]  DEFEND", self.player_defend, 2, 0)
        self.run_btn = make_action_btn("[R]  ESCAPE", self.player_run, 2, 1)
        self.skill_btn = make_action_btn("[S]  ARCANE SKILL  •  20 MP", self.player_skill, 3, 0, 2, color="#63369a", hover="#8550c5")

        if self.is_boss:
            self.run_btn.config(text="[R]  NO ESCAPE", state=tk.DISABLED, bg="#191e2a")
        
        self.update_player_stats()
        self.update_monster_stats()
        
        btn_frame.grid_columnconfigure(0, weight=1, uniform="command")
        btn_frame.grid_columnconfigure(1, weight=1, uniform="command")
        for row in (1, 2, 3):
            btn_frame.grid_rowconfigure(row, weight=1)

        self.bind("<KeyPress-a>", lambda _event: self._invoke_if_enabled(self.atk_btn))
        self.bind("<KeyPress-i>", lambda _event: self._invoke_if_enabled(self.item_btn))
        self.bind("<KeyPress-d>", lambda _event: self._invoke_if_enabled(self.def_btn))
        self.bind("<KeyPress-r>", lambda _event: self._invoke_if_enabled(self.run_btn))
        self.bind("<KeyPress-s>", lambda _event: self._invoke_if_enabled(self.skill_btn))
        self.focus_set()
        
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        play_bgm(True)
        self._start_idle_animation()
        self.wait_window(self)

    def _configure_battle_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Enemy.Horizontal.TProgressbar", troughcolor="#252b39", background=self.accent, bordercolor="#252b39", lightcolor=self.accent, darkcolor=self.accent, thickness=10)
        style.configure("PlayerHP.Horizontal.TProgressbar", troughcolor="#252b39", background="#ff4f5e", bordercolor="#252b39", lightcolor="#ff4f5e", darkcolor="#ff4f5e", thickness=10)
        style.configure("Mana.Horizontal.TProgressbar", troughcolor="#252b39", background="#3e9eff", bordercolor="#252b39", lightcolor="#3e9eff", darkcolor="#3e9eff", thickness=10)

    def _draw_arena(self, event):
        canvas = self.scene_frame
        canvas.delete("arena")
        width, height = event.width, event.height
        self._scene_width = width
        self._scene_height = height
        canvas.create_rectangle(0, int(height * 0.58), width, height, fill="#0c1320", outline="", tags="arena")
        canvas.create_line(0, int(height * 0.58), width, int(height * 0.58), fill="#26314a", width=2, tags="arena")
        for index in range(1, 7):
            y = int(height * 0.58 + (height * 0.42 * index / 7))
            inset = int(width * 0.04 * index)
            canvas.create_line(inset, y, width - inset, y, fill="#151e30", tags="arena")
        for x_ratio in (0.08, 0.20, 0.34, 0.66, 0.80, 0.92):
            x = int(width * x_ratio)
            canvas.create_line(width // 2, int(height * 0.58), x, height, fill="#111a2a", tags="arena")
        canvas.create_oval(int(width * 0.64), int(height * 0.47), int(width * 0.88), int(height * 0.60), fill="#11192a", outline="#2a3652", tags="arena")
        canvas.create_oval(int(width * 0.10), int(height * 0.80), int(width * 0.37), int(height * 0.94), fill="#11192a", outline="#2a3652", tags="arena")
        for x_ratio, y_ratio, size in ((.45, .16, 2), (.52, .30, 1), (.89, .12, 2), (.43, .48, 1), (.57, .10, 1)):
            x, y = int(width * x_ratio), int(height * y_ratio)
            canvas.create_oval(x, y, x + size, y + size, fill="#536384", outline="", tags="arena")
        canvas.tag_lower("arena")
        if hasattr(self, "p_sprite") and hasattr(self, "m_sprite"):
            self._position_sprites()
            canvas.tag_raise("sprite")

    def _position_sprites(self):
        player_x = self._scene_width * 0.23 + self._sprite_hit_shift["player"]
        player_y = self._scene_height * (0.66 + self._idle_offset)
        monster_x = self._scene_width * 0.76 + self._sprite_hit_shift["monster"]
        monster_y = self._scene_height * (0.30 - self._idle_offset)
        self.scene_frame.coords(self.p_sprite, player_x, player_y)
        self.scene_frame.coords(self.m_sprite, monster_x, monster_y)

    def _invoke_if_enabled(self, button):
        if str(button["state"]) != str(tk.DISABLED):
            button.invoke()

    def _start_idle_animation(self):
        self._idle_phase = getattr(self, "_idle_phase", 0) + 1
        self._idle_offset = 0.008 if self._idle_phase % 2 else 0
        if self.winfo_exists():
            self._position_sprites()
            self._animation_jobs.append(self.after(420, self._start_idle_animation))

    def _animate_hit(self, target, damage, color="#ff5967"):
        sprite = self.m_sprite if target == "monster" else self.p_sprite
        self._sprite_hit_shift[target] = -18 if target == "monster" else 18
        self._position_sprites()
        x, y = self.scene_frame.coords(sprite)
        impact_ring = self.scene_frame.create_oval(
            x - 55, y - 55, x + 55, y + 55,
            outline=color, width=2, tags="effect"
        )
        self.scene_frame.tag_lower(impact_ring, sprite)

        def restore():
            if self.winfo_exists():
                self._sprite_hit_shift[target] = 0
                self._position_sprites()
                self.scene_frame.delete(impact_ring)

        self._animation_jobs.append(self.after(110, restore))
        self._show_floating_text(f"-{max(0, int(damage))}", target, color)

    def _show_floating_text(self, text, target, color):
        start_x, start_y = ((0.76, 0.16) if target == "monster" else (0.23, 0.51))
        text_item = self.scene_frame.create_text(
            self._scene_width * start_x,
            self._scene_height * start_y,
            text=text,
            font=("Arial", 18, "bold"),
            fill=color,
            tags="effect"
        )

        def rise(step=0):
            if step >= 8:
                self.scene_frame.delete(text_item)
                return
            self.scene_frame.move(text_item, 0, -4)
            self._animation_jobs.append(self.after(45, lambda: rise(step + 1)))

        rise()

    def destroy(self):
        play_bgm(False)
        for job in self._animation_jobs:
            try:
                self.after_cancel(job)
            except (tk.TclError, ValueError):
                pass
        self._animation_jobs.clear()
        super().destroy()

    def update_player_stats(self):
        visible_hp = max(0, self.player.hp)
        self.p_name_lbl.config(text=f"{self.player.name}  •  LV {self.player.level}")
        self.p_hp_lbl.config(text=f"HP   {visible_hp} / {self.player.max_hp}")
        self.p_hp_bar['maximum'] = self.player.max_hp
        self.p_hp_bar['value'] = visible_hp
        self.p_mana_lbl.config(text=f"MP   {self.player.mana} / 100")
        self.p_mana_bar['maximum'] = 100
        self.p_mana_bar['value'] = self.player.mana
        
        # Dynamic Buttons
        can_skill = self.player.mana >= 20
        self.skill_btn.config(state=tk.NORMAL if can_skill else tk.DISABLED, bg=self.skill_btn.base_color if can_skill else "#191e2a")
        
        consumables = [item for item in self.player.inventory if getattr(item, 'is_consumable', False)]
        can_item = len(consumables) > 0
        self.item_btn.config(state=tk.NORMAL if can_item else tk.DISABLED, bg=self.item_btn.base_color if can_item else "#191e2a")

    def update_monster_stats(self):
        self.m_name_lbl.config(text=self.monster_name)
        visible_hp = max(0, self.monster_hp)
        hp_percent = int(visible_hp / self.monster_max_hp * 100)
        self.m_hp_lbl.config(text=f"HP   {visible_hp} / {self.monster_max_hp}")
        self.m_hp_percent_lbl.config(text=f"{hp_percent}%")
        self.m_hp_bar['maximum'] = self.monster_max_hp
        self.m_hp_bar['value'] = visible_hp

    def append_text(self, text, kind="system"):
        self.battle_log.config(state=tk.NORMAL)
        self.battle_log.insert(tk.END, "› ", "system")
        self.battle_log.insert(tk.END, text + "\n", kind)
        self.battle_log.see(tk.END)
        self.battle_log.config(state=tk.DISABLED)

    def player_attack(self):
        play_sound("attack")
        weapon_dmg = self.player.equipped_weapon.additional_damage if getattr(self.player, 'equipped_weapon', None) else 0
        damage = 15 + (self.player.level * 5) + int(weapon_dmg) + random.randint(0, 9)
        self.monster_hp -= damage
        self._animate_hit("monster", damage)
        self.append_text(f"You strike {self.monster_name} for {damage} damage.", "player")
        self.update_monster_stats()
        
        if self.monster_hp <= 0:
            self.append_text(f"{self.monster_name} has been defeated!", "reward")
            self.reward_player()
            self.destroy()
            return
            
        self.monster_turn()

    def player_defend(self):
        self.append_text("You take a guarded stance.", "player")
        play_sound("damage")
        armor_def = self.player.equipped_armor.defense_bonus if getattr(self.player, 'equipped_armor', None) else 0
        reduced = max(0, self.monster_attack - random.randint(0, 4) - 5 - int(armor_def))
        self.player.hp -= reduced
        self._animate_hit("player", reduced)
        self.append_text(f"{self.monster_name} attacks, but your guard reduces it to {reduced} damage.", "enemy")
        self.update_player_stats()
        
        if self.player.hp <= 0:
            self.player_defeated()

    def player_skill(self):
        if self.player.mana >= 20:
            play_sound("skill")
            skill_dmg = 40 + random.randint(0, 19)
            self.player.use_mana(20)
            self.monster_hp -= skill_dmg
            self._animate_hit("monster", skill_dmg, "#c69cff")
            self.append_text(f"Arcane energy erupts for {skill_dmg} damage!", "skill")
            self.update_monster_stats()
            self.update_player_stats()
            
            if self.monster_hp <= 0:
                self.append_text(f"{self.monster_name} has been defeated!", "reward")
                self.reward_player()
                self.destroy()
                return
        else:
            self.append_text("Not enough MP to channel the skill.", "enemy")
            return
            
        self.monster_turn()

    def player_run(self):
        if random.randint(0, 99) < 50:
            self.append_text(f"You escape from {self.monster_name}.", "player")
            self.destroy()
        else:
            self.append_text("Escape failed!", "enemy")
            self.monster_turn()

    def player_item(self):
        consumables = [item for item in self.player.inventory if getattr(item, 'is_consumable', False)]
        if not consumables:
            self.append_text("There are no usable items in your pack.", "enemy")
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
                self._show_floating_text(f"+{used_item.heal_amount}", "player", "#67dca5")
                self.append_text(f"{used_item.item_name} restores {used_item.heal_amount} HP.", "player")
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
        self._animate_hit("player", taken)
        self.append_text(f"{self.monster_name} hits you for {taken} damage.", "enemy")
        self.update_player_stats()
        
        if self.player.hp <= 0:
            self.player_defeated()

    def player_defeated(self):
        self.append_text(f"You were defeated by {self.monster_name}.", "enemy")
        messagebox.showinfo("Game Over!", "You have been defeated!")
        sys.exit(0)

    def reward_player(self):
        exp = random.randint(20, 49)
        coins = random.randint(10, 29)
        previous_level = self.player.level
        self.player.add_experience(exp)
        self.player.add_coins(coins)

        dropped_item = None
        if not self.is_boss and random.randint(0, 99) < 30:
            loot_pool = [
                Item("Rusty Dagger", "Basic", 8.0),
                Item("Bone Club", "Crude", 11.0),
                Item("Slime Sword", "Sticky", 13.0)
            ]
            dropped_item = random.choice(loot_pool)
            self.player.inventory.append(dropped_item)

        VictoryScreen(
            self,
            self.player,
            self.monster_name,
            exp,
            coins,
            loot=dropped_item,
            leveled_up=self.player.level > previous_level,
        )
