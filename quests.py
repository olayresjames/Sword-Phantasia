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
    objective_type: str = "defeat"
    objective_label: str = ""


QUESTS = (
    Quest("slime_tide", "The Slime Tide", "frontier", 1, "slime", 3, "Defeat the slimes gathering around the Frontier Plains.", 35, 25, ("Traveler's Tonic", "Consumable", 0.0, True, 35, False, 0.0)),
    Quest("goblin_warband", "Break the Warband", "mosswood", 3, "goblin", 4, "Thin the goblin ranks threatening travelers in Mosswood.", 55, 45, ("Mossguard Vest", "Light", 0.0, False, 0, True, 7.0)),
    Quest("restless_dead", "Silence the Restless", "crypt", 6, "skeleton", 4, "Return the warriors of the Ashen Crypt to their final rest.", 80, 70, ("Warden Charm", "Ancient", 18.0, False, 0, False, 0.0)),
    Quest("primordial_night", "End the Primordial Night", "throne", 10, "demon", 1, "Defeat Demon King Koji and free the realm.", 150, 200),
    Quest("gel_research", "Colors in the Gel", "frontier", 1, "prismatic_gel", 2, "Gather prismatic gel from deposits and carefully disarmed traps.", 30, 30, objective_type="collect", objective_label="Prismatic Gel gathered"),
    Quest("watchtower_echoes", "Echoes of the Watch", "frontier", 1, "old_watchtower", 1, "Find the hidden stair into the Old Watchtower.", 40, 35, objective_type="landmark", objective_label="Old Watchtower discovered"),
    Quest("mooncap_harvest", "A Luminous Harvest", "mosswood", 3, "mooncap_spore", 3, "Collect mooncap spores for the Mosswood herbalists.", 55, 50, objective_type="collect", objective_label="Mooncap Spores gathered"),
    Quest("scouts_choice", "No Scout Left Behind", "mosswood", 3, "guide_scout", 1, "Decide the fate of the scout lost beyond the warband trails.", 65, 60, objective_type="choice", objective_label="Scout's fate decided"),
    Quest("vault_cartography", "Chains and Cartography", "crypt", 6, "warden_vault", 1, "Locate the true Warden's Vault beyond the fallen chains.", 75, 70, objective_type="landmark", objective_label="Warden's Vault discovered"),
    Quest("trial_of_ashes", "The Trial of Ashes", "crypt", 6, "crypt", 3, "Survive three encounters within the Ashen Crypt.", 95, 85, objective_type="survive", objective_label="Crypt encounters survived"),
    Quest("measured_victory", "Measured Victory", "crypt", 6, "skeleton_after_defend", 1, "Defeat a skeleton after using Defend during that battle.", 110, 100, objective_type="special_defeat", objective_label="Guarded victory achieved"),
    Quest("mercy_in_the_void", "Judgment in the Void", "throne", 10, "spare_shade", 1, "Choose how to answer the Penitent Shade's request.", 120, 120, objective_type="choice", objective_label="Shade's fate decided"),
    Quest("embers_of_tomorrow", "Embers of Tomorrow", "throne", 10, "void_ember", 2, "Gather primordial embers from unstable spaces in the throne.", 145, 140, objective_type="collect", objective_label="Void Embers gathered"),
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
    return f"{quest.title}  •  {progress}/{quest.required} {quest_objective_label(quest)}"


def record_defeat(player, monster_family):
    return record_event(player, "defeat", monster_family)


def quest_objective_label(quest):
    if quest.objective_label:
        return quest.objective_label
    return f"{quest.target_family.title()} defeated"


def record_event(player, objective_type, target, amount=1):
    if not hasattr(player, "quest_progress"):
        player.quest_progress = {}
    if not hasattr(player, "completed_quests"):
        player.completed_quests = []
    completed = set(player.completed_quests)
    updates = []
    completions = []
    for quest in available_quests(player):
        if quest.key in completed or quest.objective_type != objective_type or quest.target_family != target:
            continue
        progress = min(quest.required, player.quest_progress.get(quest.key, 0) + amount)
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
                player.add_item(reward_item)
            completions.append((quest, reward_item))
    return updates, completions
