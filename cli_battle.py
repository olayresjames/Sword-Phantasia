import random
import threading
import sys
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
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.stop()
        except (FileNotFoundError, pygame.error):
            pass
except ImportError:
    def play_sound(action):
        pass
    def play_bgm(start=True):
        pass

class Battle:
    def __init__(self, player, is_boss=False):
        self.player = player
        self.is_boss = is_boss

    def start(self):
        if self.is_boss:
            monster_name = "Demon King Koji"
            monster_max_hp = 500
            monster_hp = monster_max_hp
            monster_attack = 45
        else:
            monster_names = ["Slime", "Goblin", "Skeleton"]
            monster_name = random.choice(monster_names)
            
            level_bonus_hp = (self.player.level - 1) * 15
            level_bonus_atk = (self.player.level - 1) * 3
            monster_max_hp = random.randint(30, 79) + level_bonus_hp
            monster_hp = monster_max_hp
            monster_attack = random.randint(5, 14) + level_bonus_atk

        weapon_dmg = self.player.equipped_weapon.additional_damage if getattr(self.player, 'equipped_weapon', None) else 0
        player_attack = 15 + (self.player.level * 5) + int(weapon_dmg)
        print(f"\nA wild {monster_name} appears! (HP: {monster_hp})")
        play_bgm(True)

        while self.player.hp > 0 and monster_hp > 0:
            print(f"\nYour HP: {self.player.hp} | Your Mana: {self.player.mana} | {monster_name} HP: {monster_hp}/{monster_max_hp}")
            print("1. Attack\n2. Defend\n3. Use Skill (Cost: 20 Mana)\n4. Run\n5. Item")
            
            try: choice = int(input("Your choice: "))
            except ValueError:
                print("Invalid choice. Try again.")
                continue

            if choice == 1:
                play_sound("attack")
                dmg = player_attack + random.randint(0, 9)
                monster_hp -= dmg
                print(f"You attacked the {monster_name} for {dmg} damage!")
                if monster_hp <= 0:
                    print(f"You defeated the {monster_name}!")
                    self.reward_player()
                    play_bgm(False)
                    return
            elif choice == 2:
                print("You brace yourself for an attack.")
                play_sound("damage")
                armor_def = self.player.equipped_armor.defense_bonus if getattr(self.player, 'equipped_armor', None) else 0
                reduced = max(0, monster_attack - random.randint(0, 4) - 5 - int(armor_def))
                self.player.hp -= reduced
                print(f"The {monster_name} attacked, but you only took {reduced} damage!")
                continue
            elif choice == 3:
                if self.player.mana >= 20:
                    play_sound("skill")
                    skill_dmg = 40 + random.randint(0, 19)
                    self.player.use_mana(20)
                    monster_hp -= skill_dmg
                    print(f"You used a powerful skill and dealt {skill_dmg} damage!")
                    if monster_hp <= 0:
                        print(f"You defeated the {monster_name}!")
                        self.reward_player()
                        play_bgm(False)
                        return
                else:
                    print("Not enough mana to use skill!")
                    continue
            elif choice == 4:
                if random.randint(0, 99) < 50:
                    print(f"You successfully ran away from the {monster_name}!")
                    play_bgm(False)
                    return
                else:
                    print("You failed to escape!")
            elif choice == 5:
                consumables = [item for item in self.player.inventory if getattr(item, 'is_consumable', False)]
                if not consumables:
                    print("You don't have any usable items!")
                    continue
                    
                print("\n=== Use Item ===")
                for idx, item in enumerate(consumables):
                    print(f"{idx + 1}. {item.item_name} (Heals {item.heal_amount} HP)")
                print("0. Cancel")
                
                try:
                    item_choice = int(input("Select item to use: "))
                    if 1 <= item_choice <= len(consumables):
                        used_item = consumables[item_choice - 1]
                        self.player.inventory.remove(used_item)
                        self.player.hp = min(self.player.hp + used_item.heal_amount, self.player.max_hp)
                        print(f"You used {used_item.item_name} and recovered {used_item.heal_amount} HP!")
                    elif item_choice == 0:
                        continue
                    else:
                        print("Invalid choice.")
                        continue
                except ValueError:
                    print("Invalid choice.")
                    continue
            else:
                print("Invalid choice. Try again.")
                continue

            play_sound("damage")
            armor_def = self.player.equipped_armor.defense_bonus if getattr(self.player, 'equipped_armor', None) else 0
            taken = max(0, monster_attack + random.randint(0, 4) - int(armor_def))
            self.player.hp -= taken
            print(f"The {monster_name} attacked you for {taken} damage!")

            if self.player.hp <= 0:
                print(f"You were defeated by the {monster_name}. Game over!")
                play_bgm(False)
                return

    def reward_player(self):
        exp = random.randint(20, 49)
        coins = random.randint(10, 29)
        self.player.add_experience(exp)
        self.player.add_coins(coins)
        print(f"You gained {exp} EXP and {coins} coins!")
        
        # 30% chance for a weapon drop
        if not self.is_boss and random.randint(0, 99) < 30:
            loot_pool = [
                Item("Rusty Dagger", "Basic", 8.0),
                Item("Bone Club", "Crude", 11.0),
                Item("Slime Sword", "Sticky", 13.0)
            ]
            dropped_item = random.choice(loot_pool)
            self.player.inventory.append(dropped_item)
            print(f"The monster dropped a {dropped_item.item_name}!")