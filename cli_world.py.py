import random
import sys
from item import Item
from cli_battle import Battle

class WorldTraversion:
    def __init__(self, player):
        self.player = player
        if getattr(self.player, 'equipped_weapon', None) is None:
            self.player.equipped_weapon = Item("Sword", "Sharp Blade", 10.0)
            self.player.inventory.append(self.player.equipped_weapon)

    def start_adventure(self):
        while True:
            print("\n===============================")
            print(f" Name: {self.player.name}")
            wep_name = self.player.equipped_weapon.item_name if getattr(self.player, 'equipped_weapon', None) else "None"
            arm_name = getattr(self.player, 'equipped_armor').item_name if getattr(self.player, 'equipped_armor', None) else "None"
            print(f" HP: {self.player.hp}/{self.player.max_hp} | Mana: {self.player.mana} | Lvl: {self.player.level} | Coins: {self.player.coins} | Wep: {wep_name} | Arm: {arm_name}")
            print("===============================\n")

            if self.player.level >= 10:
                print("You have reached level 10!\nA powerful foe awaits you...\nChallenge Demon King Koji?")
                print("1. Yes\n2. No")
                try: choice = int(input("\nEnter choice: "))
                except ValueError: choice = 2

                if choice == 1:
                    print("\nThe Demon King Koji appears!")
                    Battle(self.player, is_boss=True).start()
                    return
                else:
                    print("You chose to continue adventuring.")
                    continue

            print(" 1. Walk Forward\n 2. Walk Back\n 3. Walk Left\n 4. Walk Right")
            print(" 5. Explore (Look for monsters)\n 6. Rest (Restore 10 HP and 10 Mana)")
            print(" 7. Go to Blacksmith\n 8. Shop\n 9. Inventory\n 10. Equip Weapon\n 11. Save Game\n 12. Quit")

            try: choice = int(input("\nEnter choice: "))
            except ValueError:
                print("Invalid choice.")
                continue

            if choice in [1, 2, 3, 4]:
                print("You moved.")
                if random.randint(0, 99) < 20: self.encounter_monster()
            elif choice == 5:
                print("You search the area...")
                if random.randint(0, 99) < 50: self.encounter_monster()
                else: print("No monsters found.")
            elif choice == 6:
                if self.player.hp >= self.player.max_hp and self.player.mana >= 100:
                    print("\nYou are already at full HP and Mana!")
                else:
                    self.player.hp = min(self.player.hp + 10, self.player.max_hp)
                    self.player.mana = min(self.player.mana + 10, 100)
                    print(f"\nYou rested. Current HP: {self.player.hp}, Current Mana: {self.player.mana}")
            elif choice == 7:
                self.visit_blacksmith()
            elif choice == 8:
                self.visit_shop()
            elif choice == 9:
                print("\n=== Inventory ===")
                if getattr(self.player, 'equipped_weapon', None):
                    w = self.player.equipped_weapon
                    print(f"Equipped Weapon: {w.item_name} (+{w.additional_damage:.1f} DMG)")
                if getattr(self.player, 'equipped_armor', None):
                    a = getattr(self.player, 'equipped_armor')
                    print(f"Equipped Armor: {a.item_name} (+{a.defense_bonus:.1f} DEF)")
                for idx, item in enumerate(getattr(self.player, 'inventory', [])):
                    if getattr(item, 'is_consumable', False):
                        print(f"{idx + 1}. {item.item_name} (Heals {item.heal_amount} HP)")
                    elif getattr(item, 'is_armor', False):
                        print(f"{idx + 1}. {item.item_name} (+{item.defense_bonus:.1f} DEF)")
                    else:
                        print(f"{idx + 1}. {item.item_name} (+{item.additional_damage:.1f} DMG)")
                if not getattr(self.player, 'inventory', []):
                    print("Your inventory is empty.")
            elif choice == 10:
                equippables = [item for item in getattr(self.player, 'inventory', []) if not getattr(item, 'is_consumable', False)]
                if not equippables:
                    print("You don't have any items in your inventory to equip.")
                    continue
                print("\n=== Equip Item ===")
                for idx, item in enumerate(equippables):
                    if getattr(item, 'is_armor', False):
                        print(f"{idx + 1}. {item.item_name} (+{item.defense_bonus:.1f} DEF)")
                    else:
                        print(f"{idx + 1}. {item.item_name} (+{item.additional_damage:.1f} DMG)")
                try:
                    eq_choice = int(input("Select item number to equip (0 to cancel): "))
                    if 1 <= eq_choice <= len(equippables):
                        selected = equippables[eq_choice - 1]
                        if getattr(selected, 'is_armor', False):
                            self.player.equipped_armor = selected
                            print(f"Equipped {self.player.equipped_armor.item_name}!")
                        else:
                            self.player.equipped_weapon = selected
                            print(f"Equipped {self.player.equipped_weapon.item_name}!")
                except ValueError:
                    print("Invalid choice.")
            elif choice == 11:
                self.player.save_to_file()
                print("\nGame saved successfully!")
            elif choice == 12:
                print("Exiting the world. Thank you for playing!")
                return
            else:
                print("Invalid choice.")

    def encounter_monster(self):
        print("A wild encounter!")
        Battle(self.player).start()
        if self.player.hp <= 0:
            print("\nYou have been defeated! Game over!")
            sys.exit(0)
        self.player.save_to_file()
        print("Game auto-saved.")

    def visit_blacksmith(self):
        weapon = getattr(self.player, 'equipped_weapon', None)
        if not weapon:
            print("\nYou don't have an equipped weapon to upgrade!")
            return
        print(f"\nWelcome to the Blacksmith!\nWeapon: {weapon.item_name} | Damage bonus: {weapon.additional_damage}")
        print(f"Coins: {self.player.coins} | Upgrade cost: 50 coins\nUpgrade? (1: Yes, 2: No)")
        
        try: choice = int(input("\nEnter choice: "))
        except ValueError: choice = 2
        
        if choice == 1:
            if self.player.coins >= 50:
                print("Applying a 20% upgrade...")
                weapon.apply_upgrades(20)
                self.player.spend_coins(50)
                print(f"Upgrade complete! New bonus: {weapon.additional_damage}")
            else:
                print("\nYou don't have enough coins.")
        else:
            print("\nCome back anytime!")

    def visit_shop(self):
        print(f"\nWelcome to the Shop! You have {self.player.coins} coins.")
        shop_items = [
            {"item": Item("Iron Sword", "Sturdy", 15.0), "cost": 30},
            {"item": Item("Steel Axe", "Heavy", 20.0), "cost": 50},
            {"item": Item("Excalibur", "Legendary", 50.0), "cost": 200},
            {"item": Item("Healing Potion", "Consumable", 0.0, is_consumable=True, heal_amount=50), "cost": 15},
            {"item": Item("Leather Armor", "Light", 0.0, is_armor=True, defense_bonus=5.0), "cost": 40},
            {"item": Item("Iron Armor", "Sturdy", 0.0, is_armor=True, defense_bonus=12.0), "cost": 100}
        ]
        
        for idx, entry in enumerate(shop_items):
            i = entry["item"]
            if getattr(i, 'is_consumable', False):
                print(f"{idx + 1}. {i.item_name} (Heals {i.heal_amount} HP) - {entry['cost']} Coins")
            elif getattr(i, 'is_armor', False):
                print(f"{idx + 1}. {i.item_name} (+{i.defense_bonus} DEF) - {entry['cost']} Coins")
            else:
                print(f"{idx + 1}. {i.item_name} (+{i.additional_damage} DMG) - {entry['cost']} Coins")
        print("0. Leave Shop")
        
        try:
            choice = int(input("Enter choice: "))
            if 1 <= choice <= len(shop_items):
                entry = shop_items[choice - 1]
                if self.player.coins >= entry['cost']:
                    self.player.spend_coins(entry['cost'])
                    new_item = Item(entry['item'].item_name, entry['item'].attributes, entry['item'].additional_damage, getattr(entry['item'], 'is_consumable', False), getattr(entry['item'], 'heal_amount', 0), getattr(entry['item'], 'is_armor', False), getattr(entry['item'], 'defense_bonus', 0.0))
                    self.player.inventory.append(new_item)
                    print(f"You bought {new_item.item_name} for {entry['cost']} coins!")
                else:
                    print("Not enough coins!")
            elif choice == 0:
                print("You left the shop.")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")