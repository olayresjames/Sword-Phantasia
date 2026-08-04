from dataclasses import dataclass
import random


@dataclass(frozen=True)
class ExplorationEvent:
    key: str
    title: str
    region: str
    kind: str
    description: str
    target: str = ""
    weight: int = 1


MATERIAL_LABELS = {
    "prismatic_gel": "Prismatic Gel",
    "mooncap_spore": "Mooncap Spore",
    "warden_ash": "Warden Ash",
    "void_ember": "Void Ember",
}

LANDMARK_LABELS = {
    "old_watchtower": "Old Watchtower",
    "mooncap_sanctum": "Mooncap Sanctum",
    "warden_vault": "Warden's Vault",
    "void_gallery": "Void Gallery",
}


EVENTS = (
    ExplorationEvent("frontier_cache", "A Weathered Lockbox", "frontier", "treasure", "A half-buried lockbox glints beneath the silvergrass.", weight=3),
    ExplorationEvent("gel_deposit", "Prismatic Gel Deposit", "frontier", "material", "A rainbow sheen ripples across an abandoned slime trail.", "prismatic_gel", 3),
    ExplorationEvent("old_watchtower", "The Old Watchtower", "frontier", "landmark", "You find the forgotten stair into the ruined watchtower.", "old_watchtower", 2),
    ExplorationEvent("road_pilgrim", "A Roadside Pilgrim", "frontier", "choice", "A wounded pilgrim asks for gold to reach Frontier Camp.", "aid_pilgrim", 2),
    ExplorationEvent("wind_shrine", "Shrine of Open Skies", "frontier", "shrine", "Blue ribbons dance around a quiet roadside shrine.", weight=2),
    ExplorationEvent("hunter_snare", "Hidden Hunter's Snare", "frontier", "trap", "A taut wire cuts across the grass ahead.", "prismatic_gel", 2),
    ExplorationEvent("frontier_trader", "Traveling Peddler", "frontier", "merchant", "A peddler offers one regional find at a reduced price.", weight=2),

    ExplorationEvent("mosswood_cache", "Warband Stash", "mosswood", "treasure", "A goblin supply bundle hangs beneath a marked oak.", weight=3),
    ExplorationEvent("mooncap_patch", "Mooncap Grove", "mosswood", "material", "Luminous mooncaps release silver spores into the air.", "mooncap_spore", 3),
    ExplorationEvent("mooncap_sanctum", "Mooncap Sanctum", "mosswood", "landmark", "A living arch opens onto an ancient druid sanctuary.", "mooncap_sanctum", 2),
    ExplorationEvent("lost_scout", "The Lost Scout", "mosswood", "choice", "A frightened scout asks you to guide them past the warband trails.", "guide_scout", 2),
    ExplorationEvent("root_shrine", "The Rootbound Shrine", "mosswood", "shrine", "Warm amber light pulses beneath a colossal root.", weight=2),
    ExplorationEvent("thorn_pit", "Thorn-Covered Pit", "mosswood", "trap", "Fresh leaves conceal a goblin pit trap.", "mooncap_spore", 2),
    ExplorationEvent("mosswood_trader", "Mooncap Herbalist", "mosswood", "merchant", "A masked herbalist quietly displays forest wares.", weight=2),

    ExplorationEvent("crypt_cache", "Sealed Burial Niche", "crypt", "treasure", "A cracked funerary seal reveals an untouched offering.", weight=3),
    ExplorationEvent("ash_urn", "Warden's Ash Urn", "crypt", "material", "Cold violet flame circles a bronze urn of sacred ash.", "warden_ash", 3),
    ExplorationEvent("warden_vault", "The Warden's Vault", "crypt", "landmark", "Behind fallen chains, you uncover the true Warden's Vault.", "warden_vault", 2),
    ExplorationEvent("bound_spirit", "A Bound Spirit", "crypt", "choice", "A lucid spirit asks you to break the sigil binding it here.", "free_spirit", 2),
    ExplorationEvent("ash_shrine", "Altar of Last Rest", "crypt", "shrine", "An undisturbed altar hums with peaceful light.", weight=2),
    ExplorationEvent("falling_stones", "Collapsing Passage", "crypt", "trap", "The ceiling groans and showers the passage with dust.", "warden_ash", 2),
    ExplorationEvent("crypt_trader", "Relic Appraiser", "crypt", "merchant", "A fearless appraiser sorts relics beside the crypt gate.", weight=2),

    ExplorationEvent("throne_cache", "Obsidian Reliquary", "throne", "treasure", "A black reliquary pulses between extinguished braziers.", weight=3),
    ExplorationEvent("void_ember", "Primordial Ember", "throne", "material", "A fragment of undying void-fire floats above the floor.", "void_ember", 3),
    ExplorationEvent("void_gallery", "The Hidden Void Gallery", "throne", "landmark", "A false wall dissolves, revealing murals older than the throne.", "void_gallery", 2),
    ExplorationEvent("penitent_shade", "The Penitent Shade", "throne", "choice", "A demon shade offers a secret in exchange for mercy.", "spare_shade", 2),
    ExplorationEvent("eclipse_shrine", "Eclipse Shrine", "throne", "shrine", "Twin flames—one gold, one violet—burn without fuel.", weight=2),
    ExplorationEvent("void_rift", "Unstable Void Rift", "throne", "trap", "Space fractures across your path with a deafening crack.", "void_ember", 2),
    ExplorationEvent("throne_trader", "The Last Merchant", "throne", "merchant", "An impossible merchant waits where no mortal should stand.", weight=2),
)


def events_for_region(region_key):
    return tuple(event for event in EVENTS if event.region == region_key)


def choose_exploration_event(player, region_key, rng=None):
    rng = rng or random
    discovered = set(getattr(player, "discovered_landmarks", []))
    choices = set(getattr(player, "story_choices", []))
    candidates = []
    for event in events_for_region(region_key):
        if event.kind == "landmark" and event.target in discovered:
            continue
        if event.kind == "choice" and any(choice == event.target or choice.startswith(f"{event.target}:") for choice in choices):
            continue
        candidates.append(event)
    if not candidates:
        candidates = [event for event in events_for_region(region_key) if event.kind not in {"landmark", "choice"}]
    return rng.choices(candidates, weights=[event.weight for event in candidates], k=1)[0]
