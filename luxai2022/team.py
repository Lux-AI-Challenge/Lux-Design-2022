from dataclasses import dataclass
from enum import Enum
from luxai2022.globals import TERM_COLORS
from termcolor import colored
@dataclass
class FactionInfo:
    color: str = "none"
    alt_color: str = "red"
    faction_id: int = -1


class FactionTypes(Enum):
    AlphaStrike = FactionInfo(color="yellow", faction_id=0)
    MotherMars = FactionInfo(color="green", faction_id=1)
    TheBuilders = FactionInfo(color="blue", faction_id=2)
    FirstMars = FactionInfo(color="red", faction_id=3)


class Team:
    def __init__(self, team_id: int, agent: str, faction: FactionTypes = None) -> None:
        self.faction = faction
        self.team_id = team_id
        # the key used to differentiate ownership of things in state
        self.agent = agent
    def state_dict(self):
        return dict(
            team_id=self.team_id,
            faction=self.faction.name
        )
    def __str__(self) -> str:
        out = f"[Player {self.team_id}]"
        if TERM_COLORS:
            return colored(out, self.faction.value.color)
        return out
