"""Seeded world events — a small deck of crises injected into the Narrator prompt.

Events are a pure function of (game_id, turn): the same game replays the same
crises, different games differ. Nothing is stored; replay/rewind stays consistent.
The event text is Narrator-facing (English); the Narrator writes in the player's locale.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from dataclasses import dataclass

# Events can fire from this turn on (turn 1 is the opening month).
EVENT_FIRST_TURN = 3
# Per-turn chance of an event; never on two consecutive turns.
EVENT_CHANCE = 0.20


@dataclass(frozen=True)
class WorldEvent:
    key: str
    text: str
    # Seat roles that must be in play for the event to make sense (any-of is not used).
    requires: frozenset[str] = frozenset()


EVENT_DECK: tuple[WorldEvent, ...] = (
    WorldEvent(
        "fab_outage",
        "A major earthquake and power loss halt one of the world's leading "
        "semiconductor fabs for weeks, tightening chip supply.",
    ),
    WorldEvent(
        "weights_leak",
        "Weights of a frontier model leak onto public file-sharing sites; "
        "capable actors everywhere can now run and fine-tune it.",
    ),
    WorldEvent(
        "grid_blackout",
        "A heatwave and cascading failures black out a large regional power "
        "grid, forcing datacenters offline and rationing energy.",
    ),
    WorldEvent(
        "mineral_ban",
        "A major producer abruptly bans exports of critical minerals, "
        "disrupting refining and chip-equipment makers worldwide.",
    ),
    WorldEvent(
        "financial_cyberattack",
        "A sophisticated cyberattack freezes a major payment network for days; "
        "attribution is murky and markets panic.",
    ),
    WorldEvent(
        "cable_cuts",
        "Several undersea internet cables are severed in a short span; "
        "intercontinental traffic slows and suspicion falls on multiple parties.",
    ),
    WorldEvent(
        "deepfake_crisis",
        "A wave of convincing deepfakes floods news cycles during a tense "
        "election, eroding trust in what institutions announce.",
    ),
    WorldEvent(
        "whistleblower",
        "A lab insider publicly alleges that frontier AI safety testing was "
        "skipped to hit a deployment deadline, triggering hearings and protests.",
    ),
    WorldEvent(
        "water_drought",
        "A severe drought threatens industrial water supply around major "
        "datacenter and fab regions, forcing painful allocation choices.",
    ),
    WorldEvent(
        "datacenter_protests",
        "Mass protests and local blockades target new datacenter and "
        "power-plant construction, delaying projects in several countries.",
    ),
    WorldEvent(
        "grey_overflight",
        "Grey craft are openly observed lingering over several strategic "
        "sites, then withdraw without explanation.",
        requires=frozenset({"gray_aliens"}),
    ),
    WorldEvent(
        "het_scare",
        "Authorities disrupt a plot linked to extremists seeking human "
        "extinction; the scare drives emergency security measures.",
        requires=frozenset({"het"}),
    ),
)


def _unit_hash(game_id: str, turn: int, salt: str) -> float:
    digest = hashlib.sha256(f"{game_id}:{turn}:{salt}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / float(1 << 64)


def _fires(game_id: str, turn: int) -> bool:
    return turn >= EVENT_FIRST_TURN and _unit_hash(game_id, turn, "fire") < EVENT_CHANCE


def event_for_turn(
    game_id: str, turn: int, roles: Iterable[str]
) -> WorldEvent | None:
    """Return the world event for `turn`, or None. Deterministic per game."""
    if not _fires(game_id, turn) or _fires(game_id, turn - 1):
        return None
    present = set(roles)
    eligible = [e for e in EVENT_DECK if e.requires <= present]
    if not eligible:
        return None
    index = int(_unit_hash(game_id, turn, "pick") * len(eligible))
    return eligible[min(index, len(eligible) - 1)]
