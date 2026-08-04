from dataclasses import dataclass
import random


@dataclass(frozen=True)
class EnemyIntent:
    label: str
    kind: str
    weight: int
    multiplier: float = 1.0
    heal_fraction: float = 0.0
    guard_fraction: float = 0.0


@dataclass(frozen=True)
class MonsterSpec:
    name: str
    family: str
    sprite_key: str
    hp_range: tuple
    attack_range: tuple
    weight: int = 1
    elite: bool = False
    boss_key: str = None
    reward_exp: int = 0
    reward_gold: int = 0


@dataclass(frozen=True)
class Region:
    key: str
    name: str
    unlock_level: int
    description: str
    locations: dict
    monsters: tuple


ENEMY_INTENTS = {
    "slime": (
        EnemyIntent("Wobbly Tackle", "attack", 6, multiplier=1.0),
        EnemyIntent("Corrosive Splash", "attack", 3, multiplier=1.35),
        EnemyIntent("Gel Regeneration", "heal", 2, heal_fraction=0.14),
    ),
    "goblin": (
        EnemyIntent("Jagged Slash", "attack", 6, multiplier=1.0),
        EnemyIntent("Dirty Ambush", "attack", 3, multiplier=1.5),
        EnemyIntent("Pilfering Strike", "steal", 2, multiplier=0.75),
    ),
    "skeleton": (
        EnemyIntent("Boneblade Strike", "attack", 6, multiplier=1.0),
        EnemyIntent("Grave Counter", "attack", 3, multiplier=1.4),
        EnemyIntent("Bone Guard", "guard", 2, guard_fraction=0.40),
    ),
    "demon": (
        EnemyIntent("Abyssal Claw", "attack", 5, multiplier=1.0),
        EnemyIntent("Primordial Hellfire", "attack", 4, multiplier=1.55),
        EnemyIntent("World-Ender", "attack", 1, multiplier=1.95),
    ),
    "void": (
        EnemyIntent("Void Rend", "attack", 5, multiplier=1.0),
        EnemyIntent("Eclipse Flare", "attack", 3, multiplier=1.45),
        EnemyIntent("Abyssal Ward", "guard", 2, guard_fraction=0.35),
    ),
}


REGIONS = {
    "frontier": Region(
        "frontier",
        "Frontier Plains",
        1,
        "Wind-beaten grasslands where strange slimes gather near the old roads.",
        {
            "forward": ("Whispering Road", "A weathered road winds toward distant ruins."),
            "back": ("Frontier Camp", "A quiet campfire marks the edge of the known realm."),
            "left": ("Silvergrass Field", "Pale grass bends around pools of living gel."),
            "right": ("Old Watch Hill", "A ruined watchtower overlooks the plains."),
        },
        (
            MonsterSpec("Slime", "slime", "Slime", (30, 52), (5, 10), 5),
            MonsterSpec("Verdant Slime", "slime", "Slime", (42, 65), (7, 12), 3),
            MonsterSpec("King Slime", "slime", "Slime", (70, 95), (10, 15), 1),
        ),
    ),
    "mosswood": Region(
        "mosswood",
        "Mosswood Wilds",
        3,
        "An ancient forest occupied by cunning goblin warbands.",
        {
            "forward": ("Warchief's Path", "Totems and bootprints mark a guarded trail."),
            "back": ("Mosswood Gate", "Stone lanterns stand beneath the tangled canopy."),
            "left": ("Mooncap Hollow", "Blue mushrooms illuminate abandoned camps."),
            "right": ("Thornwatch Ridge", "Goblin scouts watch from thorn-covered ledges."),
        },
        (
            MonsterSpec("Goblin", "goblin", "Goblin", (65, 88), (11, 17), 5),
            MonsterSpec("Goblin Scout", "goblin", "Goblin", (72, 98), (13, 19), 3),
            MonsterSpec("Goblin Warchief", "goblin", "Goblin", (105, 135), (17, 23), 1),
        ),
    ),
    "crypt": Region(
        "crypt",
        "Ashen Crypt",
        6,
        "A buried necropolis where the honored dead no longer sleep.",
        {
            "forward": ("Hall of Ash", "Dust falls from statues of forgotten monarchs."),
            "back": ("Crypt Entrance", "Cold daylight fades behind the burial doors."),
            "left": ("Ossuary Walk", "Thousands of bones line the narrow passage."),
            "right": ("Warden's Vault", "Ancient chains rattle behind a sealed arch."),
        },
        (
            MonsterSpec("Skeleton", "skeleton", "Skeleton", (105, 140), (18, 25), 5),
            MonsterSpec("Crypt Archer", "skeleton", "Skeleton", (115, 150), (20, 27), 3),
            MonsterSpec("Bone Warden", "skeleton", "Skeleton", (155, 195), (24, 32), 1),
        ),
    ),
    "throne": Region(
        "throne",
        "Primordial Throne",
        10,
        "The final stronghold of Demon King Koji.",
        {
            "forward": ("Throne Approach", "Black fire burns along the final path."),
            "back": ("Obsidian Gate", "The sealed gate separates the realm from oblivion."),
            "left": ("Void Gallery", "Ancient murals depict the birth of primordial demons."),
            "right": ("Crown of Ash", "A shattered balcony hangs above an endless abyss."),
        },
        (
            MonsterSpec("Abyss Stalker", "void", "Demon King Koji", (230, 300), (30, 39), 5),
            MonsterSpec("Hellfire Knight", "void", "Demon King Koji", (285, 355), (35, 44), 3, elite=True),
            MonsterSpec("Void Herald", "void", "Demon King Koji", (350, 430), (40, 50), 1, elite=True),
        ),
    ),
}


DEMON_KING = MonsterSpec("Demon King Koji", "demon", "Demon King Koji", (500, 500), (45, 45), 1)


MINIBOSSES = {
    "frontier": MonsterSpec(
        "Tideheart Behemoth", "slime", "Tideheart Behemoth", (145, 165), (15, 19),
        boss_key="tideheart", reward_exp=90, reward_gold=70,
    ),
    "mosswood": MonsterSpec(
        "Thornlord Grak", "goblin", "Thornlord Grak", (245, 275), (25, 31),
        boss_key="thornlord", reward_exp=130, reward_gold=105,
    ),
    "crypt": MonsterSpec(
        "Ashen Bonewyrm", "skeleton", "Ashen Bonewyrm", (365, 405), (35, 43),
        boss_key="bonewyrm", reward_exp=180, reward_gold=150,
    ),
}


MINIBOSS_QUESTS = {
    "frontier": "slime_tide",
    "mosswood": "goblin_warband",
    "crypt": "restless_dead",
}


ASCENDED_MONSTERS = {
    "frontier": (
        MonsterSpec("Prismatic Slime", "slime", "Slime", (175, 225), (24, 31), 2, elite=True),
        MonsterSpec("Tideborn Slime", "slime", "Slime", (220, 275), (27, 35), 1, elite=True),
    ),
    "mosswood": (
        MonsterSpec("Bloodmoon Raider", "goblin", "Goblin", (235, 295), (31, 39), 2, elite=True),
        MonsterSpec("Elder Warchief", "goblin", "Goblin", (290, 350), (35, 44), 1, elite=True),
    ),
    "crypt": (
        MonsterSpec("Gravebound Champion", "skeleton", "Skeleton", (300, 370), (39, 48), 2, elite=True),
        MonsterSpec("Deathless Warden", "skeleton", "Skeleton", (365, 445), (43, 53), 1, elite=True),
    ),
}


def defeated_miniboss_keys(player):
    return set(getattr(player, "defeated_minibosses", []))


def miniboss_for_region(player, region_key=None):
    key = region_key or current_region(player).key
    boss = MINIBOSSES.get(key)
    if not boss or boss.boss_key in defeated_miniboss_keys(player):
        return None
    required_quest = MINIBOSS_QUESTS[key]
    if required_quest not in set(getattr(player, "completed_quests", [])):
        return None
    return boss


def all_minibosses_defeated(player):
    defeated = defeated_miniboss_keys(player)
    return all(boss.boss_key in defeated for boss in MINIBOSSES.values())


def unlocked_regions(player):
    return tuple(region for region in REGIONS.values() if player.level >= region.unlock_level)


def current_region(player):
    key = getattr(player, "current_region", "frontier")
    region = REGIONS.get(key, REGIONS["frontier"])
    if player.level < region.unlock_level:
        return REGIONS["frontier"]
    return region


def choose_monster(player):
    region = current_region(player)
    monsters = list(region.monsters)
    if player.level >= 11:
        monsters.extend(ASCENDED_MONSTERS.get(region.key, ()))
    if not monsters:
        return REGIONS["crypt"].monsters[0]
    return random.choices(monsters, weights=[monster.weight for monster in monsters], k=1)[0]


def choose_enemy_intent(family, hp_ratio=1.0):
    intents = list(ENEMY_INTENTS.get(family, ENEMY_INTENTS["slime"]))
    weights = [intent.weight for intent in intents]
    if family == "demon" and hp_ratio <= 0.35:
        weights = [2, 5, 4]
    return random.choices(intents, weights=weights, k=1)[0]
