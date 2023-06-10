from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict


class Role(Enum):
    UNDEFINED = 1
    MAFIA = 2
    CITIZEN = 3
    COMMISSAR = 4


@dataclass
class Player:
    session_id: str
    username: str
    accept_core_notifications: bool = True
    notifications: List[str] = field(default_factory=list)

    role: Role = Role.UNDEFINED # players role
    voted: bool = False # whether player voted
    alive: bool = True # whether player is alive
    votes_count: int = 0 # how many players voted for this user
