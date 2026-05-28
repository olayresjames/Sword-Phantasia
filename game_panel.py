import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import random
import sys
from battle_panel import BattlePanel
from item import Item

class GamePanel(tk.Frame):
    def __init__(self, parent, player):
        super().__init__(parent)
        self.player = player
        self.configure(bg="#0a0a0a")
        
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        style.configure("Red.Horizontal.TProgressbar", troughcolor='#2a0000', background='#cc0000', bordercolor='#000000', lightcolor='#ff3333', darkcolor='#990000')
        style.configure("Blue.Horizontal.TProgressbar", troughcolor='#001133', background='#0055cc', bordercolor='#000000', lightcolor='#3388ff', darkcolor='#003399')
        
        stats_frame = tk.Frame(self, bg="#0a0a0a")
        stats_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=15)
        
        # Left stats: Name, Level, Coins, Weapons
        self.info_label = tk.Label(stats_frame, font=("Arial", 13, "bold"), fg="#ffffff", bg="#0a0a0a", justify=tk.LEFT)
        self.info_label.pack(side=tk.LEFT)
        
        # Right stats: HP and Mana bars
        bars_frame = tk.Frame(stats_frame, bg="#0a0a0a")
        bars_frame.pack(side=tk.RIGHT)
        
        self.hp_lbl = tk.Label(bars_frame, font=("Arial", 11, "bold"), fg="#ff3333", bg="#0a0a0a")
        self.hp_lbl.grid(row=0, column=0, sticky="e", padx=5)
        self.hp_bar = ttk.Progressbar(bars_frame, style="Red.Horizontal.TProgressbar", orient="horizontal", length=200, mode="determinate")
        self.hp_bar.grid(row=0, column=1, pady=2)
        
        self.mana_lbl = tk.Label(bars_frame, font=("Arial", 11, "bold"), fg="#3388ff", bg="#0a0a0a")
        self.mana_lbl.grid(row=1, column=0, sticky="e", padx=5)
        self.mana_bar = ttk.Progressbar(bars_frame, style="Blue.Horizontal.TProgressbar", orient="horizontal", length=200, mode="determinate")
        self.mana_bar.grid(row=1, column=1, pady=2)
        
        self.text_area = tk.Text(self, state=tk.DISABLED, wrap=tk.WORD, bg="#141414", fg="#e0e0e0", font=("Consolas", 12), relief=tk.FLAT, insertbackground="white")
        self.text_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        btn_frame = tk.Frame(self, bg="#0a0a0a")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=15)
        
        buttons = [
            "Walk Forward", "Walk Back", "Walk Left", "Walk Right",
            "Explore", "Rest", "Blacksmith", "Shop", "Inventory", "Equip", "Save Game", "Quit"
        ]
        
        self.btn_dict = {}
        for i, text in enumerate(buttons):
            r, c = divmod(i, 6)
            btn = tk.Button(btn_frame, text=text, command=lambda cmd=text: self.action_performed(cmd),
                            bg="#7a0000", fg="#ffffff", activebackground="#b30000", activeforeground="#ffffff", 
                            disabledforeground="#888888", relief=tk.FLAT, font=("Arial", 14, "bold"), pady=15)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#b30000") if b['state'] != tk.DISABLED else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#7a0000") if b['state'] != tk.DISABLED else None)
            btn.grid(row=r, column=c, sticky="ew", padx=10, pady=10)
            btn_frame.grid_columnconfigure(c, weight=1)
            self.btn_dict[text] = btn
            
        self.update_stats()

    def update_stats(self):
        wep_name = self.player.equipped_weapon.item_name if getattr(self.player, 'equipped_weapon', None) else "None"
        arm_name = getattr(self.player, 'equipped_armor').item_name if getattr(self.player, 'equipped_armor', None) else "None"
        
        self.info_label.config(
            text=f"Hero: {self.player.name}   |   Level: {self.player.level}   |   Coins: {self.player.coins}\n"
                 f"Weapon: {wep_name}   |   Armor: {arm_name}"
        )
        self.hp_bar['maximum'] = self.player.max_hp
        self.hp_bar['value'] = self.player.hp
        self.hp_lbl.config(text=f"HP: {self.player.hp}/{self.player.max_hp}")
        
        self.mana_bar['maximum'] = 100
        self.mana_bar['value'] = self.player.mana
        self.mana_lbl.config(text=f"MP: {self.player.mana}/100")
        
        # Dynamic Button Updating
        equippables = [item for item in self.player.inventory if not getattr(item, 'is_consumable', False)]
        can_equip = len(equippables) > 0
        if "Equip" in self.btn_dict:
            self.btn_dict["Equip"].config(state=tk.NORMAL if can_equip else tk.DISABLED, bg="#7a0000" if can_equip else "#333333")
            
        can_smith = getattr(self.player, 'equipped_weapon', None) is not None
        if "Blacksmith" in self.btn_dict:
            self.btn_dict["Blacksmith"].config(state=tk.NORMAL if can_smith else tk.DISABLED, bg="#7a0000" if can_smith else "#333333")

    def append_text(self, text):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def encounter_monster(self):
        self.append_text("A wild encounter!")
        BattlePanel(self.winfo_toplevel(), self.player)
        self.append_text("You survived the battle!")
        self.player.save_to_file()
        self.append_text("Game auto-saved.")
        self.update_stats()

    def rest(self):
        self.player.hp = min(self.player.hp + 10, self.player.max_hp)
        self.player.mana = min(self.player.mana + 10, 100)
        self.append_text("You rested and regained 10 HP and 10 Mana.")
        self.update_stats()

    def visit_blacksmith(self):
        if not self.player.equipped_weapon:
            self.append_text("You don't have a weapon equipped to upgrade!")
            return
            
        msg = f"Welcome to the Blacksmith!\nYour coins: {self.player.coins}\nUpgrade {self.player.equipped_weapon.item_name} cost: 50 coins"
        choice = messagebox.askyesno("Blacksmith", msg + "\n\nUpgrade Weapon?")
        
        if choice:
            if self.player.coins >= 50:
                self.player.spend_coins(50)
                self.player.equipped_weapon.apply_upgrades(20)
                self.append_text(f"Your {self.player.equipped_weapon.item_name} has been upgraded!")
                self.update_stats()
            else:
                self.append_text("You don't have enough coins!")
        else:
            self.append_text("You left the blacksmith.")

    def visit_shop(self):
        shop_win = tk.Toplevel(self)
        shop_win.title("Shop")
        shop_win.geometry("450x350")
        shop_win.configure(bg="#0a0a0a")
        shop_win.grab_set()
        
        tk.Label(shop_win, text="=== THE MERCHANT ===", font=("Arial", 14, "bold"), fg="#ff3333", bg="#0a0a0a", pady=10).pack()
        tk.Label(shop_win, text=f"Your coins: {self.player.coins}", font=("Arial", 11), fg="#ffffff", bg="#0a0a0a", pady=5).pack()
        
        shop_items = [
            {"item": Item("Iron Sword", "Sturdy", 15.0), "cost": 30},
            {"item": Item("Steel Axe", "Heavy", 20.0), "cost": 50},
            {"item": Item("Excalibur", "Legendary", 50.0), "cost": 200},
            {"item": Item("Healing Potion", "Consumable", 0.0, is_consumable=True, heal_amount=50), "cost": 15},
            {"item": Item("Leather Armor", "Light", 0.0, is_armor=True, defense_bonus=5.0), "cost": 40},
            {"item": Item("Iron Armor", "Sturdy", 0.0, is_armor=True, defense_bonus=12.0), "cost": 100}
        ]
        
        listbox = tk.Listbox(shop_win, bg="#141414", fg="#ffffff", font=("Consolas", 11), selectbackground="#7a0000")
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for idx, entry in enumerate(shop_items):
            i = entry["item"]
            if getattr(i, 'is_consumable', False):
                listbox.insert(tk.END, f"{i.item_name} (Heals {i.heal_amount} HP) - {entry['cost']} Coins")
            elif getattr(i, 'is_armor', False):
                listbox.insert(tk.END, f"{i.item_name} (+{i.defense_bonus} DEF) - {entry['cost']} Coins")
            else:
                listbox.insert(tk.END, f"{i.item_name} (+{i.additional_damage} DMG) - {entry['cost']} Coins")
            
        def on_buy():
            selection = listbox.curselection()
            if selection:
                entry = shop_items[selection[0]]
                if self.player.coins >= entry['cost']:
                    self.player.spend_coins(entry['cost'])
                    new_item = Item(entry['item'].item_name, entry['item'].attributes, entry['item'].additional_damage, getattr(entry['item'], 'is_consumable', False), getattr(entry['item'], 'heal_amount', 0), getattr(entry['item'], 'is_armor', False), getattr(entry['item'], 'defense_bonus', 0.0))
                    self.player.inventory.append(new_item)
                    self.append_text(f"You bought {new_item.item_name} for {entry['cost']} coins!")
                    shop_win.destroy()
                    self.update_stats()
                else:
                    messagebox.showwarning("Shop", "Not enough coins!", parent=shop_win)
                    
        buy_btn = tk.Button(shop_win, text="Buy Selected Item", command=on_buy, bg="#7a0000", fg="white", activebackground="#b30000", activeforeground="white", relief=tk.FLAT, font=("Arial", 11, "bold"))
        buy_btn.bind("<Enter>", lambda e: e.widget.config(bg="#b30000"))
        buy_btn.bind("<Leave>", lambda e: e.widget.config(bg="#7a0000"))
        buy_btn.pack(pady=10, padx=20, fill=tk.X)

    def show_inventory(self):
        inv_text = "=== Inventory ===\n"
        if self.player.equipped_weapon:
            w = self.player.equipped_weapon
            inv_text += f"Equipped Weapon: {w.item_name} (+{w.additional_damage:.1f} DMG)\n"
        if getattr(self.player, 'equipped_armor', None):
            a = getattr(self.player, 'equipped_armor')
            inv_text += f"Equipped Armor: {a.item_name} (+{a.defense_bonus:.1f} DEF)\n"
        if not self.player.inventory:
            inv_text += "Your inventory is empty.\n"
        else:
            for idx, item in enumerate(self.player.inventory):
                if getattr(item, 'is_consumable', False):
                    inv_text += f"{idx + 1}. {item.item_name} (Heals {item.heal_amount} HP)\n"
                elif getattr(item, 'is_armor', False):
                    inv_text += f"{idx + 1}. {item.item_name} (+{item.defense_bonus:.1f} DEF)\n"
                else:
                    inv_text += f"{idx + 1}. {item.item_name} (+{item.additional_damage:.1f} DMG)\n"
        self.append_text(inv_text)

    def equip_weapon(self):
        equippables = [item for item in self.player.inventory if not getattr(item, 'is_consumable', False)]
        if not equippables:
            self.append_text("You don't have any items to equip!")
            return
            
        equip_win = tk.Toplevel(self)
        equip_win.title("Equip Item")
        equip_win.geometry("400x300")
        equip_win.configure(bg="#0a0a0a")
        equip_win.grab_set()
        
        tk.Label(equip_win, text="Select an item to equip:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#0a0a0a").pack(pady=10)
        
        listbox = tk.Listbox(equip_win, bg="#141414", fg="#ffffff", font=("Consolas", 11), selectbackground="#7a0000")
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for item in equippables:
            if getattr(item, 'is_armor', False):
                listbox.insert(tk.END, f"{item.item_name} (+{item.defense_bonus:.1f} DEF)")
            else:
                listbox.insert(tk.END, f"{item.item_name} (+{item.additional_damage:.1f} DMG)")
            
        def on_equip():
            selection = listbox.curselection()
            if selection:
                selected = equippables[selection[0]]
                if getattr(selected, 'is_armor', False):
                    self.player.equipped_armor = selected
                    self.append_text(f"Equipped {self.player.equipped_armor.item_name}!")
                else:
                    self.player.equipped_weapon = selected
                    self.append_text(f"Equipped {self.player.equipped_weapon.item_name}!")
                equip_win.destroy()
                self.update_stats()
                
        eq_btn = tk.Button(equip_win, text="Equip", command=on_equip, bg="#7a0000", fg="white", activebackground="#b30000", activeforeground="white", relief=tk.FLAT, font=("Arial", 11, "bold"))
        eq_btn.bind("<Enter>", lambda e: e.widget.config(bg="#b30000"))
        eq_btn.bind("<Leave>", lambda e: e.widget.config(bg="#7a0000"))
        eq_btn.pack(pady=10, padx=20, fill=tk.X)

    def action_performed(self, command):
        if command.startswith("Walk"):
            direction = command.replace("Walk ", "").lower()
            self.append_text(f"You moved {direction}")
            if random.randint(0, 99) < 20:
                self.encounter_monster()
        elif command == "Explore":
            self.append_text("You search the area...")
            if random.randint(0, 99) < 50:
                self.encounter_monster()
            else:
                self.append_text("No monsters found.")
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
        elif command == "Save Game":
            self.player.save_to_file()
            self.append_text("Game saved successfully!")
        elif command == "Quit":
            sys.exit(0)
            
        if self.player.level >= 10:
            choice = messagebox.askyesno(
                "Final Boss", 
                "You have reached level 10!\nA powerful foe awaits you...\nWould you like to challenge the Demon King Koji?"
            )
            if choice:
                self.fight_final_boss()

    def fight_final_boss(self):
        self.append_text("\nThe Demon King Koji appears!")
        BattlePanel(self.winfo_toplevel(), self.player, is_boss=True)
        self.append_text("Congratulations! You defeated the Demon King Koji!")
        self.append_text("Thank you for playing Sword Phantasia!")
        messagebox.showinfo("Victory!", "Congratulations! You defeated the Demon King Koji!\nThank you for playing!")
        sys.exit(0)