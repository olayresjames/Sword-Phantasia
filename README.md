# Sword Phantasia

A Python-based Role-Playing Game (RPG) featuring a graphical user interface built with Tkinter and audio powered by Pygame.

## Features
* **Graphical Interface:** Engaging Tkinter-based UI for battles, main menus, shopping, and inventory management.
* **Character Progression:** Gain experience points from defeating monsters to level up your hero and increase max HP.
* **Class Skill Trees:** Play as a Vanguard, Ranger, or Berserker and unlock class abilities at levels 1, 4, 7, and 10.
* **Tactical Turn-Based Combat:** Read telegraphed enemy intents, exploit heavy attacks with skills, defend to recover MP, manage skill cooldowns, and adapt to escalating boss phases.
* **Regions & Quests:** Progress through the Frontier Plains, Mosswood Wilds, Ashen Crypt, and Primordial Throne while completing persistent story quests.
* **Dynamic Exploration:** Discover treasures, materials, landmarks, NPC choices, shrines, traps, and wandering regional merchants while traveling.
* **Varied Objectives:** Complete gathering, discovery, survival, special-combat, choice-driven, and monster-hunting quests.
* **Regional Loot:** Discover distinct weapons, armor, consumables, and rare treasures in every region, with improved drop rates from ascended enemies.
* **Region Champions:** Complete each regional quest to challenge Tideheart Behemoth, Thornlord Grak, and the Ashen Bonewyrm before confronting Demon King Koji.
* **Postgame Mastery:** Continue beyond level 10 with rising EXP requirements, stronger enemy variants, and class-skill mastery upgrades at levels 12 and 15.
* **Clean Inventory System:** Stack consumables, compare gear against equipped stats, sort by type and rarity, and automatically recycle weak duplicate equipment into Metal Scrap within a 30-slot pack.
* **Tiered Forging:** Improve weapons through five linear forge tiers with escalating prices based on tier, weapon strength, and rarity.
* **Recoverable Defeat:** Retry, return to camp with a gold penalty, load your last save, or return to title instead of losing the entire session.
* **Difficulty & Accessibility:** Choose Easy, Normal, or Hard; control text speed, audio levels, display mode, reduced animations, and remappable adventure/battle controls.
* **Resilient Saves:** Validate save data, write atomically, retain two backups, and recover automatically if the primary save is damaged.
* **Audio & Music:** Shared, cached, volume-aware sound effects and battle music with graceful silent fallback.

## Prerequisites
* Python 3.x
* [Pygame](https://www.pygame.org/) (Required for sound effects and music to play)

## Installation & Setup
1. Ensure you have Python installed on your system.
2. Open your terminal or command prompt and install the required dependencies:
   ```bash
   pip install pygame
   ```
3. Run the game:
   ```bash
   python main.py
   ```
    
## How to Play
1. Start the game and click "Play Game" from the main menu.
2. Enter your character's name and select a starting weapon (Sword, Bow, or Axe).
3. Use the on-screen controls or WASD/arrow keys to explore. Press `M` for the Region Map and `Q` for the Quest Log.
4. Watch enemy intents during combat and press `S` to open your class skill deck.
   Skills deal 25% bonus damage against telegraphed heavy attacks. Defending restores MP, with extra recovery against heavy attacks.
5. Complete each regional quest and defeat its champion to break the three seals on the Primordial Throne.
6. Reach Level 10 and travel to the Primordial Throne for the final challenge. Continue leveling afterward to hunt ascended enemies and reach Mastery III.

## Regenerating Pixel-Art Sprites

The monster and miniboss sprites are generated locally with Pillow and do not require an API key:
```bash
pip install pillow
python tools/generate_monster_sprites.py
```

## Automated Tests

Run the leveling, quests, equipment/inventory, save recovery, and combat calculation tests with:

```bash
python -m unittest discover -s tests -v
```

## Building as an Executable (.exe)
To bundle the game into a standalone Windows executable using PyInstaller, run the following command in the project root:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --add-data "assets;assets" main.py
```
Your generated standalone game will be located in the newly created `dist/` folder.
