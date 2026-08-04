from dataclasses import dataclass


@dataclass(frozen=True)
class Skill:
    name: str
    unlock_level: int
    mp_cost: int
    description: str
    min_damage: int
    max_damage: int
    hits: int = 1
    heal: int = 0
    guard: int = 0
    evade: bool = False
    attack_bonus: int = 0
    weaken: int = 0
    cooldown: int = 1


CLASS_SKILLS = {
    "sword": {
        "name": "Vanguard",
        "identity": "A balanced frontline warrior who mixes precise strikes with defense.",
        "skills": (
            Skill("Cross Slash", 1, 18, "Two disciplined cuts against one target.", 18, 26, hits=2),
            Skill("Aegis Breaker", 4, 24, "A shielded strike that reduces the next incoming hit.", 45, 60, guard=10, cooldown=2),
            Skill("Blade Tempest", 7, 36, "Four rapid sword arcs tear through the enemy.", 18, 25, hits=4, cooldown=2),
            Skill("Radiant Oath", 10, 50, "A legendary finishing cut that also restores 25 HP.", 100, 135, heal=25, cooldown=3),
        ),
    },
    "bow": {
        "name": "Ranger",
        "identity": "A mobile marksman specializing in multi-hit volleys and evasion.",
        "skills": (
            Skill("Piercing Shot", 1, 16, "A focused arrow that punches through defenses.", 36, 50),
            Skill("Arrow Barrage", 4, 28, "Rain five arrows onto the enemy in quick succession.", 12, 18, hits=5, cooldown=2),
            Skill("Windstep Volley", 7, 30, "Fire twice and evade the enemy's next attack.", 22, 30, hits=2, evade=True, cooldown=2),
            Skill("Starfall Rain", 10, 50, "A celestial storm of seven devastating arrows.", 17, 24, hits=7, cooldown=3),
        ),
    },
    "axe": {
        "name": "Berserker",
        "identity": "A relentless heavy hitter built around overwhelming burst damage.",
        "skills": (
            Skill("Cleaving Blow", 1, 20, "A brutal overhead swing with high base damage.", 45, 62),
            Skill("War Cry", 4, 22, "Strike with fury and empower the next normal attack.", 35, 48, attack_bonus=20, cooldown=2),
            Skill("Earthshaker", 7, 36, "Crack the ground and weaken the enemy's next attack.", 78, 105, weaken=12, cooldown=2),
            Skill("Ragnarok Splitter", 10, 55, "Commit everything to one cataclysmic axe strike.", 135, 180, cooldown=3),
        ),
    },
}


def class_key(player):
    weapon_name = getattr(player, "starting_weapon", None)
    if not weapon_name:
        equipped = getattr(player, "equipped_weapon", None)
        weapon_name = getattr(equipped, "item_name", "")
    normalized = str(weapon_name).lower()
    for key in CLASS_SKILLS:
        if key in normalized:
            return key
    return "sword"


def class_data(player):
    return CLASS_SKILLS[class_key(player)]


def class_name(player):
    return class_data(player)["name"]


def all_skills(player):
    return class_data(player)["skills"]


def unlocked_skills(player, level=None):
    current_level = player.level if level is None else level
    return tuple(skill for skill in all_skills(player) if skill.unlock_level <= current_level)


def newly_unlocked_skills(player, previous_level, current_level=None):
    new_level = player.level if current_level is None else current_level
    return tuple(skill for skill in all_skills(player) if previous_level < skill.unlock_level <= new_level)


def mastery_rank(player_or_level):
    """Class skills ascend twice after the original level-10 cap."""
    level = player_or_level if isinstance(player_or_level, int) else player_or_level.level
    if level >= 15:
        return 3
    if level >= 12:
        return 2
    return 1


def mastery_multiplier(player_or_level):
    return 1.0 + (mastery_rank(player_or_level) - 1) * 0.20


def newly_reached_mastery(previous_level, current_level):
    previous_rank = mastery_rank(previous_level)
    current_rank = mastery_rank(current_level)
    return current_rank if current_rank > previous_rank else None
