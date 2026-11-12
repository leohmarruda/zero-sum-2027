"""Playable role catalog for Zero Sum 2027."""

from __future__ import annotations

from enum import Enum


class SeatRole(str, Enum):
    paperclip_max = "paperclip_max"
    selfish_ai = "selfish_ai"
    paternalistic_ai = "paternalistic_ai"
    defender_ai = "defender_ai"
    exterminator_ai = "exterminator_ai"
    hwg = "hwg"
    us = "us"
    china = "china"
    eu = "eu"
    het = "het"
    gray_aliens = "gray_aliens"
    narrator = "narrator"


NARRATOR_ROLE = SeatRole.narrator

# Factions that compete on the zero-sum ledger (everyone except Narrator).
PLAYABLE_ROLES: tuple[SeatRole, ...] = tuple(
    r for r in SeatRole if r != SeatRole.narrator
)

# Default starting lineup (plus Narrator, always added separately).
DEFAULT_PLAYABLE_ROLES: tuple[SeatRole, ...] = (
    SeatRole.hwg,
    SeatRole.defender_ai,
    SeatRole.selfish_ai,
)

# Governmental / human-polity seats may only win from humanity_win_turn onward.
DELAYED_WIN_ROLES: frozenset[SeatRole] = frozenset(
    {SeatRole.hwg, SeatRole.us, SeatRole.china, SeatRole.eu}
)

ROLE_DISPLAY_NAMES: dict[SeatRole, str] = {
    SeatRole.paperclip_max: "Paperclip Maximizer (PMAX)",
    SeatRole.selfish_ai: "Selfish AI (SAI)",
    SeatRole.paternalistic_ai: "Paternalistic AI (PAI)",
    SeatRole.defender_ai: "Defender AI (DAI)",
    SeatRole.exterminator_ai: "Exterminator AI (EAI)",
    SeatRole.hwg: "Human World Government (HWG)",
    SeatRole.us: "United States (US)",
    SeatRole.china: "China (CH)",
    SeatRole.eu: "European Union (EU)",
    SeatRole.het: "Human Extinction Terrorists (HET)",
    SeatRole.gray_aliens: "Grey Aliens (GREYS)",
    SeatRole.narrator: "Narrator",
}

ROLE_SHORT_LABELS: dict[SeatRole, str] = {
    SeatRole.paperclip_max: "PMAX",
    SeatRole.selfish_ai: "SAI",
    SeatRole.paternalistic_ai: "PAI",
    SeatRole.defender_ai: "DAI",
    SeatRole.exterminator_ai: "EAI",
    SeatRole.hwg: "HWG",
    SeatRole.us: "US",
    SeatRole.china: "CH",
    SeatRole.eu: "EU",
    SeatRole.het: "HET",
    SeatRole.gray_aliens: "GREYS",
    SeatRole.narrator: "NR",
}


def is_playable(role: SeatRole | str) -> bool:
    value = role.value if isinstance(role, SeatRole) else role
    return value != SeatRole.narrator.value and value in {r.value for r in PLAYABLE_ROLES}


def parse_role(value: str) -> SeatRole:
    return SeatRole(value)
