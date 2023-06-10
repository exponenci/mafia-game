from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional


class Role(Enum):
    MAFIA = 1
    CITIZEN = 2
    COMMISSAR = 3


@dataclass
class Player:
    username: str
    session_id: Optional[str] = None

    accept_core_notifications: bool = True

    # role: Role = Role.UNDEFINED # players role
    # voted: bool = False # whether player voted
    # alive: bool = True # whether player is alive
    # votes_count: int = 0 # how many players voted for this user
