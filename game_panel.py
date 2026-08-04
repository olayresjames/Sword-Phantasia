import random
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from battle_panel import BattlePanel, hero_sprite_path
from character import Character, experience_to_next_level
from credits_panel import EndCreditsScreen
from exploration import LANDMARK_LABELS, MATERIAL_LABELS, choose_exploration_event
from game_data import SHOP_INVENTORY
from game_settings import apply_display_mode, key_sequence, settings
from audio_manager import audio_manager
from item import Item
from loot_data import RARITY_COLORS, roll_region_loot
from quests import QUESTS, completed_quest_keys, primary_objective, quest_objective_label, quest_progress, record_event
from skills import CLASS_SKILLS, class_name, mastery_rank
from world_data import MINIBOSSES, MINIBOSS_QUESTS, REGIONS, all_minibosses_defeated, current_region, defeated_miniboss_keys, miniboss_for_region


class GamePanel(tk.Frame):
    BG = "#070a11"
    SURFACE = "#101621"
    SURFACE_ALT = "#151d2b"
    BORDER = "#2a354b"
    TEXT = "#f2f5ff"
    MUTED = "#8793ac"
    BLUE = "#4ca8ff"
    GREEN = "#5ed9a2"
    GOLD = "#ffd166"
    RED = "#ff5363"
    PURPLE = "#a977e8"

    def __init__(self, parent, player):
        super().__init__(parent, bg=self.BG)
        self.player = player
        starting_region = current_region(player)
        self.player.current_region = starting_region.key
        self.location_name = starting_region.name
        self.location_description = starting_region.description
        self.btn_dict = {}
        self._toast_job = None
        self._bar_jobs = {}

        self._configure_styles()
        self._build_header()
        self._build_workspace()
        self._build_utility_bar()
        self._bind_shortcuts()
        self.update_stats()
        self.append_text(f"{self.player.name}'s journey begins at the Frontier Crossroads.", "system")

    def _configure_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        styles = {
            "AdventureHP.Horizontal.TProgressbar": self.RED,
            "AdventureMP.Horizontal.TProgressbar": self.BLUE,
            "AdventureXP.Horizontal.TProgressbar": self.GOLD,
        }
        for name, color in styles.items():
            style.configure(
                name,
                troughcolor="#252d3d",
                background=color,
                bordercolor="#252d3d",
                lightcolor=color,
                darkcolor=color,
                thickness=10,
            )

    def _build_header(self):
        header = tk.Frame(self, bg="#0d131e", height=64, highlightbackground=self.BORDER, highlightthickness=1)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)

        title_block = tk.Frame(header, bg="#0d131e")
        title_block.pack(side=tk.LEFT, padx=22, pady=9)
        tk.Label(title_block, text="SWORD PHANTASIA", font=("Georgia", 15, "bold"), fg=self.TEXT, bg="#0d131e").pack(anchor="w")
        tk.Label(title_block, text="ADVENTURE  •  CHAPTER I", font=("Arial", 8, "bold"), fg=self.PURPLE, bg="#0d131e").pack(anchor="w")

        self.save_status_lbl = tk.Label(header, text="NOT YET SAVED", font=("Arial", 8, "bold"), fg=self.MUTED, bg="#0d131e")
        self.save_status_lbl.pack(side=tk.RIGHT, padx=(8, 22))
        self.gold_header_lbl = tk.Label(header, text="◆ 0 G", font=("Consolas", 12, "bold"), fg=self.GOLD, bg="#0d131e")
        self.gold_header_lbl.pack(side=tk.RIGHT, padx=16)
        tk.Label(header, text="CURRENT FUNDS", font=("Arial", 8, "bold"), fg=self.MUTED, bg="#0d131e").pack(side=tk.RIGHT)

    def _build_workspace(self):
        workspace = tk.Frame(self, bg=self.BG)
        workspace.pack(fill=tk.BOTH, expand=True, padx=14, pady=12)

        self._build_hero_panel(workspace)
        self._build_journey_panel(workspace)
        self._build_action_panel(workspace)

    def _build_hero_panel(self, parent):
        panel = tk.Frame(parent, bg=self.SURFACE, width=255, highlightbackground=self.BORDER, highlightthickness=1)
        panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        panel.pack_propagate(False)

        tk.Label(panel, text="ADVENTURER", font=("Arial", 9, "bold"), fg=self.MUTED, bg=self.SURFACE).pack(anchor="w", padx=18, pady=(16, 4))
        portrait = tk.Canvas(panel, height=142, bg="#0b1019", highlightthickness=0)
        portrait.pack(fill=tk.X, padx=14)
        portrait.create_oval(50, 108, 190, 132, fill="#131d2d", outline="#31405c")
        self.hero_image = None
        sprite_path = hero_sprite_path(self.player)
        if sprite_path:
            try:
                self.hero_image = tk.PhotoImage(file=sprite_path)
            except (tk.TclError, OSError):
                pass
        if self.hero_image:
            portrait.create_image(120, 70, image=self.hero_image)
        else:
            portrait.create_text(120, 70, text="\\o/", font=("Consolas", 40, "bold"), fill=self.BLUE)

        self.hero_name_lbl = tk.Label(panel, font=("Arial", 18, "bold"), fg=self.TEXT, bg=self.SURFACE)
        self.hero_name_lbl.pack(anchor="w", padx=18, pady=(10, 0))
        self.level_lbl = tk.Label(panel, font=("Arial", 8, "bold"), fg=self.GOLD, bg=self.SURFACE, wraplength=218, justify=tk.LEFT)
        self.level_lbl.pack(anchor="w", padx=18, pady=(2, 12))

        self.hp_lbl, self.hp_bar = self._stat_bar(panel, "HP", self.RED, "AdventureHP.Horizontal.TProgressbar")
        self.mana_lbl, self.mana_bar = self._stat_bar(panel, "MP", self.BLUE, "AdventureMP.Horizontal.TProgressbar")
        self.xp_lbl, self.xp_bar = self._stat_bar(panel, "EXP", self.GOLD, "AdventureXP.Horizontal.TProgressbar")

        tk.Label(panel, text="EQUIPMENT", font=("Arial", 9, "bold"), fg=self.MUTED, bg=self.SURFACE).pack(anchor="w", padx=18, pady=(18, 7))
        self.weapon_lbl = self._equipment_chip(panel, "WEAPON")
        self.armor_lbl = self._equipment_chip(panel, "ARMOR")

    def _stat_bar(self, parent, name, color, style):
        row = tk.Frame(parent, bg=self.SURFACE)
        row.pack(fill=tk.X, padx=18, pady=(0, 8))
        tk.Label(row, text=name, width=4, anchor="w", font=("Consolas", 9, "bold"), fg=color, bg=self.SURFACE).pack(side=tk.LEFT)
        value = tk.Label(row, font=("Consolas", 9, "bold"), fg=self.TEXT, bg=self.SURFACE)
        value.pack(side=tk.RIGHT)
        bar = ttk.Progressbar(parent, style=style, orient="horizontal", mode="determinate")
        bar.pack(fill=tk.X, padx=18, pady=(0, 10), ipady=2)
        return value, bar

    def _equipment_chip(self, parent, title):
        chip = tk.Frame(parent, bg=self.SURFACE_ALT, height=47)
        chip.pack(fill=tk.X, padx=14, pady=4)
        chip.pack_propagate(False)
        tk.Label(chip, text=title, width=8, anchor="w", font=("Arial", 8, "bold"), fg=self.MUTED, bg=self.SURFACE_ALT).pack(side=tk.LEFT, padx=(12, 4))
        value = tk.Label(chip, anchor="e", font=("Arial", 9, "bold"), fg=self.TEXT, bg=self.SURFACE_ALT)
        value.pack(side=tk.RIGHT, padx=12)
        return value

    def _build_journey_panel(self, parent):
        center = tk.Frame(parent, bg=self.BG)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)

        area = tk.Frame(center, bg=self.SURFACE, height=112, highlightbackground=self.BORDER, highlightthickness=1)
        area.pack(fill=tk.X, pady=(0, 10))
        area.pack_propagate(False)
        tk.Frame(area, bg=self.BLUE, width=5).pack(side=tk.LEFT, fill=tk.Y)
        area_copy = tk.Frame(area, bg=self.SURFACE)
        area_copy.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=18, pady=12)
        tk.Label(area_copy, text="CURRENT AREA", font=("Arial", 8, "bold"), fg=self.MUTED, bg=self.SURFACE).pack(anchor="w")
        self.location_lbl = tk.Label(area_copy, font=("Georgia", 20, "bold"), fg=self.TEXT, bg=self.SURFACE)
        self.location_lbl.pack(anchor="w")
        self.location_desc_lbl = tk.Label(area_copy, font=("Arial", 9), fg="#aab4c8", bg=self.SURFACE)
        self.location_desc_lbl.pack(anchor="w", pady=(2, 0))

        objective = tk.Frame(center, bg="#171525", height=55, highlightbackground="#4b3968", highlightthickness=1)
        objective.pack(fill=tk.X, pady=(0, 10))
        objective.pack_propagate(False)
        tk.Label(objective, text="OBJECTIVE", font=("Arial", 8, "bold"), fg=self.PURPLE, bg="#171525").pack(side=tk.LEFT, padx=(16, 10))
        self.objective_lbl = tk.Label(objective, font=("Arial", 10, "bold"), fg="#ddd1ee", bg="#171525")
        self.objective_lbl.pack(side=tk.LEFT)

        log_frame = tk.Frame(center, bg="#090d14", highlightbackground=self.BORDER, highlightthickness=1)
        log_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(log_frame, text="JOURNEY LOG", font=("Arial", 9, "bold"), fg=self.MUTED, bg="#090d14").pack(anchor="w", padx=16, pady=(13, 3))
        self.text_area = tk.Text(
            log_frame,
            state=tk.DISABLED,
            wrap=tk.WORD,
            bg="#090d14",
            fg="#dce3f2",
            font=("Consolas", 11),
            relief=tk.FLAT,
            padx=14,
            pady=8,
            spacing1=3,
            spacing3=5,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.tag_configure("system", foreground="#aab5cb")
        self.text_area.tag_configure("travel", foreground="#71b9ff")
        self.text_area.tag_configure("success", foreground=self.GREEN)
        self.text_area.tag_configure("warning", foreground="#ff8993")
        self.text_area.tag_configure("reward", foreground=self.GOLD)
        self.text_area.tag_configure("special", foreground="#c59af2")

    def _build_action_panel(self, parent):
        panel = tk.Frame(parent, bg=self.SURFACE, width=310, highlightbackground=self.BORDER, highlightthickness=1)
        panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        panel.pack_propagate(False)

        tk.Label(panel, text="TRAVEL", font=("Arial", 9, "bold"), fg=self.MUTED, bg=self.SURFACE).pack(anchor="w", padx=18, pady=(16, 8))
        movement = tk.Frame(panel, bg=self.SURFACE)
        movement.pack(padx=18)
        self._action_button(movement, "▲", "Walk Forward", 0, 1, "Move north along the road", compact=True)
        self._action_button(movement, "◀", "Walk Left", 1, 0, "Take the western path", compact=True)
        self._action_button(movement, "●", "Explore", 1, 1, "Search the current area", compact=True, color="#7f2632", hover="#b63846")
        self._action_button(movement, "▶", "Walk Right", 1, 2, "Take the eastern path", compact=True)
        self._action_button(movement, "▼", "Walk Back", 2, 1, "Return toward camp", compact=True)

        self._section_label(panel, "ADVENTURE")
        adventure = tk.Frame(panel, bg=self.SURFACE)
        adventure.pack(fill=tk.X, padx=13)
        self._action_button(adventure, "EXPLORE", "Explore", 0, 0, "Search for monsters and discoveries", color="#7f2632", hover="#b63846")
        self._action_button(adventure, "REST", "Rest", 0, 1, "Recover 10 HP and 10 MP", color="#27634d", hover="#328165")
        self._action_button(adventure, "REGION MAP", "Region Map", 1, 0, "Travel between unlocked regions")
        self._action_button(adventure, "QUEST LOG", "Quest Log", 1, 1, "Review objectives and rewards")

        self._section_label(panel, "SETTLEMENT")
        settlement = tk.Frame(panel, bg=self.SURFACE)
        settlement.pack(fill=tk.X, padx=13)
        self._action_button(settlement, "SHOP", "Shop", 0, 0, "Purchase equipment and supplies")
        self._action_button(settlement, "SMITH", "Blacksmith", 0, 1, "Upgrade your equipped weapon")

        self.champion_btn = tk.Button(
            panel,
            text="REGION CHAMPION  •  LOCKED",
            command=lambda: self.action_performed("Challenge Region Champion"),
            bg="#191e2a",
            fg="#68738d",
            disabledforeground="#68738d",
            relief=tk.FLAT,
            bd=0,
            font=("Arial", 9, "bold"),
            cursor="hand2",
            pady=11,
            state=tk.DISABLED,
        )
        self.champion_btn.pack(fill=tk.X, padx=18, pady=(18, 0))
        self.btn_dict["Challenge Region Champion"] = self.champion_btn

        self.boss_btn = tk.Button(
            panel,
            text="FINAL OBJECTIVE  •  LOCKED",
            command=lambda: self.action_performed("Challenge Demon King"),
            bg="#191e2a",
            fg="#68738d",
            disabledforeground="#68738d",
            relief=tk.FLAT,
            bd=0,
            font=("Arial", 9, "bold"),
            cursor="hand2",
            pady=11,
            state=tk.DISABLED,
        )
        self.boss_btn.pack(fill=tk.X, padx=18, pady=(8, 8))
        self.btn_dict["Challenge Demon King"] = self.boss_btn

        self.action_hint = tk.StringVar(value="Choose an action to continue your journey.")
        tk.Label(panel, textvariable=self.action_hint, wraplength=265, justify=tk.LEFT, font=("Arial", 9), fg=self.MUTED, bg=self.SURFACE).pack(side=tk.BOTTOM, anchor="w", padx=18, pady=16)

    def _section_label(self, parent, text):
        tk.Label(parent, text=text, font=("Arial", 9, "bold"), fg=self.MUTED, bg=self.SURFACE).pack(anchor="w", padx=18, pady=(18, 7))

    def _action_button(self, parent, label, command, row, column, hint, compact=False, color="#263149", hover="#354461"):
        button = tk.Button(
            parent,
            text=label,
            command=lambda: self.action_performed(command),
            bg=color,
            fg=self.TEXT,
            activebackground=hover,
            activeforeground="#ffffff",
            disabledforeground="#667087",
            relief=tk.FLAT,
            bd=0,
            font=("Arial", 13 if compact else 10, "bold"),
            cursor="hand2",
            width=4 if compact else 10,
            pady=10 if compact else 11,
        )
        button.base_color = color
        button.hover_color = hover
        button.hint = hint
        button.default_hint = hint
        button.bind("<Enter>", self._on_action_hover)
        button.bind("<Leave>", self._on_action_leave)
        button.grid(row=row, column=column, sticky="nsew", padx=4, pady=4)
        parent.grid_columnconfigure(column, weight=1)
        self.btn_dict.setdefault(command, button)
        return button

    def _build_utility_bar(self):
        bar = tk.Frame(self, bg="#0d131e", height=62, highlightbackground=self.BORDER, highlightthickness=1)
        bar.pack(side=tk.BOTTOM, fill=tk.X)
        bar.pack_propagate(False)
        tk.Label(bar, text="MENU", font=("Arial", 8, "bold"), fg=self.MUTED, bg="#0d131e").pack(side=tk.LEFT, padx=(20, 8))
        self._utility_button(bar, "INVENTORY  [I]", "Inventory")
        self._utility_button(bar, "EQUIPMENT  [E]", "Equip")
        self._utility_button(bar, "OPTIONS  [ESC]", "Options")
        self._utility_button(bar, "AUDIO & SETTINGS  [F10]", "Settings")
        self._utility_button(bar, "SAVE GAME", "Save Game")
        self._utility_button(bar, "QUIT", "Quit", danger=True, side=tk.RIGHT)

        self.toast_lbl = tk.Label(self, font=("Arial", 9, "bold"), fg="#09110d", bg=self.GREEN, padx=18, pady=9)

    def _utility_button(self, parent, text, command, danger=False, side=tk.LEFT):
        base = "#54232c" if danger else self.SURFACE_ALT
        hover = "#7d303d" if danger else "#253149"
        button = tk.Button(parent, text=text, command=lambda: self.action_performed(command), bg=base, fg=self.TEXT, activebackground=hover, activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Arial", 9, "bold"), cursor="hand2", padx=17, pady=9)
        button.base_color = base
        button.hover_color = hover
        button.bind("<Enter>", lambda event: event.widget.config(bg=event.widget.hover_color) if event.widget["state"] != tk.DISABLED else None)
        button.bind("<Leave>", lambda event: event.widget.config(bg=event.widget.base_color) if event.widget["state"] != tk.DISABLED else None)
        button.pack(side=side, padx=5, pady=10)
        self.btn_dict[command] = button

    def _bind_shortcuts(self):
        root = self.winfo_toplevel()
        for sequence in getattr(self, "_shortcut_sequences", ()):
            root.unbind(sequence)
        bindings = {
            key_sequence(settings.key("walk_forward")): "Walk Forward",
            "<KeyPress-Up>": "Walk Forward",
            key_sequence(settings.key("walk_back")): "Walk Back",
            "<KeyPress-Down>": "Walk Back",
            key_sequence(settings.key("walk_left")): "Walk Left",
            "<KeyPress-Left>": "Walk Left",
            key_sequence(settings.key("walk_right")): "Walk Right",
            "<KeyPress-Right>": "Walk Right",
            key_sequence(settings.key("inventory")): "Inventory",
            key_sequence(settings.key("equip")): "Equip",
            key_sequence(settings.key("region_map")): "Region Map",
            key_sequence(settings.key("quest_log")): "Quest Log",
            key_sequence(settings.key("options")): "Options",
            "<KeyPress-F10>": "Settings",
        }
        self._shortcut_sequences = tuple(bindings)
        for sequence, command in bindings.items():
            root.bind(sequence, lambda _event, value=command: self.action_performed(value))

    def _on_action_hover(self, event):
        button = event.widget
        self.action_hint.set(button.hint)
        if button["state"] != tk.DISABLED:
            button.config(bg=button.hover_color)

    def _on_action_leave(self, event):
        button = event.widget
        self.action_hint.set("Choose an action to continue your journey.")
        if button["state"] != tk.DISABLED:
            button.config(bg=button.base_color)

    def update_stats(self):
        weapon = self.player.equipped_weapon if getattr(self.player, "equipped_weapon", None) else None
        armor = self.player.equipped_armor if getattr(self.player, "equipped_armor", None) else None
        self.hero_name_lbl.config(text=self.player.name)
        self.level_lbl.config(text=f"LEVEL {self.player.level}  •  {class_name(self.player).upper()}  •  MASTERY {mastery_rank(self.player)}")
        self.gold_header_lbl.config(text=f"◆ {self.player.coins} G")
        self.hp_lbl.config(text=f"{max(0, self.player.hp)} / {self.player.max_hp}")
        self._animate_bar(self.hp_bar, max(0, self.player.hp), self.player.max_hp)
        self.mana_lbl.config(text=f"{self.player.mana} / 100")
        self._animate_bar(self.mana_bar, self.player.mana, 100)
        xp_required = experience_to_next_level(self.player.level)
        self.xp_lbl.config(text=f"{self.player.experience} / {xp_required}")
        self._animate_bar(self.xp_bar, self.player.experience, xp_required)
        self.weapon_lbl.config(text=f"{weapon.item_name} {weapon.forge_label()}" if weapon else "None")
        self.armor_lbl.config(text=armor.item_name if armor else "None")
        self.location_lbl.config(text=self.location_name)
        self.location_desc_lbl.config(text=self.location_description)

        equippables = [item for item in self.player.inventory if not getattr(item, "is_consumable", False)]
        self._set_button_state("Equip", bool(equippables), "No equipment available")
        self._set_button_state("Blacksmith", weapon is not None, "Equip a weapon to use the smith")

        region_key = self.player.current_region
        region_boss = MINIBOSSES.get(region_key)
        available_boss = miniboss_for_region(self.player, region_key)
        defeated_bosses = defeated_miniboss_keys(self.player)
        if available_boss:
            self.champion_btn.config(text=f"CHALLENGE  •  {available_boss.name.upper()}", state=tk.NORMAL, bg="#8a6427", fg="#ffffff")
        elif region_boss and region_boss.boss_key in defeated_bosses:
            self.champion_btn.config(text="REGION CHAMPION  •  DEFEATED", state=tk.DISABLED, bg="#21352e", fg=self.GREEN)
        elif region_boss:
            quest_title = next(quest.title for quest in QUESTS if quest.key == MINIBOSS_QUESTS[region_key])
            self.champion_btn.config(text=f"COMPLETE  •  {quest_title.upper()}", state=tk.DISABLED, bg="#191e2a", fg="#68738d")
        else:
            self.champion_btn.config(text="REGION CHAMPIONS  •  RETURN TO THE REALM", state=tk.DISABLED, bg="#191e2a", fg="#68738d")

        guardians_ready = all_minibosses_defeated(self.player)
        boss_ready = self.player.level >= 10 and region_key == "throne" and guardians_ready
        if boss_ready:
            self.boss_btn.config(text="CHALLENGE DEMON KING", state=tk.NORMAL, bg="#663795", fg="#ffffff")
            self.boss_btn.bind("<Enter>", lambda event: event.widget.config(bg="#8750bc"))
            self.boss_btn.bind("<Leave>", lambda event: event.widget.config(bg="#663795"))
            self.objective_lbl.config(text=primary_objective(self.player))
        else:
            if self.player.level < 10:
                boss_text = f"FINAL OBJECTIVE  •  LEVEL {self.player.level}/10"
            elif not guardians_ready:
                boss_text = f"DEFEAT REGION CHAMPIONS  •  {len(defeated_bosses)}/3"
            else:
                boss_text = "FINAL OBJECTIVE  •  TRAVEL TO THRONE"
            self.boss_btn.config(text=boss_text, state=tk.DISABLED, bg="#191e2a", fg="#68738d")
            self.objective_lbl.config(text=primary_objective(self.player))

        if available_boss:
            self.objective_lbl.config(text=f"Challenge the region champion: {available_boss.name}")
        elif self.player.level >= 10 and not guardians_ready:
            self.objective_lbl.config(text=f"Break the champion seals: {len(defeated_bosses)}/3 defeated")

    def _set_button_state(self, command, enabled, disabled_hint):
        button = self.btn_dict.get(command)
        if not button:
            return
        button.config(state=tk.NORMAL if enabled else tk.DISABLED, bg=button.base_color if enabled else "#191e2a")
        if hasattr(button, "hint"):
            button.hint = button.default_hint if enabled else disabled_hint

    def _animate_bar(self, bar, target, maximum):
        old_job = self._bar_jobs.get(str(bar))
        if old_job:
            try:
                self.after_cancel(old_job)
            except tk.TclError:
                pass
        bar.config(maximum=maximum)
        start = float(bar["value"])
        target = max(0, min(float(target), float(maximum)))
        if settings.get("reduce_animations"):
            bar["value"] = target
            self._bar_jobs.pop(str(bar), None)
            return
        steps = 10

        def advance(step=1):
            bar["value"] = start + (target - start) * step / steps
            if step < steps:
                self._bar_jobs[str(bar)] = self.after(settings.delay(24), lambda: advance(step + 1))
            else:
                self._bar_jobs.pop(str(bar), None)

        advance()

    def append_text(self, text, kind="system"):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, "› ", "system")
        self.text_area.insert(tk.END, text.strip() + "\n", kind)
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def show_toast(self, text, color=None):
        if self._toast_job:
            try:
                self.after_cancel(self._toast_job)
            except tk.TclError:
                pass
        self.toast_lbl.config(text=text, bg=color or self.GREEN)
        self.toast_lbl.place(relx=0.98, rely=0.09, anchor="ne")
        self.toast_lbl.lift()
        self._toast_job = self.after(2200, self.toast_lbl.place_forget)

    def _pulse_label(self, label, color):
        original = label.cget("fg")
        label.config(fg=color)
        self.after(450, lambda: label.config(fg=original) if label.winfo_exists() else None)

    def encounter_monster(self):
        region = current_region(self.player)
        if not region.monsters:
            self.append_text("No lesser creature dares approach the Primordial Throne.", "special")
            return
        self.append_text(f"A hostile presence emerges in {region.name}!", "warning")
        battle = self._run_battle()
        if battle is None:
            return
        if battle.victory:
            self.append_text(f"You return from battle with {battle.monster_name} behind you.", "success")
        else:
            return
        self.player.save_to_file()
        self.save_status_lbl.config(text="AUTOSAVED", fg=self.GREEN)
        self.show_toast("GAME AUTOSAVED")
        self.update_stats()

    def _run_battle(self, monster_spec=None, is_boss=False, is_miniboss=False):
        encounter_spec = monster_spec
        while True:
            battle = BattlePanel(
                self.winfo_toplevel(),
                self.player,
                is_boss=is_boss,
                monster_spec=encounter_spec,
                is_miniboss=is_miniboss,
            )
            encounter_spec = battle.monster_spec
            if battle.retry_requested:
                self.append_text(f"You rise to challenge {battle.monster_name} again.", "special")
                continue
            if battle.load_requested:
                loaded = Character.load_from_file()
                if loaded:
                    self.player = loaded
                    region = current_region(self.player)
                    self.location_name, self.location_description = region.locations["back"]
                    self.append_text("The last save is restored. The failed battle never happened.", "success")
                    self.update_stats()
                    self.show_toast("LAST SAVE LOADED", self.BLUE)
                else:
                    self.append_text("No save could be loaded. You return to camp instead.", "warning")
                    self.player.hp = max(1, self.player.max_hp // 2)
                    self.player.mana = max(self.player.mana, 40)
                return None
            if battle.title_requested:
                self._return_to_title_now()
                return None
            if battle.defeated:
                region = current_region(self.player)
                self.location_name, self.location_description = region.locations["back"]
                self.append_text(f"You awaken at {self.location_name}, having lost {battle.defeat_penalty} gold.", "warning")
                self.player.save_to_file()
                self.save_status_lbl.config(text="AUTOSAVED", fg=self.GREEN)
                self.update_stats()
            return battle

    def _return_to_title_now(self):
        root = self.winfo_toplevel()
        self.destroy()
        from main_menu import MainMenu
        MainMenu(root)

    def resolve_exploration_event(self):
        region = current_region(self.player)
        event = choose_exploration_event(self.player, region.key)
        self.append_text(f"{event.title}: {event.description}", "special")
        updates, completions = [], []

        if event.kind == "treasure":
            region_index = tuple(REGIONS).index(region.key)
            gold = random.randint(12 + region_index * 8, 28 + region_index * 14)
            self.player.add_coins(gold)
            self.append_text(f"The cache contains {gold} gold.", "reward")
            if random.randint(1, 100) <= 35:
                item = roll_region_loot(region.key)
                self.player.add_item(item)
                self.append_text(f"You also discover a {item.rarity} {item.item_name}.", "reward")

        elif event.kind == "material":
            updates, completions = self._gather_material(event.target)

        elif event.kind == "landmark":
            if event.target not in self.player.discovered_landmarks:
                self.player.discovered_landmarks.append(event.target)
            updates, completions = record_event(self.player, "landmark", event.target)
            self.location_name = LANDMARK_LABELS.get(event.target, event.title)
            self.location_description = event.description
            self.append_text(f"Landmark discovered: {self.location_name}.", "reward")

        elif event.kind == "choice":
            updates, completions = self._resolve_story_choice(event)

        elif event.kind == "shrine":
            pray = messagebox.askyesno(event.title, f"{event.description}\n\nCommune with the shrine?", parent=self)
            if pray:
                hp_before, mana_before = self.player.hp, self.player.mana
                self.player.hp = min(self.player.max_hp, self.player.hp + max(25, self.player.max_hp // 4))
                self.player.mana = min(100, self.player.mana + 30)
                self.append_text(f"The shrine restores {self.player.hp - hp_before} HP and {self.player.mana - mana_before} MP.", "success")
            else:
                self.append_text("You leave the shrine undisturbed.", "system")

        elif event.kind == "trap":
            disarm = messagebox.askyesno(event.title, f"{event.description}\n\nAttempt to disarm it for materials?", parent=self)
            if disarm and random.randint(1, 100) <= 65:
                self.append_text("You disarm the trap and recover its rare components.", "success")
                updates, completions = self._gather_material(event.target)
            elif disarm:
                damage = max(8, self.player.max_hp // 8)
                self.player.hp = max(1, self.player.hp - damage)
                self.append_text(f"The trap triggers for {damage} damage, but you escape alive.", "warning")
            else:
                mana_loss = min(self.player.mana, 5)
                self.player.mana -= mana_loss
                self.append_text(f"A careful detour costs time and {mana_loss} MP.", "system")

        elif event.kind == "merchant":
            item = roll_region_loot(region.key)
            rarity_factor = {"Common": 1.0, "Uncommon": 1.3, "Rare": 1.7, "Epic": 2.2, "Legendary": 3.0}.get(item.rarity, 1.0)
            region_index = tuple(REGIONS).index(region.key)
            price = int(round((20 + region_index * 20) * rarity_factor / 5.0) * 5)
            buy = messagebox.askyesno(event.title, f"{event.description}\n\n{item.rarity} {item.item_name} — {price} gold\n\nPurchase it?", parent=self)
            if buy and self.player.spend_coins(price):
                self.player.add_item(item)
                self.append_text(f"You purchase {item.item_name} for {price} gold.", "reward")
            elif buy:
                self.append_text("The merchant sees your empty purse and closes the case.", "warning")
            else:
                self.append_text("You decline the merchant's offer.", "system")

        self._report_quest_progress(updates, completions)
        self.player.save_to_file()
        self.save_status_lbl.config(text="AUTOSAVED", fg=self.GREEN)
        self.update_stats()

    def _gather_material(self, material_key):
        label = MATERIAL_LABELS.get(material_key, material_key.replace("_", " ").title())
        self.player.materials[material_key] = self.player.materials.get(material_key, 0) + 1
        self.append_text(f"Material acquired: {label} ({self.player.materials[material_key]} owned).", "reward")
        return record_event(self.player, "collect", material_key)

    def _resolve_story_choice(self, event):
        prompts = {
            "aid_pilgrim": "Give the pilgrim 10 gold and escort them toward camp?",
            "guide_scout": "Guide the scout through the dangerous warband trails?",
            "free_spirit": "Break the binding sigil and release the spirit?",
            "spare_shade": "Spare the shade and hear its secret?",
        }
        accepted = messagebox.askyesno(event.title, f"{event.description}\n\n{prompts.get(event.target, 'Offer your help?')}", parent=self)
        decision = "aid" if accepted else "refuse"
        self.player.story_choices.append(f"{event.target}:{decision}")
        if accepted:
            if event.target == "aid_pilgrim":
                donation = min(10, self.player.coins)
                self.player.coins -= donation
                self.append_text(f"You give {donation} gold. The pilgrim blesses your journey.", "success")
            elif event.target == "guide_scout":
                self.player.add_coins(30)
                self.append_text("The grateful scout shares a hidden warband purse containing 30 gold.", "reward")
            elif event.target == "free_spirit":
                self.player.mana = 100
                self.append_text("The freed spirit restores your MP before fading into peace.", "success")
            elif event.target == "spare_shade":
                self.player.materials["void_ember"] = self.player.materials.get("void_ember", 0) + 1
                self.append_text("The shade reveals a Void Ember and the weakness of the throne.", "reward")
                extra_updates, extra_completions = record_event(self.player, "collect", "void_ember")
                choice_updates, choice_completions = record_event(self.player, "choice", event.target)
                return choice_updates + extra_updates, choice_completions + extra_completions
        else:
            self.append_text("You refuse the request and continue on your chosen path.", "system")
        return record_event(self.player, "choice", event.target)

    def _report_quest_progress(self, updates, completions):
        for quest, progress in updates:
            self.append_text(f"Quest progress: {quest.title} — {progress}/{quest.required}.", "success")
        for quest, reward_item in completions:
            item_text = f" and {reward_item.item_name}" if reward_item else ""
            self.append_text(f"Quest complete: {quest.title}! +{quest.reward_exp} EXP, +{quest.reward_gold} gold{item_text}.", "reward")
            self.show_toast(f"QUEST COMPLETE  •  {quest.title.upper()}", self.GOLD)

    def rest(self):
        hp_before, mana_before = self.player.hp, self.player.mana
        self.player.hp = min(self.player.hp + 10, self.player.max_hp)
        self.player.mana = min(self.player.mana + 10, 100)
        hp_gain = self.player.hp - hp_before
        mana_gain = self.player.mana - mana_before
        self.append_text(f"You rest by the roadside and recover {hp_gain} HP and {mana_gain} MP.", "success")
        self.update_stats()
        self._pulse_label(self.hp_lbl, self.GREEN)
        self._pulse_label(self.mana_lbl, self.GREEN)

    def show_region_map(self):
        window, content = self._modal("REGION MAP", "Travel across the realm as your strength grows.", "760x520")
        regions = tuple(REGIONS.values())
        body = tk.Frame(content, bg=self.SURFACE)
        body.pack(fill=tk.BOTH, expand=True, padx=22, pady=22)
        listbox = tk.Listbox(body, bg="#0b1019", fg=self.TEXT, selectbackground="#3b4d70", selectforeground="#ffffff", font=("Consolas", 11, "bold"), relief=tk.FLAT, activestyle="none", width=31)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        details = tk.Frame(body, bg=self.SURFACE_ALT, width=390)
        details.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        name_lbl = tk.Label(details, text="SELECT A REGION", wraplength=330, font=("Georgia", 20, "bold"), fg=self.TEXT, bg=self.SURFACE_ALT)
        name_lbl.pack(padx=24, pady=(34, 8))
        level_lbl = tk.Label(details, text="", font=("Arial", 9, "bold"), fg=self.GOLD, bg=self.SURFACE_ALT)
        level_lbl.pack()
        description_lbl = tk.Label(details, text="Choose a destination on the map.", wraplength=330, justify=tk.LEFT, font=("Arial", 10), fg=self.MUTED, bg=self.SURFACE_ALT)
        description_lbl.pack(padx=26, pady=20)
        travel_btn = self._modal_button(details, "SELECT REGION", lambda: travel(), self.BLUE, "#3d8fd7")
        travel_btn.config(state=tk.DISABLED)

        for region in regions:
            if self.player.current_region == region.key:
                marker = "HERE"
            elif self.player.level >= region.unlock_level:
                marker = "OPEN"
            else:
                marker = f"LV {region.unlock_level}"
            listbox.insert(tk.END, f" {marker:<5}  {region.name}")

        def on_select(_event=None):
            selection = listbox.curselection()
            if not selection:
                return
            region = regions[selection[0]]
            unlocked = self.player.level >= region.unlock_level
            current = self.player.current_region == region.key
            name_lbl.config(text=region.name)
            level_lbl.config(text=f"UNLOCK LEVEL  {region.unlock_level}")
            monsters = ", ".join(monster.name for monster in region.monsters) or "Demon King Koji"
            champion = MINIBOSSES.get(region.key)
            champion_text = f"\n\nREGION CHAMPION\n{champion.name}" if champion else ""
            description_lbl.config(text=f"{region.description}\n\nENCOUNTERS\n{monsters}{champion_text}")
            if current:
                travel_btn.config(text="CURRENT REGION", state=tk.DISABLED, bg="#252b37")
            elif not unlocked:
                travel_btn.config(text=f"REQUIRES LEVEL {region.unlock_level}", state=tk.DISABLED, bg="#252b37")
            else:
                travel_btn.config(text="TRAVEL HERE", state=tk.NORMAL, bg=self.BLUE, command=travel)

        def travel():
            selection = listbox.curselection()
            if not selection:
                return
            region = regions[selection[0]]
            if self.player.level < region.unlock_level:
                return
            self.player.current_region = region.key
            self.location_name = region.name
            self.location_description = region.description
            self.append_text(f"You travel to {region.name}.", "travel")
            self.update_stats()
            self.show_toast(f"REGION  •  {region.name.upper()}", self.BLUE)
            window.destroy()

        listbox.bind("<<ListboxSelect>>", on_select)
        listbox.bind("<Double-Button-1>", lambda _event: travel())

    def show_quest_log(self):
        window, content = self._modal("QUEST LOG", "Track the battles shaping the fate of the realm.", "800x550")
        completed = completed_quest_keys(self.player)
        quests = tuple(quest for quest in QUESTS if self.player.level >= quest.unlock_level)
        body = tk.Frame(content, bg=self.SURFACE)
        body.pack(fill=tk.BOTH, expand=True, padx=22, pady=22)
        listbox = tk.Listbox(body, bg="#0b1019", fg=self.TEXT, selectbackground="#3b4d70", selectforeground="#ffffff", font=("Consolas", 10, "bold"), relief=tk.FLAT, activestyle="none", width=35)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        details = tk.Frame(body, bg=self.SURFACE_ALT)
        details.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        name_lbl = tk.Label(details, text="SELECT A QUEST", wraplength=350, font=("Georgia", 19, "bold"), fg=self.TEXT, bg=self.SURFACE_ALT)
        name_lbl.pack(padx=24, pady=(34, 8))
        status_lbl = tk.Label(details, text="", font=("Arial", 9, "bold"), fg=self.GREEN, bg=self.SURFACE_ALT)
        status_lbl.pack()
        description_lbl = tk.Label(details, text="Your active story objectives appear here.", wraplength=350, justify=tk.LEFT, font=("Arial", 10), fg=self.MUTED, bg=self.SURFACE_ALT)
        description_lbl.pack(padx=28, pady=22)

        if not quests:
            listbox.insert(tk.END, " No quests available")
        for quest in quests:
            progress = quest_progress(self.player, quest)
            marker = "DONE" if quest.key in completed else f"{progress}/{quest.required}"
            listbox.insert(tk.END, f" {marker:<5}  {quest.title}")

        def on_select(_event=None):
            selection = listbox.curselection()
            if not selection or not quests:
                return
            quest = quests[selection[0]]
            progress = quest_progress(self.player, quest)
            is_complete = quest.key in completed
            name_lbl.config(text=quest.title)
            status_lbl.config(text="COMPLETED" if is_complete else f"PROGRESS  {progress} / {quest.required}", fg=self.GREEN if is_complete else self.GOLD)
            item_reward = f" + {quest.reward_item[0]}" if quest.reward_item else ""
            region_name = REGIONS[quest.region].name
            description_lbl.config(text=f"{quest.description}\n\nOBJECTIVE\n{quest_objective_label(quest)}\n\nREGION\n{region_name}\n\nREWARD\n{quest.reward_exp} EXP  •  {quest.reward_gold} GOLD{item_reward}")

        listbox.bind("<<ListboxSelect>>", on_select)

    def visit_blacksmith(self):
        weapon = getattr(self.player, "equipped_weapon", None)
        if not weapon:
            self.show_toast("EQUIP A WEAPON FIRST", self.RED)
            return
        window, content = self._modal("THE BLACKSMITH", "Five forge tiers. Linear power. Rising cost.", "600x460")
        tk.Label(content, text="EQUIPPED WEAPON", font=("Arial", 9, "bold"), fg=self.MUTED, bg=self.SURFACE).pack(anchor="w", padx=28, pady=(24, 5))
        tk.Label(content, text=f"{weapon.item_name}  {weapon.forge_label()}", font=("Georgia", 24, "bold"), fg=self.TEXT, bg=self.SURFACE).pack(anchor="w", padx=28)

        comparison = tk.Frame(content, bg=self.SURFACE_ALT)
        comparison.pack(fill=tk.X, padx=28, pady=22)
        current = weapon.additional_damage
        upgraded = weapon.next_upgrade_damage()
        tk.Label(comparison, text=f"CURRENT\n{current:.1f} DMG", font=("Consolas", 12, "bold"), fg=self.MUTED, bg=self.SURFACE_ALT, justify=tk.CENTER).pack(side=tk.LEFT, expand=True, pady=18)
        tk.Label(comparison, text="➜", font=("Arial", 20, "bold"), fg=self.GOLD, bg=self.SURFACE_ALT).pack(side=tk.LEFT)
        after_text = f"AFTER +{weapon.upgrade_level + 1}\n{upgraded:.1f} DMG" if not weapon.at_max_upgrade else f"FORGE LIMIT\n{current:.1f} DMG"
        tk.Label(comparison, text=after_text, font=("Consolas", 12, "bold"), fg=self.GREEN if not weapon.at_max_upgrade else self.GOLD, bg=self.SURFACE_ALT, justify=tk.CENTER).pack(side=tk.LEFT, expand=True, pady=18)

        cost = weapon.upgrade_cost()
        can_afford = cost is not None and self.player.coins >= cost
        if weapon.is_legacy_upgrade:
            cost_text = f"LEGACY WEAPON  •  PRESERVED ABOVE THE +{weapon.max_upgrade_level} CAP"
        elif weapon.at_max_upgrade:
            cost_text = f"MAXIMUM FORGE TIER  •  +{weapon.max_upgrade_level}"
        else:
            cost_text = f"COST  {cost} G    •    FUNDS  {self.player.coins} G"
        cost_lbl = tk.Label(content, text=cost_text, font=("Arial", 10, "bold"), fg=self.GOLD if can_afford or weapon.at_max_upgrade else self.RED, bg=self.SURFACE)
        cost_lbl.pack()

        def upgrade():
            current_cost = weapon.upgrade_cost()
            if current_cost is None or not self.player.spend_coins(current_cost):
                return
            if not weapon.upgrade_weapon():
                self.player.add_coins(current_cost)
                return
            self.append_text(f"The blacksmith forges {weapon.item_name} to {weapon.forge_label()} and {weapon.additional_damage:.1f} damage.", "reward")
            self.update_stats()
            self._pulse_label(self.gold_header_lbl, "#ffffff")
            self.show_toast("WEAPON UPGRADED", self.GOLD)
            window.destroy()

        button = self._modal_button(content, "FORGE WEAPON" if cost is not None else "FORGE LIMIT REACHED", upgrade, self.GOLD, "#c99a3e")
        button.config(state=tk.NORMAL if can_afford else tk.DISABLED, bg=self.GOLD if can_afford else "#252b37", fg="#171008" if can_afford else self.MUTED)

    def visit_shop(self):
        window, content = self._modal("THE MERCHANT", "Equipment and supplies for the road ahead.", "760x540")
        shop_items = tuple({"item": entry.create_item(), "cost": entry.cost} for entry in SHOP_INVENTORY)

        self._currency_strip(content)
        body = tk.Frame(content, bg=self.SURFACE)
        body.pack(fill=tk.BOTH, expand=True, padx=22, pady=(8, 18))
        listbox = tk.Listbox(body, bg="#0b1019", fg=self.TEXT, selectbackground="#3b4d70", selectforeground="#ffffff", font=("Consolas", 11), relief=tk.FLAT, bd=0, activestyle="none")
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        details = tk.Frame(body, bg=self.SURFACE_ALT, width=260)
        details.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        details.pack_propagate(False)
        detail_name = tk.Label(details, text="SELECT AN ITEM", wraplength=220, font=("Georgia", 17, "bold"), fg=self.TEXT, bg=self.SURFACE_ALT)
        detail_name.pack(padx=18, pady=(26, 8))
        detail_desc = tk.Label(details, text="Choose merchandise to inspect.", wraplength=220, justify=tk.LEFT, font=("Arial", 10), fg=self.MUTED, bg=self.SURFACE_ALT)
        detail_desc.pack(padx=18, pady=8)
        buy_btn = self._modal_button(details, "BUY", lambda: buy_selected(), self.GOLD, "#c99a3e")
        buy_btn.config(state=tk.DISABLED)

        for entry in shop_items:
            listbox.insert(tk.END, f"  {entry['item'].item_name:<20} {entry['cost']:>4} G")

        def describe(item):
            if item.is_consumable:
                return f"Consumable\nRestores {item.heal_amount} HP"
            if item.is_armor:
                return f"{item.attributes} armor\n+{item.defense_bonus:.1f} DEF"
            return f"{item.attributes} weapon\n+{item.additional_damage:.1f} DMG"

        def on_select(_event=None):
            selection = listbox.curselection()
            if not selection:
                return
            entry = shop_items[selection[0]]
            detail_name.config(text=entry["item"].item_name)
            detail_desc.config(text=f"{describe(entry['item'])}\n\nPRICE  {entry['cost']} G")
            affordable = self.player.coins >= entry["cost"]
            buy_btn.config(state=tk.NORMAL if affordable else tk.DISABLED, text="BUY ITEM" if affordable else "NOT ENOUGH GOLD", bg=self.GOLD if affordable else "#252b37", fg="#171008" if affordable else self.MUTED)

        def buy_selected():
            selection = listbox.curselection()
            if not selection:
                return
            entry = shop_items[selection[0]]
            if not self.player.spend_coins(entry["cost"]):
                return
            source = entry["item"]
            new_item = Item(source.item_name, source.attributes, source.additional_damage, source.is_consumable, source.heal_amount, source.is_armor, source.defense_bonus, source.rarity, source.upgrade_level, source.base_damage)
            result = self.player.add_item(new_item)
            outcome = " (stacked)" if result["outcome"] == "stacked" else ""
            self.append_text(f"Purchased {new_item.item_name}{outcome} for {entry['cost']} gold.", "reward")
            self.update_stats()
            self._pulse_label(self.gold_header_lbl, "#ffffff")
            self.show_toast(f"ACQUIRED  •  {new_item.item_name.upper()}", self.GOLD)
            window.destroy()

        listbox.bind("<<ListboxSelect>>", on_select)
        listbox.bind("<Double-Button-1>", lambda _event: buy_selected())

    def show_inventory(self, equipment_only=False):
        title = "EQUIPMENT" if equipment_only else "INVENTORY"
        subtitle = "Choose what your hero carries into battle." if equipment_only else "Review, equip, or use collected items."
        window, content = self._modal(title, subtitle, "800x560")
        self._currency_strip(content)
        material_summary = ", ".join(
            f"{MATERIAL_LABELS.get(key, key.replace('_', ' ').title())} ×{amount}"
            for key, amount in sorted(self.player.materials.items()) if amount
        ) or "None collected"
        tk.Label(content, text=f"PACK CAPACITY  {self.player.inventory_slots_used}/{self.player.inventory_limit} SLOTS", font=("Arial", 8, "bold"), fg=self.BLUE, bg=self.SURFACE, anchor="w").pack(fill=tk.X, padx=24, pady=(0, 3))
        tk.Label(content, text=f"QUEST MATERIALS  •  {material_summary}", font=("Arial", 8, "bold"), fg=self.GOLD, bg=self.SURFACE, anchor="w", wraplength=730).pack(fill=tk.X, padx=24, pady=(0, 3))
        help_text = "Select an item, then choose EQUIP ITEM. Double-clicking also equips it." if equipment_only else "Select an item to inspect it. Double-click to equip or use it. ◆ marks equipped gear."
        tk.Label(content, text=help_text, font=("Arial", 9), fg="#aeb8cc", bg=self.SURFACE, anchor="w").pack(fill=tk.X, padx=24, pady=(0, 3))

        rarity_order = {"Legendary": 0, "Epic": 1, "Rare": 2, "Uncommon": 3, "Common": 4}
        candidates = sorted(
            (item for item in self.player.inventory if not equipment_only or not item.is_consumable),
            key=lambda item: (0 if item.is_consumable else 1 if item.is_armor else 2, rarity_order.get(item.rarity, 5), item.item_name.lower()),
        )
        body = tk.Frame(content, bg=self.SURFACE)
        body.pack(fill=tk.BOTH, expand=True, padx=22, pady=(8, 18))
        listbox = tk.Listbox(body, bg="#0b1019", fg=self.TEXT, selectbackground="#3b4d70", selectforeground="#ffffff", font=("Consolas", 11), relief=tk.FLAT, activestyle="none")
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        details = tk.Frame(body, bg=self.SURFACE_ALT, width=290)
        details.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        details.pack_propagate(False)
        name_lbl = tk.Label(details, text="SELECT AN ITEM", wraplength=250, font=("Georgia", 17, "bold"), fg=self.TEXT, bg=self.SURFACE_ALT)
        name_lbl.pack(padx=20, pady=(26, 8))
        type_lbl = tk.Label(details, text="", font=("Arial", 9, "bold"), fg=self.PURPLE, bg=self.SURFACE_ALT)
        type_lbl.pack()
        desc_lbl = tk.Label(details, text="Your pack is empty." if not candidates else "Choose an item to see its details.", wraplength=245, justify=tk.LEFT, font=("Arial", 10), fg=self.MUTED, bg=self.SURFACE_ALT)
        desc_lbl.pack(padx=20, pady=16)
        action_btn = self._modal_button(details, "SELECT ITEM", lambda: use_selected(), self.BLUE, "#3d8fd7")
        action_btn.config(state=tk.DISABLED)

        for item in candidates:
            marker = "◆" if item is self.player.equipped_weapon or item is self.player.equipped_armor else " "
            rarity = getattr(item, "rarity", "Common")
            quantity = f" x{item.quantity}" if item.is_consumable else ""
            listbox.insert(tk.END, f" {marker} [{rarity[0]}] {item.item_name}{quantity}")

        def item_details(item):
            if item.is_consumable:
                return "CONSUMABLE", f"{item.attributes}\n\nRestores {item.heal_amount} HP.\nQuantity: {item.quantity}"
            if item.is_armor:
                equipped = "\n\nCurrently equipped." if item is self.player.equipped_armor else ""
                current = getattr(getattr(self.player, "equipped_armor", None), "defense_bonus", 0.0)
                comparison = f"\nCompared to equipped: {item.defense_bonus - current:+.1f} DEF" if item is not self.player.equipped_armor else ""
                return "ARMOR", f"{item.attributes}\n\nDefense +{item.defense_bonus:.1f}{comparison}{equipped}"
            equipped = "\n\nCurrently equipped." if item is self.player.equipped_weapon else ""
            forge_note = f"\nForge tier {item.forge_label()} / +{item.max_upgrade_level}"
            current = getattr(getattr(self.player, "equipped_weapon", None), "additional_damage", 0.0)
            comparison = f"\nCompared to equipped: {item.additional_damage - current:+.1f} DMG" if item is not self.player.equipped_weapon else ""
            return "WEAPON", f"{item.attributes}\n\nDamage +{item.additional_damage:.1f}{comparison}{forge_note}{equipped}"

        def on_select(_event=None):
            selection = listbox.curselection()
            if not selection:
                return
            item = candidates[selection[0]]
            item_type, description = item_details(item)
            rarity = getattr(item, "rarity", "Common")
            name_lbl.config(text=item.item_name)
            type_lbl.config(text=f"{rarity.upper()}  •  {item_type}", fg=RARITY_COLORS.get(rarity, self.PURPLE))
            desc_lbl.config(text=description)
            if item.is_consumable:
                can_use = self.player.hp < self.player.max_hp
                action_btn.config(text="USE ITEM" if can_use else "HP ALREADY FULL", state=tk.NORMAL if can_use else tk.DISABLED, bg=self.GREEN if can_use else "#252b37", fg="#08110d" if can_use else self.MUTED)
            elif item is self.player.equipped_weapon or item is self.player.equipped_armor:
                action_btn.config(text="EQUIPPED", state=tk.DISABLED, bg="#252b37", fg=self.MUTED)
            else:
                action_btn.config(text="EQUIP ITEM", state=tk.NORMAL, bg=self.BLUE, fg="#ffffff")

        def use_selected():
            selection = listbox.curselection()
            if not selection:
                return
            item = candidates[selection[0]]
            if item.is_consumable:
                previous_hp = self.player.hp
                self.player.hp = min(self.player.max_hp, self.player.hp + item.heal_amount)
                self.player.consume_item(item)
                healed = self.player.hp - previous_hp
                self.append_text(f"Used {item.item_name} and restored {healed} HP.", "success")
                self.show_toast(f"RECOVERED {healed} HP", self.GREEN)
            elif item.is_armor:
                self.player.equipped_armor = item
                self.append_text(f"Equipped {item.item_name}.", "success")
                self.show_toast(f"EQUIPPED  •  {item.item_name.upper()}")
            else:
                self.player.equipped_weapon = item
                self.append_text(f"Equipped {item.item_name}.", "success")
                self.show_toast(f"EQUIPPED  •  {item.item_name.upper()}")
            self.update_stats()
            window.destroy()

        listbox.bind("<<ListboxSelect>>", on_select)
        listbox.bind("<Double-Button-1>", lambda _event: use_selected())

    def equip_weapon(self):
        self.show_inventory(equipment_only=True)

    def show_settings(self):
        window, content = self._modal("AUDIO, SETTINGS & PLAYER STATS", "Audio controls are always available from the bottom bar or F10.", "900x680")
        body = tk.Frame(content, bg=self.SURFACE)
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=18)

        difficulty = tk.StringVar(value=settings.get("difficulty"))
        text_speed = tk.StringVar(value=settings.get("text_speed"))
        display_mode = tk.StringVar(value=settings.get("display_mode"))
        reduce_animations = tk.BooleanVar(value=settings.get("reduce_animations"))
        music_volume = tk.DoubleVar(value=settings.get("music_volume") * 100)
        sfx_volume = tk.DoubleVar(value=settings.get("sfx_volume") * 100)
        original_music_volume = settings.get("music_volume")
        original_sfx_volume = settings.get("sfx_volume")

        weapon_damage = getattr(getattr(self.player, "equipped_weapon", None), "additional_damage", 0.0)
        armor_defense = getattr(getattr(self.player, "equipped_armor", None), "defense_bonus", 0.0)
        attack_power = 15 + self.player.level * 5 + int(weapon_damage)
        stats = tk.Frame(body, bg="#0b1019", highlightbackground=self.BORDER, highlightthickness=1)
        stats.pack(fill=tk.X, pady=(0, 12))
        tk.Label(stats, text="PLAYER STATS", bg="#0b1019", fg=self.GOLD, font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=(16, 20), pady=13)
        stat_text = (
            f"{self.player.name}  |  LV {self.player.level} {class_name(self.player).upper()}  |  "
            f"HP {self.player.hp}/{self.player.max_hp}  |  MP {self.player.mana}/100  |  "
            f"ATK {attack_power}  |  DEF {armor_defense:.0f}  |  GOLD {self.player.coins}"
        )
        tk.Label(stats, text=stat_text, bg="#0b1019", fg=self.TEXT, font=("Consolas", 9, "bold")).pack(side=tk.LEFT, pady=13)

        top_settings = tk.Frame(body, bg=self.SURFACE)
        top_settings.pack(fill=tk.X)
        general = tk.LabelFrame(top_settings, text=" GAMEPLAY & ACCESSIBILITY ", bg=self.SURFACE_ALT, fg=self.GOLD, font=("Arial", 9, "bold"), bd=1, relief=tk.FLAT, width=400, height=150)
        general.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        general.pack_propagate(False)

        def option_row(row, label, variable, values):
            tk.Label(general, text=label, bg=self.SURFACE_ALT, fg=self.TEXT, font=("Arial", 9, "bold")).grid(row=row, column=0, sticky="w", padx=14, pady=7)
            menu = tk.OptionMenu(general, variable, *values)
            menu.config(bg="#253149", fg="#ffffff", activebackground="#354461", activeforeground="#ffffff", relief=tk.FLAT, width=14, highlightthickness=0)
            menu["menu"].config(bg="#253149", fg="#ffffff")
            menu.grid(row=row, column=1, sticky="w", padx=10, pady=5)

        option_row(0, "Difficulty", difficulty, ("Easy", "Normal", "Hard"))
        option_row(1, "Text speed", text_speed, ("Fast", "Normal", "Slow"))
        option_row(2, "Display", display_mode, ("Windowed", "Fullscreen"))
        tk.Checkbutton(general, text="Reduce movement, particles, and transition animations", variable=reduce_animations, bg=self.SURFACE_ALT, fg=self.TEXT, selectcolor="#253149", activebackground=self.SURFACE_ALT, activeforeground="#ffffff", font=("Arial", 9)).grid(row=3, column=0, columnspan=4, sticky="w", padx=12, pady=7)

        audio = tk.LabelFrame(top_settings, text=" AUDIO VOLUME ", bg="#171426", fg=self.PURPLE, font=("Arial", 10, "bold"), bd=1, relief=tk.FLAT, width=420, height=150)
        audio.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))
        audio.pack_propagate(False)

        def live_audio(_value=None):
            audio_manager.configure(music_volume.get() / 100.0, sfx_volume.get() / 100.0)

        tk.Label(audio, text="MUSIC", bg="#171426", fg=self.TEXT, font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", padx=(14, 4), pady=(8, 2))
        tk.Scale(audio, variable=music_volume, command=live_audio, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, bg="#171426", fg=self.TEXT, troughcolor="#4b315f", activebackground=self.PURPLE, highlightthickness=0, length=255, showvalue=True).grid(row=0, column=1, padx=4, pady=(3, 0))
        tk.Label(audio, text="SOUND FX", bg="#171426", fg=self.TEXT, font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="w", padx=(14, 4), pady=2)
        tk.Scale(audio, variable=sfx_volume, command=live_audio, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL, bg="#171426", fg=self.TEXT, troughcolor="#4b315f", activebackground=self.PURPLE, highlightthickness=0, length=255, showvalue=True).grid(row=1, column=1, padx=4)
        tk.Button(audio, text="TEST SOUND", command=lambda: (live_audio(), audio_manager.play_sound("skill")), bg="#63369a", fg="#ffffff", activebackground="#8550c5", activeforeground="#ffffff", relief=tk.FLAT, font=("Arial", 8, "bold"), padx=14, pady=5).grid(row=2, column=1, sticky="e", padx=16, pady=(0, 8))

        controls = tk.LabelFrame(body, text=" REMAPPABLE CONTROLS ", bg=self.SURFACE_ALT, fg=self.BLUE, font=("Arial", 9, "bold"), bd=1, relief=tk.FLAT)
        controls.pack(fill=tk.BOTH, expand=True, pady=(14, 0))
        labels = {
            "walk_forward": "Move forward", "walk_back": "Move back", "walk_left": "Move left", "walk_right": "Move right",
            "inventory": "Inventory", "equip": "Equipment", "region_map": "Region map", "quest_log": "Quest log", "options": "Options",
            "battle_attack": "Battle: Attack", "battle_defend": "Battle: Defend", "battle_item": "Battle: Item", "battle_skill": "Battle: Skill", "battle_escape": "Battle: Escape",
        }
        key_vars = {}
        for index, (action, label) in enumerate(labels.items()):
            column_group, row = divmod(index, 7)
            base_column = column_group * 2
            tk.Label(controls, text=label, bg=self.SURFACE_ALT, fg=self.TEXT, font=("Arial", 9)).grid(row=row, column=base_column, sticky="w", padx=(15, 6), pady=6)
            key_vars[action] = tk.StringVar(value=settings.key(action))
            tk.Entry(controls, textvariable=key_vars[action], width=12, justify=tk.CENTER, bg="#0b1019", fg="#ffffff", insertbackground="#ffffff", relief=tk.FLAT).grid(row=row, column=base_column + 1, padx=(4, 22), pady=6)

        status = tk.Label(body, text="Arrow keys remain available for movement.", bg=self.SURFACE, fg=self.MUTED, font=("Arial", 8))
        status.pack(side=tk.LEFT, pady=12)

        def save_changes():
            clean_keys = {action: value.get().strip() for action, value in key_vars.items()}
            if any(not value or len(value) > 12 for value in clean_keys.values()):
                messagebox.showerror("Invalid controls", "Each control needs a key name of 1 to 12 characters.", parent=window)
                return
            action_names = list(labels)
            adventure = [clean_keys[action].lower() for action in action_names[:9]]
            battle = [clean_keys[action].lower() for action in action_names[9:]]
            if len(adventure) != len(set(adventure)) or len(battle) != len(set(battle)):
                messagebox.showerror("Duplicate controls", "Controls on the same screen must use different keys.", parent=window)
                return
            settings.save({
                "difficulty": difficulty.get(), "text_speed": text_speed.get(),
                "display_mode": display_mode.get(), "reduce_animations": reduce_animations.get(),
                "music_volume": music_volume.get() / 100.0, "sfx_volume": sfx_volume.get() / 100.0,
                "keybindings": clean_keys,
            })
            audio_manager.configure(settings.get("music_volume"), settings.get("sfx_volume"))
            apply_display_mode(self.winfo_toplevel(), settings.get("display_mode"))
            self._bind_shortcuts()
            self.append_text(f"Settings saved. Difficulty is now {settings.get('difficulty')}.", "success")
            self.show_toast("SETTINGS SAVED")
            window.destroy()

        def close_without_saving():
            audio_manager.configure(original_music_volume, original_sfx_volume)
            window.destroy()

        tk.Button(body, text="SAVE SETTINGS", command=save_changes, bg=self.GOLD, fg="#171008", activebackground="#e4b94f", relief=tk.FLAT, font=("Arial", 10, "bold"), padx=24, pady=10).pack(side=tk.RIGHT, pady=10)
        window.protocol("WM_DELETE_WINDOW", close_without_saving)
        window.bind("<Escape>", lambda _event: close_without_saving())

    def show_options(self):
        window, content = self._modal("OPTIONS & GUIDE", "Everything you need to continue the journey.", "900x620")
        window.bind("<Escape>", lambda _event: window.destroy())

        tabs = tk.Frame(content, bg=self.SURFACE_ALT, height=54)
        tabs.pack(fill=tk.X, padx=18, pady=(18, 0))
        tabs.pack_propagate(False)
        viewer = tk.Text(
            content,
            state=tk.DISABLED,
            wrap=tk.WORD,
            bg="#0b1019",
            fg="#dce3f2",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=24,
            pady=20,
            spacing1=4,
            spacing3=8,
        )
        viewer.pack(fill=tk.BOTH, expand=True, padx=18, pady=(10, 18))
        viewer.tag_configure("title", font=("Georgia", 18, "bold"), foreground=self.GOLD, spacing3=12)
        viewer.tag_configure("heading", font=("Arial", 11, "bold"), foreground=self.BLUE, spacing1=10, spacing3=4)
        viewer.tag_configure("key", font=("Consolas", 10, "bold"), foreground=self.GREEN)
        viewer.tag_configure("body", foreground="#c8d0e1")
        viewer.tag_configure("note", foreground=self.PURPLE)

        skill_guide = [("CLASS SKILLS\n", "title")]
        skill_guide.append(("All class skills gain +20% power at level 12 (Mastery II) and +40% power at level 15 (Mastery III).\n", "note"))
        for data in CLASS_SKILLS.values():
            skill_guide.append((f"{data['name']}\n", "heading"))
            skill_guide.append((f"{data['identity']}\n", "body"))
            for skill in data["skills"]:
                skill_guide.append((f"LV {skill.unlock_level}  {skill.name}  •  {skill.mp_cost} MP\n", "key"))
                skill_guide.append((f"{skill.description}\n", "body"))

        pages = {
            "GUIDE": [
                ("SWORD PHANTASIA GUIDE\n", "title"),
                ("Exploration\n", "heading"),
                ("Travel can lead to battles or region-specific events: treasure caches, materials, landmarks, NPC decisions, shrines, traps, and wandering merchants. Explore favors discoveries and battles over quiet results.\n", "body"),
                ("Resting\n", "heading"),
                ("Rest restores up to 10 HP and 10 MP. It cannot raise either resource beyond its maximum.\n", "body"),
                ("Combat\n", "heading"),
                ("Attack uses your equipped weapon. Defend halves the remaining incoming damage and restores MP. Skills have individual costs and cooldowns, and exploit heavy enemy attacks. Items restore HP during battle.\n", "body"),
                ("Defeat\n", "heading"),
                ("Defeat never closes the game. Retry the same encounter, return to camp with a 15% gold penalty, load the last save, or return to the title screen.\n", "body"),
                ("Progression\n", "heading"),
                ("Defeating monsters awards EXP and gold. Leveling increases maximum HP and fully restores HP. After level 10, EXP requirements rise and ascended enemies begin appearing. Class Mastery improves at levels 12 and 15.\n", "body"),
                ("Region Champions\n", "heading"),
                ("Complete each region's main quest to challenge its champion. Defeat all three champions to break the seals protecting Demon King Koji. Each champion grants a unique legendary relic.\n", "body"),
                ("Regional Loot\n", "heading"),
                ("Every region has distinct weapons, armor, consumables, and rare drops. Ascended enemies have a higher drop chance.\n", "body"),
                ("Quest Variety\n", "heading"),
                ("Quest objectives include combat, gathering materials, discovering landmarks, surviving regional encounters, guarded victories, and persistent story decisions.\n", "body"),
                ("Saving\n", "heading"),
                ("The game automatically saves after encounters. Use SAVE GAME from the adventure bar whenever you want to save manually.\n", "body"),
            ],
            "EQUIPMENT": [
                ("EQUIPMENT & ITEMS\n", "title"),
                ("Equipping Gear\n", "heading"),
                ("Choose EQUIPMENT from the bottom bar or press E. Select a weapon or armor piece, then choose EQUIP ITEM. You can also double-click it. A ◆ marker identifies equipped gear.\n", "body"),
                ("Inventory\n", "heading"),
                ("Choose INVENTORY or press I to inspect everything you carry. Consumables show USE ITEM instead of EQUIP ITEM. Potions cannot be consumed when HP is already full.\n", "body"),
                ("Weapons and Armor\n", "heading"),
                ("Weapons increase attack damage. Armor reduces incoming damage. The hero sprite represents the weapon selected during character creation, even when different loot is equipped later.\n", "body"),
                ("Merchant\n", "heading"),
                ("The merchant sells weapons, armor, and healing supplies. Select merchandise to compare its effect and price before buying.\n", "body"),
                ("Blacksmith\n", "heading"),
                ("The blacksmith advances weapons through five forge tiers. Each tier adds 15% of base damage, and costs rise with tier, base strength, and rarity. Legacy weapons above +5 keep their damage but cannot be upgraded further.\n", "body"),
            ],
            "CONTROLS": [
                ("CONTROL REFERENCE\n", "title"),
                ("Adventure Screen\n", "heading"),
                ("W / Up Arrow", "key"), ("   Move forward\n", "body"),
                ("S / Down Arrow", "key"), ("   Move back\n", "body"),
                ("A / Left Arrow", "key"), ("   Move left\n", "body"),
                ("D / Right Arrow", "key"), ("   Move right\n", "body"),
                ("I", "key"), ("   Open Inventory\n", "body"),
                ("E", "key"), ("   Open Equipment\n", "body"),
                ("M", "key"), ("   Open Region Map\n", "body"),
                ("Q", "key"), ("   Open Quest Log\n", "body"),
                ("Escape", "key"), ("   Open or close Options\n", "body"),
                ("F10", "key"), ("   Open Audio, Settings, and Player Stats\n", "body"),
                ("Battle Screen\n", "heading"),
                ("A", "key"), ("   Attack\n", "body"),
                ("D", "key"), ("   Defend\n", "body"),
                ("I", "key"), ("   Use an item\n", "body"),
                ("S", "key"), ("   Use arcane skill\n", "body"),
                ("R", "key"), ("   Attempt to escape\n", "body"),
                ("Menus and Results\n", "heading"),
                ("Double-click", "key"), ("   Equip, use, or purchase a selected item\n", "body"),
                ("Enter / Space", "key"), ("   Continue from the victory screen\n", "body"),
            ],
            "SKILLS": skill_guide,
            "WORLD": [
                ("THE REALM\n", "title"),
                ("Frontier Plains  •  Level 1\n", "heading"),
                ("Slimes regenerate and use corrosive attacks. Complete The Slime Tide to earn supplies for the road.\n", "body"),
                ("Mosswood Wilds  •  Level 3\n", "heading"),
                ("Goblins ambush travelers and can steal gold. Break their warband to earn Mossguard armor.\n", "body"),
                ("Ashen Crypt  •  Level 6\n", "heading"),
                ("Skeletons use heavy counters and Bone Guard. Silence the restless dead to claim an ancient weapon.\n", "body"),
                ("Primordial Throne  •  Level 10\n", "heading"),
                ("Travel here through the Region Map to unlock the final confrontation with Demon King Koji.\n", "body"),
                ("Enemy Intents\n", "heading"),
                ("The battle target panel reveals the enemy's next action. Use this warning to choose between attacking, defending, healing, or using a class skill.\n", "note"),
            ],
            "FINAL BOSS": [
                ("THE PRIMORDIAL THRONE\n", "title"),
                ("Unlocking the Battle\n", "heading"),
                ("Reach level 10. The locked objective on the right side of the adventure screen will become CHALLENGE DEMON KING.\n", "body"),
                ("Preparing\n", "heading"),
                ("Bring healing items, upgrade your strongest weapon, equip armor, restore HP and MP, and save before entering.\n", "body"),
                ("Warning\n", "heading"),
                ("Demon King Koji has 500 HP, deals heavy damage, and cannot be escaped once the final battle begins.\n", "note"),
            ],
            "SAVE GAME": [
                ("SAVE YOUR JOURNEY\n", "title"),
                ("Manual Save\n", "heading"),
                ("Create an up-to-date save containing your level, EXP, gold, health, mana, inventory, and equipped gear. The existing save file will be updated.\n", "body"),
                ("Autosave\n", "heading"),
                ("The game automatically saves after ordinary encounters. Saving manually is recommended before shopping, upgrading equipment, or entering the Primordial Throne.\n", "body"),
            ],
        }

        save_area = tk.Frame(content, bg="#171e2d", highlightbackground=self.BORDER, highlightthickness=1)
        save_summary = tk.Label(
            save_area,
            text=f"{self.player.name}  •  LEVEL {self.player.level}  •  {self.location_name}\nHP {self.player.hp}/{self.player.max_hp}    MP {self.player.mana}/100    GOLD {self.player.coins}",
            justify=tk.LEFT,
            font=("Consolas", 10, "bold"),
            fg="#dce3f2",
            bg="#171e2d",
        )
        save_summary.pack(side=tk.LEFT, padx=18, pady=15)
        save_result = tk.Label(save_area, text="", font=("Arial", 9, "bold"), fg=self.GREEN, bg="#171e2d")
        save_result.pack(side=tk.RIGHT, padx=12)

        def save_from_options():
            self.player.save_to_file()
            self.save_status_lbl.config(text="SAVED", fg=self.GREEN)
            self.append_text("Journey progress saved from Options.", "success")
            self.show_toast("GAME SAVED")
            save_result.config(text="SAVE COMPLETE")

        save_button = tk.Button(save_area, text="SAVE NOW", command=save_from_options, bg=self.GOLD, fg="#171008", activebackground="#e4b94f", activeforeground="#171008", relief=tk.FLAT, bd=0, font=("Arial", 10, "bold"), cursor="hand2", padx=20, pady=10)
        save_button.pack(side=tk.RIGHT, padx=12, pady=12)
        title_button = tk.Button(save_area, text="RETURN TO TITLE", command=lambda: self.return_to_title(parent=window), bg="#2b3852", fg="#ffffff", activebackground="#405274", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Arial", 9, "bold"), cursor="hand2", padx=16, pady=10)
        title_button.pack(side=tk.RIGHT, padx=4, pady=12)
        quit_button = tk.Button(save_area, text="QUIT GAME", command=lambda: self.quit_game(parent=window), bg="#54232c", fg="#ffffff", activebackground="#7d303d", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Arial", 9, "bold"), cursor="hand2", padx=16, pady=10)
        quit_button.pack(side=tk.RIGHT, padx=4, pady=12)

        tab_buttons = {}

        def show_page(name):
            viewer.config(state=tk.NORMAL)
            viewer.delete("1.0", tk.END)
            for text, tag in pages[name]:
                viewer.insert(tk.END, text, tag)
            viewer.config(state=tk.DISABLED)
            for tab_name, button in tab_buttons.items():
                selected = tab_name == name
                button.config(bg="#30415e" if selected else self.SURFACE_ALT, fg="#ffffff" if selected else self.MUTED)
            if name == "SAVE GAME":
                save_area.pack(side=tk.BOTTOM, fill=tk.X, padx=18, pady=(0, 18), before=viewer)
            else:
                save_area.pack_forget()

        for column, name in enumerate(pages):
            button = tk.Button(tabs, text=name, command=lambda page=name: show_page(page), bg=self.SURFACE_ALT, fg=self.MUTED, activebackground="#30415e", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Arial", 8, "bold"), cursor="hand2", padx=4)
            button.grid(row=0, column=column, sticky="nsew", padx=1)
            tabs.grid_columnconfigure(column, weight=1, uniform="options_tab")
            tabs.grid_rowconfigure(0, weight=1)
            tab_buttons[name] = button
        show_page("GUIDE")

    def _modal(self, title, subtitle, geometry):
        window = tk.Toplevel(self)
        window.title(title.title())
        window.geometry(geometry)
        window.configure(bg=self.BG)
        window.transient(self.winfo_toplevel())
        window.grab_set()
        window.resizable(False, False)
        window.update_idletasks()
        width, height = (int(value) for value in geometry.split("x", 1))
        parent = self.winfo_toplevel()
        x = parent.winfo_rootx() + max(0, (parent.winfo_width() - width) // 2)
        y = parent.winfo_rooty() + max(0, (parent.winfo_height() - height) // 2)
        window.geometry(f"{geometry}+{x}+{y}")
        header = tk.Frame(window, bg="#0d131e", height=78, highlightbackground=self.BORDER, highlightthickness=1)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        copy = tk.Frame(header, bg="#0d131e")
        copy.pack(side=tk.LEFT, padx=24, pady=13)
        tk.Label(copy, text=title, font=("Georgia", 17, "bold"), fg=self.TEXT, bg="#0d131e").pack(anchor="w")
        tk.Label(copy, text=subtitle, font=("Arial", 9), fg=self.MUTED, bg="#0d131e").pack(anchor="w")
        tk.Button(header, text="×", command=window.destroy, bg="#0d131e", fg=self.MUTED, activebackground="#54232c", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Arial", 18), cursor="hand2").pack(side=tk.RIGHT, padx=18)
        content = tk.Frame(window, bg=self.SURFACE)
        content.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        return window, content

    def _currency_strip(self, parent):
        strip = tk.Frame(parent, bg=self.SURFACE_ALT, height=45)
        strip.pack(fill=tk.X, padx=22, pady=(18, 8))
        strip.pack_propagate(False)
        tk.Label(strip, text="AVAILABLE GOLD", font=("Arial", 8, "bold"), fg=self.MUTED, bg=self.SURFACE_ALT).pack(side=tk.LEFT, padx=14)
        tk.Label(strip, text=f"◆ {self.player.coins} G", font=("Consolas", 11, "bold"), fg=self.GOLD, bg=self.SURFACE_ALT).pack(side=tk.RIGHT, padx=14)

    def _modal_button(self, parent, text, command, color, hover):
        button = tk.Button(parent, text=text, command=command, bg=color, fg="#ffffff", activebackground=hover, activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Arial", 10, "bold"), cursor="hand2", pady=11)
        button.bind("<Enter>", lambda event: event.widget.config(bg=hover) if event.widget["state"] != tk.DISABLED else None)
        button.bind("<Leave>", lambda event: event.widget.config(bg=color) if event.widget["state"] != tk.DISABLED else None)
        button.pack(side=tk.BOTTOM, fill=tk.X, padx=18, pady=18)
        return button

    def action_performed(self, command):
        button = self.btn_dict.get(command)
        if button and str(button["state"]) == str(tk.DISABLED):
            hint = getattr(button, "hint", "That action is currently unavailable.")
            self.show_toast(hint.upper(), self.RED)
            return
        if button:
            original = button.cget("bg")
            flash = getattr(button, "hover_color", "#405173")
            button.config(bg=flash)
            self.after(120, lambda: button.config(bg=original) if button.winfo_exists() and button["state"] != tk.DISABLED else None)

        if command.startswith("Walk"):
            direction = command.replace("Walk ", "").lower()
            region = current_region(self.player)
            self.location_name, self.location_description = region.locations[direction]
            self.append_text(f"You travel {direction} and arrive at {self.location_name}.", "travel")
            self.update_stats()
            roll = random.randint(1, 100)
            if roll <= 18:
                self.encounter_monster()
            elif roll <= 43:
                self.resolve_exploration_event()
        elif command == "Explore":
            self.append_text(f"You search the surroundings of {self.location_name}.", "travel")
            roll = random.randint(1, 100)
            if roll <= 45:
                self.resolve_exploration_event()
            elif roll <= 85:
                self.encounter_monster()
            else:
                quiet_lines = (
                    "The wind shifts, but nothing answers your search.",
                    "You find old tracks that disappear before the next ridge.",
                    "For a rare moment, the road is quiet.",
                    "Distant bells echo once, then fade.",
                )
                self.append_text(random.choice(quiet_lines), "system")
        elif command == "Rest":
            self.rest()
        elif command == "Region Map":
            self.show_region_map()
        elif command == "Quest Log":
            self.show_quest_log()
        elif command == "Blacksmith":
            self.visit_blacksmith()
        elif command == "Shop":
            self.visit_shop()
        elif command == "Inventory":
            self.show_inventory()
        elif command == "Equip":
            self.equip_weapon()
        elif command == "Options":
            self.show_options()
        elif command == "Settings":
            self.show_settings()
        elif command == "Save Game":
            self.player.save_to_file()
            self.save_status_lbl.config(text="SAVED", fg=self.GREEN)
            self.append_text("Journey progress saved.", "success")
            self.show_toast("GAME SAVED")
        elif command == "Challenge Demon King":
            self.challenge_final_boss()
        elif command == "Challenge Region Champion":
            self.challenge_region_champion()
        elif command == "Quit":
            self.quit_game()

    def return_to_title(self, parent=None):
        confirmed = messagebox.askyesno(
            "Return to Title?",
            "Return to the title screen? Unsaved progress will be lost.",
            parent=parent or self,
        )
        if not confirmed:
            return
        root = self.winfo_toplevel()
        if parent and parent.winfo_exists():
            parent.destroy()
        self.destroy()
        from main_menu import MainMenu
        MainMenu(root)

    def quit_game(self, parent=None):
        confirmed = messagebox.askyesno(
            "Leave Sword Phantasia?",
            "Quit the game? Unsaved progress will be lost.",
            parent=parent or self,
        )
        if confirmed:
            self.winfo_toplevel().destroy()

    def destroy(self):
        root = self.winfo_toplevel()
        for sequence in getattr(self, "_shortcut_sequences", ()):
            try:
                root.unbind(sequence)
            except tk.TclError:
                pass
        if self._toast_job:
            try:
                self.after_cancel(self._toast_job)
            except tk.TclError:
                pass
        for job in self._bar_jobs.values():
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
        self._bar_jobs.clear()
        super().destroy()

    def challenge_final_boss(self):
        if self.player.level < 10:
            self.show_toast("REACH LEVEL 10 FIRST", self.RED)
            return
        if self.player.current_region != "throne":
            self.show_toast("TRAVEL TO THE PRIMORDIAL THRONE", self.PURPLE)
            return
        if not all_minibosses_defeated(self.player):
            remaining = 3 - len(defeated_miniboss_keys(self.player))
            self.show_toast(f"DEFEAT {remaining} REGION CHAMPION{'S' if remaining != 1 else ''}", self.GOLD)
            return
        choice = messagebox.askyesno(
            "The Primordial Throne",
            "Demon King Koji awaits beyond this point.\n\nBegin the final battle?",
            parent=self,
        )
        if choice:
            self.fight_final_boss()

    def challenge_region_champion(self):
        boss = miniboss_for_region(self.player)
        if not boss:
            self.show_toast("NO REGION CHAMPION AVAILABLE", self.RED)
            return
        choice = messagebox.askyesno(
            "Region Champion",
            f"{boss.name} answers your challenge.\n\nChampion battles cannot be escaped. Begin?",
            parent=self,
        )
        if not choice:
            return
        self.append_text(f"{boss.name}, champion of this region, emerges!", "special")
        battle = self._run_battle(monster_spec=boss, is_miniboss=True)
        if battle is None:
            return
        if battle.victory:
            self.append_text(f"{boss.name} has fallen. Its seal on the Primordial Throne breaks.", "reward")
            self.player.save_to_file()
            self.save_status_lbl.config(text="AUTOSAVED", fg=self.GREEN)
            self.show_toast("REGION CHAMPION DEFEATED", self.GOLD)
        else:
            self.append_text(f"You withdraw from {boss.name}.", "warning")
        self.update_stats()

    def fight_final_boss(self):
        self.append_text("The gates of the Primordial Throne open.", "special")
        battle = self._run_battle(is_boss=True)
        if battle is None:
            return
        if not battle.victory:
            self.append_text("You withdraw from the Primordial Throne.", "warning")
            self.update_stats()
            return
        self.append_text("Demon King Koji has fallen. The realm is free.", "reward")
        self.player.save_to_file()
        root = self.winfo_toplevel()
        credits = EndCreditsScreen(root, self.player)
        if credits.result == "title":
            self.destroy()
            from main_menu import MainMenu
            MainMenu(root)
        else:
            root.destroy()
