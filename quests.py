from dataclasses import dataclass

from item import Item


@dataclass(frozen=True)
class Quest:
    key: str
    title: str
    region: str
    unlock_level: int
    target_family: str
    required: int
    description: str
    reward_exp: int
    reward_gold: int
    reward_item: tuple = None


QUESTS = (
    Quest("slime_tide", "The Slime Tide", "frontier", 1, "slime", 3, "Defeat the slimes gathering around the Frontier Plains.", 35, 25, ("Traveler's Tonic", "Consumable", 0.0, True, 35, False, 0.0)),
    Quest("goblin_warband", "Break the Warband", "mosswood", 3, "goblin", 4, "Thin the goblin ranks threatening travelers in Mosswood.", 55, 45, ("Mossguard Vest", "Light", 0.0, False, 0, True, 7.0)),
    Quest("restless_dead", "Silence the Restless", "crypt", 6, "skeleton", 4, "Return the warriors of the Ashen Crypt to their final rest.", 80, 70, ("Warden Charm", "Ancient", 18.0, False, 0, False, 0.0)),
    Quest("primordial_night", "End the Primordial Night", "throne", 10, "demon", 1, "Defeat Demon King Koji and free the realm.", 150, 200),
)


def available_quests(player):
    return tuple(quest for quest in QUESTS if player.level >= quest.unlock_level)


def quest_progress(player, quest):
    return min(quest.required, int(getattr(player, "quest_progress", {}).get(quest.key, 0)))


def completed_quest_keys(player):
    return set(getattr(player, "completed_quests", []))


def active_quests(player):
    completed = completed_quest_keys(player)
    return tuple(quest for quest in available_quests(player) if quest.key not in completed)


def primary_objective(player):
    active = active_quests(player)
    if not active:
        return "All current quests completed"
    region_key = getattr(player, "current_region", "frontier")
    quest = next((candidate for candidate in active if candidate.region == region_key), active[0])
    progress = quest_progress(player, quest)
    return f"{quest.title}  •  {progress}/{quest.required} {quest.target_family.title()} defeated"


def record_defeat(player, monster_family):
    if not hasattr(player, "quest_progress"):
        player.quest_progress = {}
    if not hasattr(player, "completed_quests"):
        player.completed_quests = []
    completed = set(player.completed_quests)
    updates = []
    completions = []
    for quest in available_quests(player):
        if quest.key in completed or quest.target_family != monster_family:
            continue
        progress = min(quest.required, player.quest_progress.get(quest.key, 0) + 1)
        player.quest_progress[quest.key] = progress
        updates.append((quest, progress))
        if progress >= quest.required:
            player.completed_quests.append(quest.key)
            completed.add(quest.key)
            player.add_experience(quest.reward_exp)
            player.add_coins(quest.reward_gold)
            reward_item = None
            if quest.reward_item:
                reward_item = Item(*quest.reward_item)
                player.inventory.append(reward_item)
            completions.append((quest, reward_item))
    return updates, completions
