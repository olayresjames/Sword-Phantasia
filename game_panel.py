import random
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from battle_panel import BattlePanel, hero_sprite_path
from item import Item


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

    LOCATIONS = {
        "forward": ("Whispering Road", "A weathered road winds toward distant ruins."),
        "back": ("Frontier Camp", "A quiet campfire marks the edge of the known realm."),
        "left": ("Mosswood Edge", "Ancient trees crowd around a shadowed trail."),
        "right": ("Sunken Trail", "Broken stones descend into a mist-covered valley."),
    }

    def __init__(self, parent, player):
        super().__init__(parent, bg=self.BG)
        self.player = player
        self.location_name = "Frontier Crossroads"
        self.location_description = "Four roads diverge beneath an unsettled sky."
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
        self.level_lbl = tk.Label(panel, font=("Arial", 10, "bold"), fg=self.GOLD, bg=self.SURFACE)
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

        self._section_label(panel, "SETTLEMENT")
        settlement = tk.Frame(panel, bg=self.SURFACE)
        settlement.pack(fill=tk.X, padx=13)
        self._action_button(settlement, "SHOP", "Shop", 0, 0, "Purchase equipment and supplies")
        self._action_button(settlement, "SMITH", "Blacksmith", 0, 1, "Upgrade your equipped weapon")

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
        self.boss_btn.pack(fill=tk.X, padx=18, pady=(20, 8))
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
        bindings = {
            "<KeyPress-w>": "Walk Forward",
            "<KeyPress-Up>": "Walk Forward",
            "<KeyPress-s>": "Walk Back",
            "<KeyPress-Down>": "Walk Back",
            "<KeyPress-a>": "Walk Left",
            "<KeyPress-Left>": "Walk Left",
            "<KeyPress-d>": "Walk Right",
            "<KeyPress-Right>": "Walk Right",
            "<KeyPress-i>": "Inventory",
            "<KeyPress-e>": "Equip",
            "<Escape>": "Options",
        }
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
        self.level_lbl.config(text=f"LEVEL {self.player.level}")
        self.gold_header_lbl.config(text=f"◆ {self.player.coins} G")
        self.hp_lbl.config(text=f"{max(0, self.player.hp)} / {self.player.max_hp}")
        self._animate_bar(self.hp_bar, max(0, self.player.hp), self.player.max_hp)
        self.mana_lbl.config(text=f"{self.player.mana} / 100")
        self._animate_bar(self.mana_bar, self.player.mana, 100)
        self.xp_lbl.config(text=f"{self.player.experience} / 100")
        self._animate_bar(self.xp_bar, self.player.experience, 100)
        self.weapon_lbl.config(text=weapon.item_name if weapon else "None")
        self.armor_lbl.config(text=armor.item_name if armor else "None")
        self.location_lbl.config(text=self.location_name)
        self.location_desc_lbl.config(text=self.location_description)

        equippables = [item for item in self.player.inventory if not getattr(item, "is_consumable", False)]
        self._set_button_state("Equip", bool(equippables), "No equipment available")
        self._set_button_state("Blacksmith", weapon is not None, "Equip a weapon to use the smith")

        boss_ready = self.player.level >= 10
        if boss_ready:
            self.boss_btn.config(text="CHALLENGE DEMON KING", state=tk.NORMAL, bg="#663795", fg="#ffffff")
            self.boss_btn.bind("<Enter>", lambda event: event.widget.config(bg="#8750bc"))
            self.boss_btn.bind("<Leave>", lambda event: event.widget.config(bg="#663795"))
            self.objective_lbl.config(text="Enter the Primordial Throne and defeat Demon King Koji")
        else:
            self.boss_btn.config(text=f"FINAL OBJECTIVE  •  LEVEL {self.player.level}/10", state=tk.DISABLED, bg="#191e2a", fg="#68738d")
            self.objective_lbl.config(text=f"Reach level 10 to challenge Demon King Koji  •  {self.player.level}/10")

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
        steps = 10

        def advance(step=1):
            bar["value"] = start + (target - start) * step / steps
            if step < steps:
                self._bar_jobs[str(bar)] = self.after(24, lambda: advance(step + 1))
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
        self.append_text("A hostile presence emerges from the wilds!", "warning")
        BattlePanel(self.winfo_toplevel(), self.player)
        self.append_text("You return from battle alive.", "success")
        self.player.save_to_file()
        self.save_status_lbl.config(text="AUTOSAVED", fg=self.GREEN)
        self.show_toast("GAME AUTOSAVED")
        self.update_stats()

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

    def visit_blacksmith(self):
        weapon = getattr(self.player, "equipped_weapon", None)
        if not weapon:
            self.show_toast("EQUIP A WEAPON FIRST", self.RED)
            return
        window, content = self._modal("THE BLACKSMITH", "Temper steel. Sharpen destiny.", "600x430")
        tk.Label(content, text="EQUIPPED WEAPON", font=("Arial", 9, "bold"), fg=self.MUTED, bg=self.SURFACE).pack(anchor="w", padx=28, pady=(24, 5))
        tk.Label(content, text=weapon.item_name, font=("Georgia", 24, "bold"), fg=self.TEXT, bg=self.SURFACE).pack(anchor="w", padx=28)

        comparison = tk.Frame(content, bg=self.SURFACE_ALT)
        comparison.pack(fill=tk.X, padx=28, pady=22)
        current = weapon.additional_damage
        upgraded = current * 1.20
        tk.Label(comparison, text=f"CURRENT\n{current:.1f} DMG", font=("Consolas", 12, "bold"), fg=self.MUTED, bg=self.SURFACE_ALT, justify=tk.CENTER).pack(side=tk.LEFT, expand=True, pady=18)
        tk.Label(comparison, text="➜", font=("Arial", 20, "bold"), fg=self.GOLD, bg=self.SURFACE_ALT).pack(side=tk.LEFT)
        tk.Label(comparison, text=f"AFTER UPGRADE\n{upgraded:.1f} DMG", font=("Consolas", 12, "bold"), fg=self.GREEN, bg=self.SURFACE_ALT, justify=tk.CENTER).pack(side=tk.LEFT, expand=True, pady=18)

        can_afford = self.player.coins >= 50
        cost_lbl = tk.Label(content, text=f"COST  50 G    •    FUNDS  {self.player.coins} G", font=("Arial", 10, "bold"), fg=self.GOLD if can_afford else self.RED, bg=self.SURFACE)
        cost_lbl.pack()

        def upgrade():
            if not self.player.spend_coins(50):
                return
            weapon.apply_upgrades(20)
            self.append_text(f"The blacksmith upgrades {weapon.item_name} to {weapon.additional_damage:.1f} damage.", "reward")
            self.update_stats()
            self._pulse_label(self.gold_header_lbl, "#ffffff")
            self.show_toast("WEAPON UPGRADED", self.GOLD)
            window.destroy()

        button = self._modal_button(content, "UPGRADE WEAPON", upgrade, self.GOLD, "#c99a3e")
        button.config(state=tk.NORMAL if can_afford else tk.DISABLED, bg=self.GOLD if can_afford else "#252b37", fg="#171008" if can_afford else self.MUTED)

    def visit_shop(self):
        window, content = self._modal("THE MERCHANT", "Equipment and supplies for the road ahead.", "760x540")
        shop_items = [
            {"item": Item("Iron Sword", "Sturdy", 15.0), "cost": 30},
            {"item": Item("Steel Axe", "Heavy", 20.0), "cost": 50},
            {"item": Item("Excalibur", "Legendary", 50.0), "cost": 200},
            {"item": Item("Healing Potion", "Consumable", 0.0, is_consumable=True, heal_amount=50), "cost": 15},
            {"item": Item("Leather Armor", "Light", 0.0, is_armor=True, defense_bonus=5.0), "cost": 40},
            {"item": Item("Iron Armor", "Sturdy", 0.0, is_armor=True, defense_bonus=12.0), "cost": 100},
        ]

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
            new_item = Item(source.item_name, source.attributes, source.additional_damage, source.is_consumable, source.heal_amount, source.is_armor, source.defense_bonus)
            self.player.inventory.append(new_item)
            self.append_text(f"Purchased {new_item.item_name} for {entry['cost']} gold.", "reward")
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
        help_text = "Select an item, then choose EQUIP ITEM. Double-clicking also equips it." if equipment_only else "Select an item to inspect it. Double-click to equip or use it. ◆ marks equipped gear."
        tk.Label(content, text=help_text, font=("Arial", 9), fg="#aeb8cc", bg=self.SURFACE, anchor="w").pack(fill=tk.X, padx=24, pady=(0, 3))

        candidates = [item for item in self.player.inventory if not equipment_only or not item.is_consumable]
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
            listbox.insert(tk.END, f" {marker} {item.item_name}")

        def item_details(item):
            if item.is_consumable:
                return "CONSUMABLE", f"{item.attributes}\n\nRestores {item.heal_amount} HP."
            if item.is_armor:
                equipped = "\n\nCurrently equipped." if item is self.player.equipped_armor else ""
                return "ARMOR", f"{item.attributes}\n\nDefense +{item.defense_bonus:.1f}{equipped}"
            equipped = "\n\nCurrently equipped." if item is self.player.equipped_weapon else ""
            return "WEAPON", f"{item.attributes}\n\nDamage +{item.additional_damage:.1f}{equipped}"

        def on_select(_event=None):
            selection = listbox.curselection()
            if not selection:
                return
            item = candidates[selection[0]]
            item_type, description = item_details(item)
            name_lbl.config(text=item.item_name)
            type_lbl.config(text=item_type)
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
                self.player.inventory.remove(item)
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

    def show_options(self):
        window, content = self._modal("OPTIONS & GUIDE", "Everything you need to continue the journey.", "820x590")
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

        pages = {
            "GUIDE": [
                ("SWORD PHANTASIA GUIDE\n", "title"),
                ("Exploration\n", "heading"),
                ("Travel with the directional controls. Every movement has a chance to trigger an encounter. Explore searches the current area with a higher encounter chance.\n", "body"),
                ("Resting\n", "heading"),
                ("Rest restores up to 10 HP and 10 MP. It cannot raise either resource beyond its maximum.\n", "body"),
                ("Combat\n", "heading"),
                ("Attack uses your equipped weapon. Defend reduces the next incoming hit. Skills cost 20 MP and deal heavier damage. Items can restore HP during battle.\n", "body"),
                ("Progression\n", "heading"),
                ("Defeating monsters awards EXP and gold. Every 100 EXP increases your level, maximum HP, and fully restores HP. Reach level 10 to unlock the final objective.\n", "body"),
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
                ("The blacksmith upgrades the currently equipped weapon by 20% for 50 gold. Equip a weapon before visiting.\n", "body"),
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
                ("Escape", "key"), ("   Open or close Options\n", "body"),
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

        for name in pages:
            button = tk.Button(tabs, text=name, command=lambda page=name: show_page(page), bg=self.SURFACE_ALT, fg=self.MUTED, activebackground="#30415e", activeforeground="#ffffff", relief=tk.FLAT, bd=0, font=("Arial", 9, "bold"), cursor="hand2", padx=15)
            button.pack(side=tk.LEFT, fill=tk.Y, padx=2)
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
            self.location_name, self.location_description = self.LOCATIONS[direction]
            self.append_text(f"You travel {direction} and arrive at {self.location_name}.", "travel")
            self.update_stats()
            if random.randint(0, 99) < 20:
                self.encounter_monster()
        elif command == "Explore":
            self.append_text(f"You search the surroundings of {self.location_name}.", "travel")
            if random.randint(0, 99) < 50:
                self.encounter_monster()
            else:
                self.append_text("The area is quiet. Nothing answers your search.", "system")
        elif command == "Rest":
            self.rest()
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
        elif command == "Save Game":
            self.player.save_to_file()
            self.save_status_lbl.config(text="SAVED", fg=self.GREEN)
            self.append_text("Journey progress saved.", "success")
            self.show_toast("GAME SAVED")
        elif command == "Challenge Demon King":
            self.challenge_final_boss()
        elif command == "Quit":
            if messagebox.askyesno("Leave Sword Phantasia?", "Quit the game? Unsaved progress will be lost."):
                sys.exit(0)

    def challenge_final_boss(self):
        if self.player.level < 10:
            self.show_toast("REACH LEVEL 10 FIRST", self.RED)
            return
        choice = messagebox.askyesno(
            "The Primordial Throne",
            "Demon King Koji awaits beyond this point.\n\nBegin the final battle?",
            parent=self,
        )
        if choice:
            self.fight_final_boss()

    def fight_final_boss(self):
        self.append_text("The gates of the Primordial Throne open.", "special")
        BattlePanel(self.winfo_toplevel(), self.player, is_boss=True)
        self.append_text("Demon King Koji has fallen. The realm is free.", "reward")
        self.player.save_to_file()
        sys.exit(0)
