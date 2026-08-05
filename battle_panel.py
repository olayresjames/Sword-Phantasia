import tkinter as tk
from tkinter import ttk
import random
import sys
import os
from character import experience_to_next_level
from audio_manager import audio_manager
from game_data import COMBAT, difficulty_profile, scale_enemy_stats, scale_player_damage, scale_rewards
from game_settings import apply_display_mode, key_sequence, settings
from loot_data import RARITY_COLORS, miniboss_loot, reward_ranges, roll_region_loot
from quests import record_defeat, record_event
from skills import all_skills, class_name, mastery_multiplier, mastery_rank, newly_reached_mastery, newly_unlocked_skills, unlocked_skills
from world_data import DEMON_KING, choose_enemy_intent, choose_monster, current_region

HERO_SPRITES = {
    "sword": "assets/hero-sprites/sword.png",
    "bow": "assets/hero-sprites/bow.png",
    "axe": "assets/hero-sprites/axe.png",
}

MONSTER_SPRITES = {
    "Slime": "assets/monster-sprites/slime.png",
    "Verdant Slime": "assets/monster-sprites/verdant-slime.png",
    "King Slime": "assets/monster-sprites/king-slime.png",
    "Prismatic Slime": "assets/monster-sprites/prismatic-slime.png",
    "Tideborn Slime": "assets/monster-sprites/tideborn-slime.png",
    "Goblin": "assets/monster-sprites/goblin.png",
    "Goblin Scout": "assets/monster-sprites/goblin-scout.png",
    "Goblin Warchief": "assets/monster-sprites/goblin-warchief.png",
    "Bloodmoon Raider": "assets/monster-sprites/bloodmoon-raider.png",
    "Elder Warchief": "assets/monster-sprites/elder-warchief.png",
    "Skeleton": "assets/monster-sprites/skeleton.png",
    "Crypt Archer": "assets/monster-sprites/crypt-archer.png",
    "Bone Warden": "assets/monster-sprites/bone-warden.png",
    "Gravebound Champion": "assets/monster-sprites/gravebound-champion.png",
    "Deathless Warden": "assets/monster-sprites/deathless-warden.png",
    "Abyss Stalker": "assets/monster-sprites/abyss-stalker.png",
    "Hellfire Knight": "assets/monster-sprites/hellfire-knight.png",
    "Void Herald": "assets/monster-sprites/void-herald.png",
    "Demon King Koji": "assets/monster-sprites/demon-king-koji.png",
    "Tideheart Behemoth": "assets/monster-sprites/tideheart-behemoth.png",
    "Thornlord Grak": "assets/monster-sprites/thornlord-grak.png",
    "Ashen Bonewyrm": "assets/monster-sprites/ashen-bonewyrm.png",
}

REGION_BACKGROUNDS = {
    "frontier": "assets/environments/frontier.png",
    "mosswood": "assets/environments/mosswood.png",
    "crypt": "assets/environments/crypt.png",
    "throne": "assets/environments/throne.png",
}

CRITICAL_CHANCE = COMBAT["critical_chance"]
CRITICAL_MULTIPLIER = COMBAT["critical_multiplier"]
DEFEND_MP_RECOVERY = COMBAT["defend_mp_recovery"]
HEAVY_DEFEND_BONUS_MP = COMBAT["heavy_defend_bonus_mp"]
DEFEND_DAMAGE_MULTIPLIER = COMBAT["defend_damage_multiplier"]
OPENING_DAMAGE_BONUS = COMBAT["opening_damage_bonus"]
HEAVY_INTENT_THRESHOLD = COMBAT["heavy_intent_threshold"]

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

def play_sound(action):
    audio_manager.play_sound(action)


def play_bgm(start=True):
    if start:
        audio_manager.play_music("battle")
    else:
        audio_manager.stop_music()


class VictoryScreen(tk.Toplevel):
    """JRPG-inspired battle results screen."""

    def __init__(self, parent, player, monster_name, exp, coins, loot=None, leveled_up=False, new_skills=(), new_mastery_rank=None, quest_updates=(), quest_completions=()):
        super().__init__(parent)
        self.player = player
        self.is_final_victory = monster_name == "Demon King Koji"
        self._animation_jobs = []
        self._particles = []
        self.title("Victory!")
        self.resizable(False, False)
        self.configure(bg="#080b13")
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        apply_display_mode(self)

        banner_host = tk.Canvas(self, height=205, bg="#0c1120", highlightthickness=0)
        banner_host.pack(fill=tk.X)
        banner = tk.Canvas(banner_host, width=900, height=205, bg="#0c1120", highlightthickness=0)
        banner_window = banner_host.create_window(450, 0, window=banner, anchor="n")
        banner_host.bind("<Configure>", lambda event: banner_host.coords(banner_window, event.width / 2, 0))
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
        banner.create_text(450, 134, text=f"{class_name(player).upper()}  •  BATTLE RESULTS", font=("Arial", 9, "bold"), fill="#77839f")

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
        rarity = getattr(loot, "rarity", "Common") if loot else None
        loot_name = f"{rarity.upper()}  •  {loot.item_name}" if loot else "No item dropped"
        loot_color = RARITY_COLORS.get(rarity, "#c49cff") if loot else "#68738c"
        self._reward_row(results, "TREASURE", loot_name, loot_color)
        if new_skills:
            names = ", ".join(skill.name for skill in new_skills)
            self._reward_row(results, "NEW SKILL", names, "#c49cff")
        if new_mastery_rank:
            self._reward_row(results, "CLASS MASTERY", f"RANK {new_mastery_rank}", "#ffd166")
        if quest_completions:
            names = ", ".join(quest.title for quest, _item in quest_completions)
            self._reward_row(results, "QUEST COMPLETE", names, "#67dca5")

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
        xp_required = experience_to_next_level(player.level)
        tk.Label(xp_header, text=f"{player.experience} / {xp_required} EXP", font=("Consolas", 9, "bold"), fg="#dce3f4", bg="#111724").pack(side=tk.RIGHT)
        xp_bar = ttk.Progressbar(progress, style="VictoryXP.Horizontal.TProgressbar", maximum=xp_required, value=player.experience)
        xp_bar.pack(fill=tk.X, padx=22, pady=(7, 22), ipady=3)

        if self.is_final_victory:
            status_text = "Demon King Koji is no more. The realm is free."
        elif leveled_up:
            status_text = "Your strength has reached a new height."
        else:
            status_text = "The journey continues."
        tk.Label(progress, text=status_text, wraplength=275, justify=tk.LEFT, font=("Arial", 10), fg="#9ca7bd", bg="#111724").pack(anchor="w", padx=22)
        if quest_updates:
            quest, current = quest_updates[-1]
            tk.Label(progress, text=f"QUEST  •  {quest.title}\n{current} / {quest.required}", justify=tk.LEFT, font=("Arial", 9, "bold"), fg="#67dca5", bg="#111724").pack(anchor="w", padx=22, pady=(14, 0))

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

        if settings.get("reduce_animations"):
            self.exp_reward_lbl.config(text=f"+{exp} EXP")
            self.coin_reward_lbl.config(text=f"+{coins} G")
        else:
            self._create_particles()
            self._animate_particles()
            self._count_reward(self.exp_reward_lbl, exp, " EXP")
            self._count_reward(self.coin_reward_lbl, coins, " G")
        self.wait_window(self)

    def _reward_row(self, parent, title, value, color):
        row = tk.Frame(parent, bg="#171e2d", height=45)
        row.pack(fill=tk.X, padx=18, pady=2)
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
        self._animation_jobs.append(self.after(settings.delay(45), self._animate_particles))

    def _count_reward(self, label, total, suffix):
        steps = min(24, max(1, total))

        def update(step=0):
            if not label.winfo_exists():
                return
            value = total if step >= steps else int(total * step / steps)
            label.config(text=f"+{value}{suffix}")
            if step < steps:
                self._animation_jobs.append(self.after(settings.delay(28), lambda: update(step + 1)))

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


class DefeatScreen(tk.Toplevel):
    """Choose a recoverable outcome instead of terminating the process."""

    def __init__(self, parent, player, monster_name):
        super().__init__(parent)
        self.result = "camp"
        self.title("Defeated")
        self.resizable(False, False)
        self.configure(bg="#080b13")
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", lambda: self._choose("camp"))
        apply_display_mode(self)

        header = tk.Frame(self, bg="#241119", height=120, highlightbackground="#6d2938", highlightthickness=1)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="FALLEN — NOT FORGOTTEN", font=("Georgia", 26, "bold"), fg="#ff7180", bg="#241119").pack(pady=(25, 5))
        tk.Label(header, text=f"{monster_name.upper()} ENDED THIS ATTEMPT", font=("Arial", 9, "bold"), fg="#c99aa3", bg="#241119").pack()

        body_host = tk.Frame(self, bg="#080b13")
        body_host.pack(fill=tk.BOTH, expand=True)
        body = tk.Frame(body_host, bg="#080b13", width=760, height=500)
        body.place(relx=.5, rely=.5, anchor="center")
        body.pack_propagate(False)
        tk.Label(body, text="Choose how the journey continues.", font=("Arial", 11), fg="#c8d0e1", bg="#080b13").pack(pady=(0, 16))

        options = (
            ("RETRY ENCOUNTER", "Restore HP and MP, then face the same enemy again.", "retry", "#8f2f3e"),
            ("RETURN TO CAMP", f"Lose {int(difficulty_profile(settings.get('difficulty'))['defeat_gold_loss'] * 100)}% gold and recover to 50% HP and at least 40 MP.", "camp", "#725728"),
            ("LOAD LAST SAVE", "Discard progress since the most recent save.", "load", "#274f73"),
            ("RETURN TO TITLE", "Leave the current run without closing the game.", "title", "#343b4d"),
        )
        for title, description, result, color in options:
            row = tk.Frame(body, bg="#121925", highlightbackground="#29364d", highlightthickness=1)
            row.pack(fill=tk.X, pady=4)
            tk.Button(row, text=title, command=lambda choice=result: self._choose(choice), width=20, bg=color, fg="#ffffff", activebackground="#52617a", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Arial", 9, "bold"), cursor="hand2", pady=10).pack(side=tk.LEFT)
            tk.Label(row, text=description, wraplength=330, justify=tk.LEFT, font=("Arial", 9), fg="#aeb8cc", bg="#121925").pack(side=tk.LEFT, padx=14)

        self.focus_set()
        self.wait_window(self)

    def _choose(self, result):
        self.result = result
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()


class BattlePanel(tk.Toplevel):
    def __init__(self, parent, player, is_boss=False, monster_spec=None, is_miniboss=False):
        super().__init__(parent)
        self.player = player
        self.difficulty = settings.get("difficulty")
        self.is_boss = is_boss
        self.is_miniboss = is_miniboss
        self._animation_jobs = []
        self.accent = "#b26cff" if is_boss else "#ffd166" if is_miniboss else "#ff4d5a"
        self.scene_bg = "#090d16"
        self._scene_width = 1
        self._scene_height = 1
        self._idle_offset = 0
        self._sprite_hit_shift = {"player": 0, "monster": 0}
        self.skill_guard_bonus = 0
        self.evade_next_attack = False
        self.next_attack_bonus = 0
        self.enemy_weaken = 0
        self.defended_this_battle = False
        self.turn_state = "player"
        self.victory = False
        self.defeated = False
        self.retry_requested = False
        self.load_requested = False
        self.title_requested = False
        self.defeat_penalty = 0
        self.enemy_guard_fraction = 0.0
        self.skill_cooldowns = {}
        self.boss_phase = 1
        
        self.title("Final Battle!" if is_boss else "Region Champion!" if is_miniboss else "Battle!")
        self.geometry("1100x720")
        self.minsize(900, 680)
        self.configure(bg="#070910")
        self.grab_set()
        apply_display_mode(self)
        
        self.monster_spec = DEMON_KING if self.is_boss else (monster_spec or choose_monster(self.player))
        self.monster_name = self.monster_spec.name
        self.monster_family = self.monster_spec.family
        self.monster_sprite_key = self.monster_spec.sprite_key
        region = current_region(self.player)
        region_level_bonus = max(0, self.player.level - region.unlock_level)
        base_hp = random.randint(*self.monster_spec.hp_range) + region_level_bonus * 7
        base_attack = random.randint(*self.monster_spec.attack_range) + region_level_bonus
        self.monster_max_hp, self.monster_attack = scale_enemy_stats(base_hp, base_attack, self.difficulty)
        self.monster_hp = self.monster_max_hp
        self.enemy_intent = choose_enemy_intent(self.monster_family, 1.0)
            
        self._configure_battle_styles()

        # Arena header
        header = tk.Frame(self, bg="#111624", height=58, highlightbackground="#293149", highlightthickness=1)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="⚔  BATTLE ARENA", font=("Arial", 16, "bold"), fg="#f3f5ff", bg="#111624").pack(side=tk.LEFT, padx=24)
        encounter_text = "FINAL ENCOUNTER  •  PRIMORDIAL THRONE" if is_boss else "REGION CHAMPION" if is_miniboss else "ASCENDED ENCOUNTER  •  RARE LOOT" if self.monster_spec.elite else f"WILD ENCOUNTER  •  {region.name.upper()}"
        tk.Label(header, text=encounter_text, font=("Arial", 10, "bold"), fg=self.accent, bg="#111624").pack(side=tk.LEFT, padx=12)
        self.turn_badge = tk.Label(header, text="YOUR TURN", font=("Arial", 10, "bold"), fg="#08100c", bg="#55e6a5", padx=16, pady=7)
        self.turn_badge.pack(side=tk.RIGHT, padx=24, pady=12)

        # Keep the command deck compact so the arena remains the visual focus.
        ui_frame = tk.Frame(self, bg="#0d111c", height=218, highlightbackground="#30394f", highlightthickness=1)
        ui_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=(0, 12))
        ui_frame.pack_propagate(False)

        # Atmospheric battle scene.
        scene_frame = tk.Canvas(self, bg=self.scene_bg, highlightthickness=0)
        scene_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=10)
        self.scene_frame = scene_frame
        self.arena_background = None
        try:
            self.arena_background = tk.PhotoImage(file=resource_path(REGION_BACKGROUNDS[region.key]))
        except (tk.TclError, OSError, KeyError):
            pass
        self.arena_background_item = scene_frame.create_image(0, 0, image=self.arena_background or "", anchor="center", tags="backdrop")
        scene_frame.bind("<Configure>", self._draw_arena)

        # Enemy Info (Top Left)
        enemy_frame = tk.Frame(scene_frame, bg="#141a27", highlightbackground=self.accent, highlightthickness=2)
        enemy_frame.place(relx=0.035, rely=0.055, relwidth=0.305, height=126)
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
        self.m_hp_bar.pack(fill=tk.X, padx=16, pady=(3, 4), ipady=3)
        self.m_intent_lbl = tk.Label(enemy_frame, font=("Segoe UI", 9, "bold"), fg="#ffd166", bg="#141a27")
        self.m_intent_lbl.pack(anchor="w", padx=16, pady=(0, 7))
        
        # Enemy Sprite (Center Right)
        self.monster_sprite_image = None
        monster_sprite = MONSTER_SPRITES.get(self.monster_sprite_key)
        if monster_sprite:
            try:
                self.monster_sprite_image = tk.PhotoImage(file=resource_path(monster_sprite)).zoom(3, 3).subsample(2, 2)
            except (tk.TclError, OSError):
                self.monster_sprite_image = None

        if self.monster_sprite_image:
            self.m_sprite = scene_frame.create_image(0, 0, image=self.monster_sprite_image, anchor="center", tags=("sprite", "monster_sprite"))
        else:
            sprite_text = {"Slime": "(~_~)", "Goblin": "(\\>/)", "Skeleton": "[x_x]", "Demon King Koji": "\\m/ (>_<) \\m/"}.get(self.monster_sprite_key, "???")
            self.m_sprite = scene_frame.create_text(0, 0, text=sprite_text, font=("Consolas", 60, "bold"), fill=self.accent, tags=("sprite", "monster_sprite"))
        
        # Player Info (Bottom Right)
        player_frame = tk.Frame(scene_frame, bg="#141a27", highlightbackground="#45a7ff", highlightthickness=2)
        player_frame.place(relx=0.965, rely=0.945, anchor="se", relwidth=0.315, height=140)
        player_header = tk.Frame(player_frame, bg="#141a27")
        player_header.pack(fill=tk.X, padx=16, pady=(10, 2))
        self.p_name_lbl = tk.Label(player_header, font=("Arial", 16, "bold"), fg="#f3f6ff", bg="#141a27")
        self.p_name_lbl.pack(side=tk.LEFT)
        weapon = getattr(getattr(self.player, "equipped_weapon", None), "item_name", "UNARMED")
        tk.Label(player_header, text=str(weapon).upper(), font=("Arial", 8, "bold"), fg="#8ebde8", bg="#202a3d", padx=9, pady=4).pack(side=tk.RIGHT)
        self.p_class_lbl = tk.Label(player_frame, font=("Arial", 8, "bold"), fg="#b994ff", bg="#141a27")
        self.p_class_lbl.pack(anchor="w", padx=16)
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
                self.player_sprite_image = tk.PhotoImage(file=sprite_path).zoom(3, 3).subsample(2, 2)
            except (tk.TclError, OSError):
                self.player_sprite_image = None

        if self.player_sprite_image:
            self.p_sprite = scene_frame.create_image(0, 0, image=self.player_sprite_image, anchor="center", tags=("sprite", "player_sprite"))
        else:
            self.p_sprite = scene_frame.create_text(0, 0, text="\\o/", font=("Consolas", 50, "bold"), fill="#45a7ff", tags=("sprite", "player_sprite"))
        
        log_frame = tk.Frame(ui_frame, bg="#090c13", highlightbackground="#293149", highlightthickness=1)
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 6), pady=12)
        tk.Label(log_frame, text="COMBAT FEED", font=("Arial", 9, "bold"), fg="#8895b2", bg="#090c13").pack(anchor="w", padx=16, pady=(10, 3))
        self.battle_log = tk.Text(log_frame, state=tk.DISABLED, wrap=tk.WORD, bg="#090c13", fg="#dce3f5", font=("Consolas", 11), relief=tk.FLAT, insertbackground="white", height=5, padx=14, pady=6, spacing1=2, spacing3=4)
        self.battle_log.pack(fill=tk.BOTH, expand=True)
        self.battle_log.tag_configure("system", foreground="#aeb8d2")
        self.battle_log.tag_configure("player", foreground="#67dca5")
        self.battle_log.tag_configure("enemy", foreground="#ff7b86")
        self.battle_log.tag_configure("skill", foreground="#b994ff")
        self.battle_log.tag_configure("reward", foreground="#ffd166")
        self.append_text(f"A wild {self.monster_name} enters the arena.  HP {self.monster_hp}", "system")
        if self.monster_spec.elite:
            self.append_text("ASCENDED FOE: increased strength, EXP, gold, and treasure chance.", "reward")
        self.append_text("Skills exploit heavy attacks; Defend restores MP.", "system")
        
        btn_frame = tk.Frame(ui_frame, bg="#0d111c", width=390)
        btn_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(6, 12), pady=12)
        btn_frame.pack_propagate(False)
        command_header = tk.Frame(btn_frame, bg="#0d111c")
        command_header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 7))
        tk.Label(command_header, text="COMMAND", font=("Arial", 10, "bold"), fg="#f2f5ff", bg="#0d111c").pack(side=tk.LEFT)
        battle_keys = " / ".join(settings.key(action).upper() for action in ("battle_attack", "battle_defend", "battle_item", "battle_escape", "battle_skill"))
        tk.Label(command_header, text=battle_keys, font=("Consolas", 8, "bold"), fg="#68738d", bg="#0d111c").pack(side=tk.RIGHT)
        
        def make_action_btn(text, command, r, c, col_span=1, color="#273149", hover="#35425f"):
            btn = tk.Button(btn_frame, text=text, command=command, bg=color, fg="#f7f8ff",
                            activebackground=hover, activeforeground="#ffffff", disabledforeground="#626b80",
                            relief=tk.FLAT, bd=0, font=("Segoe UI", 11, "bold"),
                            cursor="hand2", padx=12, pady=10, highlightthickness=2,
                            highlightbackground=color, highlightcolor="#ffd166")
            btn.base_color = color
            btn.hover_color = hover
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=b.hover_color) if b['state'] != tk.DISABLED else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=b.base_color) if b['state'] != tk.DISABLED else None)
            btn.grid(row=r, column=c, columnspan=col_span, sticky="nsew", padx=5, pady=5)
            return btn
            
        self.atk_btn = make_action_btn(f"[{settings.key('battle_attack').upper()}]  ATTACK", self.player_attack, 1, 0, color="#9f2532", hover="#d13a48")
        self.item_btn = make_action_btn(f"[{settings.key('battle_item').upper()}]  ITEM", self.player_item, 1, 1)
        self.def_btn = make_action_btn(f"[{settings.key('battle_defend').upper()}]  DEFEND", self.player_defend, 2, 0)
        self.run_btn = make_action_btn(f"[{settings.key('battle_escape').upper()}]  ESCAPE", self.player_run, 2, 1)
        self.skill_btn = make_action_btn(f"[{settings.key('battle_skill').upper()}]  CLASS SKILLS", self.player_skill, 3, 0, 2, color="#63369a", hover="#8550c5")
        self.action_buttons = (self.atk_btn, self.item_btn, self.def_btn, self.run_btn, self.skill_btn)

        if self.is_boss or self.is_miniboss:
            self.run_btn.config(text=f"[{settings.key('battle_escape').upper()}]  NO ESCAPE", state=tk.DISABLED, bg="#191e2a")
        
        self.update_player_stats()
        self.update_monster_stats()
        
        btn_frame.grid_columnconfigure(0, weight=1, uniform="command")
        btn_frame.grid_columnconfigure(1, weight=1, uniform="command")
        for row in (1, 2, 3):
            btn_frame.grid_rowconfigure(row, weight=1)

        for action, button in (
            ("battle_attack", self.atk_btn), ("battle_item", self.item_btn),
            ("battle_defend", self.def_btn), ("battle_escape", self.run_btn),
            ("battle_skill", self.skill_btn),
        ):
            self.bind(key_sequence(settings.key(action)), lambda _event, target=button: self._invoke_if_enabled(target))
        self.focus_set()
        
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        audio_manager.configure(settings.get("music_volume"), settings.get("sfx_volume"))
        play_bgm(True)
        if not settings.get("reduce_animations"):
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
        canvas.coords(self.arena_background_item, width // 2, height // 2)
        canvas.create_rectangle(0, 0, width, height, fill="#070a11", outline="", stipple="gray75", tags="arena")
        canvas.create_line(0, int(height * .72), width, int(height * .72), fill="#59627a", width=1, tags="arena")
        canvas.create_oval(int(width * 0.63), int(height * 0.46), int(width * 0.90), int(height * 0.64), fill="#10131c", outline="#697189", stipple="gray50", tags="arena")
        canvas.create_oval(int(width * 0.08), int(height * 0.75), int(width * 0.38), int(height * 0.96), fill="#10131c", outline="#506079", stipple="gray50", tags="arena")
        canvas.tag_lower("backdrop")
        canvas.tag_raise("arena", "backdrop")
        if hasattr(self, "p_sprite") and hasattr(self, "m_sprite"):
            self._position_sprites()
            canvas.tag_raise("sprite")

    def _position_sprites(self):
        player_x = self._scene_width * 0.245 + self._sprite_hit_shift["player"]
        player_y = self._scene_height * (0.69 + self._idle_offset)
        monster_x = self._scene_width * 0.755 + self._sprite_hit_shift["monster"]
        monster_y = self._scene_height * (0.31 - self._idle_offset)
        self.scene_frame.coords(self.p_sprite, player_x, player_y)
        self.scene_frame.coords(self.m_sprite, monster_x, monster_y)

    def _invoke_if_enabled(self, button):
        if str(button["state"]) != str(tk.DISABLED):
            button.invoke()

    def _delay(self, milliseconds):
        return settings.delay(milliseconds)

    def _start_idle_animation(self):
        self._idle_phase = getattr(self, "_idle_phase", 0) + 1
        self._idle_offset = 0.008 if self._idle_phase % 2 else 0
        if self.winfo_exists():
            self._position_sprites()
            self._animation_jobs.append(self.after(self._delay(420), self._start_idle_animation))

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
        slash_items = []
        for offset in (-18, 0, 18):
            slash_items.append(self.scene_frame.create_line(
                x - 46 + offset, y + 40, x + 34 + offset, y - 42,
                fill="#fff0bd", width=4, tags="effect"
            ))
        spark_items = []
        for dx, dy in ((-58, -8), (52, -22), (-36, 48), (45, 38), (0, -62)):
            spark_items.append(self.scene_frame.create_oval(
                x + dx - 3, y + dy - 3, x + dx + 3, y + dy + 3,
                fill=color, outline="", tags="effect"
            ))

        def restore():
            if self.winfo_exists():
                self._sprite_hit_shift[target] = 0
                self._position_sprites()
                self.scene_frame.delete(impact_ring)
                for item in slash_items + spark_items:
                    self.scene_frame.delete(item)

        self._animation_jobs.append(self.after(self._delay(110), restore))
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
            self._animation_jobs.append(self.after(self._delay(45), lambda: rise(step + 1)))

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
        self.p_class_lbl.config(text=class_name(self.player).upper())
        self.p_hp_lbl.config(text=f"HP   {visible_hp} / {self.player.max_hp}")
        self.p_hp_bar['maximum'] = self.player.max_hp
        self._tween_bar(self.p_hp_bar, visible_hp)
        self.p_mana_lbl.config(text=f"MP   {self.player.mana} / 100")
        self.p_mana_bar['maximum'] = 100
        self._tween_bar(self.p_mana_bar, self.player.mana)
        
        # Dynamic Buttons
        player_can_act = self.turn_state == "player"
        can_cast = any(
            skill.mp_cost <= self.player.mana and self._skill_cooldown(skill) == 0
            for skill in unlocked_skills(self.player)
        )
        self.skill_btn.base_color = "#63369a" if can_cast else "#332741"
        self.skill_btn.config(
            state=tk.NORMAL if player_can_act else tk.DISABLED,
            text=f"[S]  {class_name(self.player).upper()} SKILLS  •  {self.player.mana} MP",
            bg=self.skill_btn.base_color if player_can_act else "#191e2a",
        )
        
        consumables = [item for item in self.player.inventory if getattr(item, 'is_consumable', False)]
        can_item = len(consumables) > 0
        self.item_btn.config(state=tk.NORMAL if can_item and player_can_act else tk.DISABLED, bg=self.item_btn.base_color if can_item and player_can_act else "#191e2a")
        self.atk_btn.config(state=tk.NORMAL if player_can_act else tk.DISABLED, bg=self.atk_btn.base_color if player_can_act else "#191e2a")
        self.def_btn.config(state=tk.NORMAL if player_can_act else tk.DISABLED, bg=self.def_btn.base_color if player_can_act else "#191e2a")
        can_escape = player_can_act and not (self.is_boss or self.is_miniboss)
        self.run_btn.config(state=tk.NORMAL if can_escape else tk.DISABLED, bg=self.run_btn.base_color if can_escape else "#191e2a")
        if self.is_boss or self.is_miniboss:
            self.run_btn.config(text="[R]  NO ESCAPE")

    def _tween_bar(self, bar, target):
        """Ease progress changes so damage and healing remain readable."""
        start = float(bar["value"] or 0)
        target = float(target)
        if settings.get("reduce_animations") or abs(target - start) < 1:
            bar["value"] = target
            return

        def step(index=1):
            if not self.winfo_exists() or index > 7:
                return
            progress = index / 7
            eased = 1 - (1 - progress) ** 2
            bar["value"] = start + (target - start) * eased
            self._animation_jobs.append(self.after(self._delay(24), lambda: step(index + 1)))

        step()

    def _begin_player_action(self, label="PLAYER ACTION"):
        if self.turn_state != "player":
            return False
        self.turn_state = "resolving"
        self.turn_badge.config(text=label, bg="#ffd166", fg="#171008")
        self.update_player_stats()
        return True

    def _queue_monster_turn(self, defending=False):
        self._animation_jobs.append(self.after(self._delay(650), lambda: self.monster_turn(defending=defending)))

    def _finish_enemy_turn(self):
        if not self.winfo_exists() or self.player.hp <= 0:
            return
        self._prepare_enemy_intent()
        self._tick_skill_cooldowns()
        self.turn_state = "player"
        self.turn_badge.config(text="YOUR TURN", bg="#55e6a5", fg="#08100c")
        self.update_player_stats()

    def update_monster_stats(self):
        self.m_name_lbl.config(text=self.monster_name)
        visible_hp = max(0, self.monster_hp)
        hp_percent = int(visible_hp / self.monster_max_hp * 100)
        self.m_hp_lbl.config(text=f"HP   {visible_hp} / {self.monster_max_hp}")
        self.m_hp_percent_lbl.config(text=f"{hp_percent}%")
        self.m_hp_bar['maximum'] = self.monster_max_hp
        self._tween_bar(self.m_hp_bar, visible_hp)
        intent_colors = {"heal": "#67dca5", "guard": "#72baff", "steal": "#ffd166"}
        intent_color = intent_colors.get(self.enemy_intent.kind, "#ff8993" if self._is_heavy_intent() else "#ffd166")
        self.m_intent_lbl.config(text=f"NEXT  •  {self.enemy_intent.label.upper()}  [{self._intent_hint()}]", fg=intent_color)

    def _intent_hint(self):
        intent = self.enemy_intent
        if intent.kind == "heal":
            return "HEAL — PRESSURE IT"
        if intent.kind == "guard":
            return "GUARD — PREPARE"
        if intent.kind == "steal":
            return "STEALS GOLD"
        if intent.multiplier >= HEAVY_INTENT_THRESHOLD:
            return "HEAVY — SKILL OR DEFEND"
        return "ATTACK"

    def _is_heavy_intent(self):
        return self.enemy_intent.kind == "attack" and self.enemy_intent.multiplier >= HEAVY_INTENT_THRESHOLD

    def _skill_cooldown(self, skill):
        return self.skill_cooldowns.get(skill.name, 0)

    def _tick_skill_cooldowns(self):
        for name, turns in tuple(self.skill_cooldowns.items()):
            remaining = turns - 1
            if remaining > 0:
                self.skill_cooldowns[name] = remaining
            else:
                self.skill_cooldowns.pop(name, None)

    def _update_boss_phase(self):
        if not self.is_boss or self.monster_hp <= 0:
            return
        hp_ratio = self.monster_hp / self.monster_max_hp
        new_phase = 3 if hp_ratio <= 0.25 else 2 if hp_ratio <= 0.50 else 1
        if new_phase <= self.boss_phase:
            return
        self.boss_phase = new_phase
        if new_phase == 2:
            self.append_text("Demon King Koji enters Phase II: Hellfire Awakening!", "enemy")
        else:
            self.append_text("Demon King Koji enters Phase III: World-Ender Unbound!", "enemy")

    def append_text(self, text, kind="system"):
        self.battle_log.config(state=tk.NORMAL)
        self.battle_log.insert(tk.END, "› ", "system")
        self.battle_log.insert(tk.END, text + "\n", kind)
        self.battle_log.see(tk.END)
        self.battle_log.config(state=tk.DISABLED)

    def player_attack(self):
        if not self._begin_player_action("ATTACKING"):
            return
        play_sound("attack")
        weapon_dmg = self.player.equipped_weapon.additional_damage if getattr(self.player, 'equipped_weapon', None) else 0
        damage = 15 + (self.player.level * 5) + int(weapon_dmg) + random.randint(0, 9) + self.next_attack_bonus
        critical = random.random() < CRITICAL_CHANCE
        if critical:
            damage = int(damage * CRITICAL_MULTIPLIER)
        damage = self._apply_enemy_guard(scale_player_damage(damage, self.difficulty))
        used_bonus = self.next_attack_bonus
        self.next_attack_bonus = 0
        self.monster_hp -= damage
        self._animate_hit("monster", damage)
        critical_text = " CRITICAL!" if critical else ""
        self.append_text(f"You strike {self.monster_name} for {damage} damage.{critical_text}", "player")
        if used_bonus:
            self.append_text(f"War Cry adds {used_bonus} bonus damage.", "skill")
        self.update_monster_stats()
        self._update_boss_phase()
        
        if self.monster_hp <= 0:
            self.append_text(f"{self.monster_name} has been defeated!", "reward")
            self.reward_player()
            self.destroy()
            return
            
        self._queue_monster_turn()

    def player_defend(self):
        if not self._begin_player_action("DEFENDING"):
            return
        self.defended_this_battle = True
        recovery = DEFEND_MP_RECOVERY + (HEAVY_DEFEND_BONUS_MP if self._is_heavy_intent() else 0)
        previous_mana = self.player.mana
        self.player.mana = min(100, self.player.mana + recovery)
        restored = self.player.mana - previous_mana
        self.append_text(f"You take a guarded stance and restore {restored} MP.", "player")
        if self._is_heavy_intent():
            self.append_text("Reading the heavy attack restores 6 bonus MP.", "skill")
        self.update_player_stats()
        self._queue_monster_turn(defending=True)

    def player_skill(self):
        if self.turn_state != "player":
            return
        skill_window = tk.Toplevel(self)
        skill_window.title(f"{class_name(self.player)} Skills")
        skill_window.resizable(False, False)
        skill_window.configure(bg="#080b13")
        skill_window.transient(self)
        skill_window.grab_set()
        apply_display_mode(skill_window)

        header = tk.Frame(skill_window, bg="#111724", height=76, highlightbackground="#343e56", highlightthickness=1)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        copy = tk.Frame(header, bg="#111724")
        copy.pack(side=tk.LEFT, padx=24, pady=12)
        tk.Label(copy, text=f"{class_name(self.player).upper()} SKILL DECK", font=("Georgia", 18, "bold"), fg="#f3f5ff", bg="#111724").pack(anchor="w")
        tk.Label(copy, text=f"LEVEL {self.player.level}  •  MASTERY {mastery_rank(self.player)}  •  {self.player.mana} MP AVAILABLE", font=("Arial", 9, "bold"), fg="#b994ff", bg="#111724").pack(anchor="w")
        tk.Button(header, text="×", command=skill_window.destroy, bg="#111724", fg="#8e9ab5", activebackground="#54232c", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Segoe UI", 20), cursor="hand2", padx=18).pack(side=tk.RIGHT, padx=16, pady=8)

        body = tk.Frame(skill_window, bg="#080b13")
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        skill_list = tk.Listbox(body, bg="#0d121c", fg="#e4e8f3", selectbackground="#4c3569", selectforeground="#ffffff", font=("Consolas", 10, "bold"), relief=tk.FLAT, activestyle="none", width=34)
        skill_list.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 8))
        details = tk.Frame(body, bg="#141a27", width=320, highlightbackground="#343e56", highlightthickness=1)
        details.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        details.pack_propagate(False)
        name_lbl = tk.Label(details, text="SELECT A SKILL", wraplength=275, font=("Georgia", 18, "bold"), fg="#f3f5ff", bg="#141a27")
        name_lbl.pack(padx=20, pady=(28, 6))
        cost_lbl = tk.Label(details, text="", font=("Consolas", 10, "bold"), fg="#b994ff", bg="#141a27")
        cost_lbl.pack()
        description_lbl = tk.Label(details, text="Choose an ability to inspect it.", wraplength=270, justify=tk.LEFT, font=("Arial", 10), fg="#aab4c9", bg="#141a27")
        description_lbl.pack(padx=22, pady=20)
        cast_btn = tk.Button(details, text="SELECT SKILL", bg="#63369a", fg="#ffffff", activebackground="#8550c5", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Arial", 10, "bold"), cursor="hand2", pady=11, state=tk.DISABLED)
        cast_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)

        skills = all_skills(self.player)
        for skill in skills:
            cooldown = self._skill_cooldown(skill)
            marker = f"CD {cooldown}" if cooldown else "READY" if skill.unlock_level <= self.player.level else f"LV {skill.unlock_level}"
            skill_list.insert(tk.END, f" {marker:<6}  {skill.name}")

        def on_select(_event=None):
            selection = skill_list.curselection()
            if not selection:
                return
            skill = skills[selection[0]]
            unlocked = skill.unlock_level <= self.player.level
            affordable = skill.mp_cost <= self.player.mana
            cooldown = self._skill_cooldown(skill)
            name_lbl.config(text=skill.name)
            cost_lbl.config(text=f"LEVEL {skill.unlock_level}  •  {skill.mp_cost} MP  •  {skill.cooldown} TURN CD")
            hits = f"\n\n{skill.hits} hits" if skill.hits > 1 else ""
            multiplier = mastery_multiplier(self.player)
            rank_min = int(skill.min_damage * multiplier)
            rank_max = int(skill.max_damage * multiplier)
            damage = f"{rank_min}-{rank_max} damage per hit at Mastery {mastery_rank(self.player)}"
            description_lbl.config(text=f"{skill.description}\n\n{damage}{hits}")
            if not unlocked:
                cast_btn.config(text=f"UNLOCKS AT LEVEL {skill.unlock_level}", state=tk.DISABLED, bg="#252b37")
            elif cooldown:
                suffix = "S" if cooldown != 1 else ""
                cast_btn.config(text=f"READY IN {cooldown} TURN{suffix}", state=tk.DISABLED, bg="#252b37")
            elif not affordable:
                cast_btn.config(text="NOT ENOUGH MP", state=tk.DISABLED, bg="#252b37")
            else:
                cast_btn.config(text="USE SKILL", state=tk.NORMAL, bg="#63369a", command=lambda chosen=skill: cast(chosen))

        def cast(skill):
            skill_window.destroy()
            self.use_class_skill(skill)

        skill_list.bind("<<ListboxSelect>>", on_select)
        skill_list.bind("<Double-Button-1>", lambda _event: cast(skills[skill_list.curselection()[0]]) if skill_list.curselection() and skills[skill_list.curselection()[0]].unlock_level <= self.player.level and skills[skill_list.curselection()[0]].mp_cost <= self.player.mana and self._skill_cooldown(skills[skill_list.curselection()[0]]) == 0 else None)
        skill_window.bind("<Escape>", lambda _event: skill_window.destroy())

    def use_class_skill(self, skill):
        if skill.unlock_level > self.player.level or skill.mp_cost > self.player.mana or self._skill_cooldown(skill):
            self.append_text("That skill cannot be used right now.", "enemy")
            return
        if not self._begin_player_action(skill.name.upper()):
            return
        self.player.use_mana(skill.mp_cost)
        self.skill_cooldowns[skill.name] = skill.cooldown + 1
        play_sound("skill")
        mastery = mastery_multiplier(self.player)
        rolls = [int(random.randint(skill.min_damage, skill.max_damage) * mastery) for _ in range(skill.hits)]
        opening_exploited = self._is_heavy_intent()
        raw_damage = sum(rolls)
        if opening_exploited:
            raw_damage = int(raw_damage * OPENING_DAMAGE_BONUS)
        total_damage = self._apply_enemy_guard(scale_player_damage(raw_damage, self.difficulty))
        self.monster_hp -= total_damage
        self._animate_hit("monster", total_damage, "#c69cff")
        hit_text = f" across {skill.hits} hits" if skill.hits > 1 else ""
        self.append_text(f"{skill.name} deals {total_damage} damage{hit_text}!", "skill")
        if opening_exploited:
            self.append_text("Perfect timing! The skill exploits the heavy attack for +25% damage.", "skill")

        if skill.heal:
            previous_hp = self.player.hp
            self.player.hp = min(self.player.max_hp, self.player.hp + skill.heal)
            healed = self.player.hp - previous_hp
            self._show_floating_text(f"+{healed}", "player", "#67dca5")
            self.append_text(f"Radiant energy restores {healed} HP.", "player")
        if skill.guard:
            self.skill_guard_bonus = skill.guard
            self.append_text(f"Aegis reduces the next incoming hit by {skill.guard}.", "skill")
        if skill.evade:
            self.evade_next_attack = True
            self.append_text("Windstep prepares an automatic evade.", "skill")
        if skill.attack_bonus:
            self.next_attack_bonus = skill.attack_bonus
            self.append_text(f"War Cry empowers the next normal attack by {skill.attack_bonus}.", "skill")
        if skill.weaken:
            self.enemy_weaken = skill.weaken
            self.append_text(f"The enemy's next attack is weakened by {skill.weaken}.", "skill")

        self.update_monster_stats()
        self.update_player_stats()
        self._update_boss_phase()
        if self.monster_hp <= 0:
            self.append_text(f"{self.monster_name} has been defeated!", "reward")
            self.reward_player()
            self.destroy()
            return
        self._queue_monster_turn()

    def player_run(self):
        if not self._begin_player_action("ESCAPING"):
            return
        if random.randint(0, 99) < 50:
            self.append_text(f"You escape from {self.monster_name}.", "player")
            self.destroy()
        else:
            self.append_text("Escape failed!", "enemy")
            self._queue_monster_turn()

    def player_item(self):
        consumables = [item for item in self.player.inventory if getattr(item, 'is_consumable', False)]
        if not consumables:
            self.append_text("There are no usable items in your pack.", "enemy")
            return
            
        item_win = tk.Toplevel(self)
        item_win.title("Use Item")
        item_win.configure(bg="#080b13")
        item_win.grab_set()
        apply_display_mode(item_win)

        header = tk.Frame(item_win, bg="#111724", height=82, highlightbackground="#343e56", highlightthickness=1)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="FIELD SUPPLIES", font=("Georgia", 19, "bold"), fg="#f3f5ff", bg="#111724").pack(anchor="w", padx=22, pady=(15, 0))
        tk.Label(header, text="Choose a restorative from your pack", font=("Segoe UI", 9, "bold"), fg="#67dca5", bg="#111724").pack(anchor="w", padx=22)
        tk.Button(header, text="×", command=item_win.destroy, bg="#111724", fg="#8e9ab5", activebackground="#54232c", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Segoe UI", 20), cursor="hand2", padx=18).place(relx=.985, rely=.5, anchor="e")
        body = tk.Frame(item_win, bg="#080b13")
        body.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)
        listbox = tk.Listbox(body, bg="#0d121c", fg="#e4e8f3", font=("Consolas", 11), selectbackground="#2d6c56", selectforeground="#ffffff", relief=tk.FLAT, activestyle="none")
        listbox.pack(fill=tk.BOTH, expand=True)
        
        for item in consumables:
            listbox.insert(tk.END, f"{item.item_name} x{item.quantity} (Heals {item.heal_amount} HP)")
            
        def on_use():
            selection = listbox.curselection()
            if selection:
                if not self._begin_player_action("USING ITEM"):
                    item_win.destroy()
                    return
                used_item = consumables[selection[0]]
                self.player.consume_item(used_item)
                self.player.hp = min(self.player.hp + used_item.heal_amount, self.player.max_hp)
                self._show_floating_text(f"+{used_item.heal_amount}", "player", "#67dca5")
                self.append_text(f"{used_item.item_name} restores {used_item.heal_amount} HP.", "player")
                self.update_player_stats()
                item_win.destroy()
                self._queue_monster_turn()
                
        use_btn = tk.Button(item_win, text="USE SELECTED ITEM", command=on_use, bg="#2f765d", fg="white", activebackground="#439879", activeforeground="white", relief=tk.FLAT, bd=0, font=("Segoe UI", 10, "bold"), pady=12)
        use_btn.bind("<Enter>", lambda e: e.widget.config(bg="#439879"))
        use_btn.bind("<Leave>", lambda e: e.widget.config(bg="#2f765d"))
        use_btn.pack(pady=(0, 18), padx=18, fill=tk.X)
        listbox.bind("<Double-Button-1>", lambda _event: on_use())
        item_win.bind("<Escape>", lambda _event: item_win.destroy())

    def monster_turn(self, defending=False):
        if not self.winfo_exists():
            return
        self.turn_state = "enemy"
        self.turn_badge.config(text="ENEMY TURN", bg="#ff5967", fg="#ffffff")
        self.update_player_stats()
        self._animation_jobs.append(self.after(self._delay(350), lambda: self._resolve_monster_turn(defending)))

    def _resolve_monster_turn(self, defending=False):
        intent = self.enemy_intent
        if intent.kind == "heal":
            healed = min(self.monster_max_hp - self.monster_hp, max(1, int(self.monster_max_hp * intent.heal_fraction)))
            self.monster_hp += healed
            self._show_floating_text(f"+{healed}", "monster", "#67dca5")
            self.append_text(f"{self.monster_name} uses {intent.label} and restores {healed} HP.", "enemy")
            self.update_monster_stats()
            self._animation_jobs.append(self.after(self._delay(650), self._finish_enemy_turn))
            return
        if intent.kind == "guard":
            self.enemy_guard_fraction = intent.guard_fraction
            self.append_text(f"{self.monster_name} uses {intent.label} and braces against your next attack.", "enemy")
            self._animation_jobs.append(self.after(self._delay(650), self._finish_enemy_turn))
            return
        if self.evade_next_attack:
            self.evade_next_attack = False
            self._show_floating_text("EVADE", "player", "#72baff")
            self.append_text(f"You evade {self.monster_name}'s attack with Windstep!", "player")
            self.update_player_stats()
            self._animation_jobs.append(self.after(self._delay(500), self._finish_enemy_turn))
            return
        play_sound("damage")
        taken = self._incoming_damage(defending=defending, multiplier=intent.multiplier)
        self.player.hp -= taken
        self._animate_hit("player", taken)
        if defending:
            self.append_text(f"{self.monster_name} attacks, but your guard reduces it to {taken} damage.", "enemy")
        else:
            self.append_text(f"{self.monster_name} uses {intent.label} for {taken} damage.", "enemy")
        if intent.kind == "steal":
            stolen = min(self.player.coins, random.randint(3, 8))
            self.player.coins -= stolen
            self.append_text(f"The goblin steals {stolen} gold!", "enemy")
        self.update_player_stats()
        
        if self.player.hp <= 0:
            self.player_defeated()
            return
        self._animation_jobs.append(self.after(self._delay(650), self._finish_enemy_turn))

    def _incoming_damage(self, defending=False, multiplier=1.0):
        armor_def = self.player.equipped_armor.defense_bonus if getattr(self.player, 'equipped_armor', None) else 0
        defense_bonus = 5 + random.randint(0, 4) if defending else 0
        phase_multiplier = 1.0
        if self.is_boss:
            phase_multiplier += (self.boss_phase - 1) * 0.15
        taken = max(
            0,
            int(self.monster_attack * multiplier * phase_multiplier) + random.randint(0, 4)
            - int(armor_def)
            - defense_bonus
            - self.skill_guard_bonus
            - self.enemy_weaken,
        )
        if defending:
            taken = int(taken * DEFEND_DAMAGE_MULTIPLIER)
        self.skill_guard_bonus = 0
        self.enemy_weaken = 0
        return taken

    def _apply_enemy_guard(self, damage):
        if self.enemy_guard_fraction <= 0:
            return damage
        reduced_damage = max(1, int(damage * (1.0 - self.enemy_guard_fraction)))
        blocked = damage - reduced_damage
        self.enemy_guard_fraction = 0.0
        self.append_text(f"Bone Guard blocks {blocked} damage.", "enemy")
        return reduced_damage

    def _prepare_enemy_intent(self):
        hp_ratio = max(0, self.monster_hp) / self.monster_max_hp
        self.enemy_intent = choose_enemy_intent(self.monster_family, hp_ratio)
        if hasattr(self, "m_intent_lbl"):
            self.m_intent_lbl.config(text=f"INTENT  •  {self.enemy_intent.label.upper()}  [{self._intent_hint()}]")

    def player_defeated(self):
        self.append_text(f"You were defeated by {self.monster_name}.", "enemy")
        self.defeated = True
        self.turn_state = "defeated"
        self.update_player_stats()
        choice = DefeatScreen(self, self.player, self.monster_name).result
        if choice == "retry":
            self.player.hp = self.player.max_hp
            self.player.mana = 100
            self.retry_requested = True
        elif choice == "load":
            self.load_requested = True
        elif choice == "title":
            self.title_requested = True
        else:
            loss = difficulty_profile(self.difficulty)["defeat_gold_loss"]
            self.defeat_penalty = min(self.player.coins, max(1, int(self.player.coins * loss))) if self.player.coins else 0
            self.player.coins -= self.defeat_penalty
            self.player.hp = max(1, self.player.max_hp // 2)
            self.player.mana = max(self.player.mana, 40)
        self.destroy()

    def reward_player(self):
        self.victory = True
        region_key = current_region(self.player).key
        if self.is_miniboss:
            exp = self.monster_spec.reward_exp
            coins = self.monster_spec.reward_gold
        elif self.is_boss:
            exp, coins = 150, 200
        else:
            exp_range, coin_range = reward_ranges(region_key)
            exp = random.randint(*exp_range)
            coins = random.randint(*coin_range)
            if self.monster_spec.elite:
                exp = int(exp * 1.5)
                coins = int(coins * 1.5)
        exp, coins = scale_rewards(exp, coins, self.difficulty)
        previous_level = self.player.level
        self.player.add_experience(exp)
        self.player.add_coins(coins)

        dropped_item = None
        if self.is_miniboss:
            dropped_item = miniboss_loot(self.monster_spec.boss_key)
        elif not self.is_boss:
            drop_chance = 65 if self.monster_spec.elite else 40
            if random.randint(1, 100) <= drop_chance:
                dropped_item = roll_region_loot(region_key)
        if dropped_item:
            self.player.add_item(dropped_item)

        if self.is_miniboss and self.monster_spec.boss_key not in self.player.defeated_minibosses:
            self.player.defeated_minibosses.append(self.monster_spec.boss_key)

        quest_updates, quest_completions = record_defeat(self.player, self.monster_family)
        survival_updates, survival_completions = record_event(self.player, "survive", region_key)
        quest_updates += survival_updates
        quest_completions += survival_completions
        if self.monster_family == "skeleton" and self.defended_this_battle:
            special_updates, special_completions = record_event(self.player, "special_defeat", "skeleton_after_defend")
            quest_updates += special_updates
            quest_completions += special_completions

        VictoryScreen(
            self,
            self.player,
            self.monster_name,
            exp,
            coins,
            loot=dropped_item,
            leveled_up=self.player.level > previous_level,
            new_skills=newly_unlocked_skills(self.player, previous_level),
            new_mastery_rank=newly_reached_mastery(previous_level, self.player.level),
            quest_updates=quest_updates,
            quest_completions=quest_completions,
        )
