# Sword Phantasia

A Python-based Role-Playing Game (RPG) featuring a graphical user interface built with Tkinter and audio powered by Pygame.

## Features
* **Graphical Interface:** Engaging Tkinter-based UI for battles, main menus, shopping, and inventory management.
* **Character Progression:** Gain experience points from defeating monsters to level up your hero and increase max HP.
* **Class Skill Trees:** Play as a Vanguard, Ranger, or Berserker and unlock class abilities at levels 1, 4, 7, and 10.
* **Turn-Based Combat:** Read telegraphed enemy intents, defend strategically, and battle enemies with family-specific abilities.
* **Regions & Quests:** Progress through the Frontier Plains, Mosswood Wilds, Ashen Crypt, and Primordial Throne while completing persistent story quests.
* **Inventory System:** Manage consumables, equip powerful weapons, and don armor to boost your stats.
* **Town Facilities:** Visit the Blacksmith to upgrade your equipped gear or the Shop to purchase potions and stronger equipment.
* **Save/Load System:** Seamlessly save your progress and load it later so you never lose your adventure.
* **Audio & Music:** Immersive sound effects and background music during battles (handled by Pygame).

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
5. Complete regional quests, reach Level 10, and travel to the Primordial Throne for the final challenge.

## Building as an Executable (.exe)
To bundle the game into a standalone Windows executable using PyInstaller, run the following command in the project root:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --add-data "assets;assets" main.py
```
Your generated standalone game will be located in the newly created `dist/` folder.
