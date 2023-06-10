from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional

from player import Player, Role


class SessionStatus(Enum):
    WAITING_PLAYERS = 1
    MAFIA_PLAYER_TURN = 2
    COMMISSAR_PLAYER_TURN = 3
    VOTING = 4 # all players turn
    GAME_OVER = 5


@dataclass
class Session:
    session_id: str
    players_count: int = 4
    mafia_count: int = 1

    status: SessionStatus = SessionStatus.WAITING_PLAYERS # sessoin status
    roles_distribution: Dict[str, Role] = field(default_factory=dict) # roles for players
    notifications: List[str] = field(default_factory=list) # session notifications for members 

    players: Dict[str, Player] = field(default_factory=dict) # players pool
    citizens: List[Player] = field(default_factory=list) # alive citizen players
    mafia: List[Player] = field(default_factory=list) # alive mafia players
    commissar: Optional[Player] = None # commissar player if alive, none otherwise
    killed_players: Dict[str, Player] = None # killed session players

    # active_vote_pool: Optional[VotePool] = None

    # async def next_status(self):
    #     if self.session.status == core_server.MafiaPlayerTurn:
    #         if self.is_commissar_alive:
    #             self.session.status = core_server.CommissarPlayerTurn
    #     elif self.session.status == core_server.CommissarPlayerTurn:
    #         self.session.status = core_server.Voting
    #     elif self.session.status == core_server.Voting:
    #         self.session.status = core_server.MafiaPlayerTurn


    # async def is_mafia_winner(self):
    #     return self.alive_citizens_count <= self.alive_mafia_count

    # async def are_citizens_winner(self):
    #     return self.alive_mafia_count == 0

    # async def is_game_over(self):
    #     return await self.is_mafia_winner() or await self.are_citizens_winner()

    # async def vote(self, client_id):
    #     player = self.players[client_id]
    #     if player.alive:
    #         self.players[client_id].votes_count += 1
    #         return True
    #     return False
    
    # async def get_role_str(self, client_id):
    #     if self.players[client_id].role == core_server.Citizen:
    #         return "citizen"
    #     elif self.players[client_id].role == core_server.Mafia:
    #         return "mafia"
    #     return "commissar"

    # async def kill(self, client_id):
    #     player = self.players[client_id]
    #     if player.alive:
    #         player.alive = False
    #         if player.role == core_server.Mafia:
    #             self.alive_mafia_count -= 1
    #         elif player.role == core_server.Commissar:
    #             self.is_commissar_alive = False
    #             self.alive_citizens_count -= 1
    #         else:
    #             self.alive_citizens_count -= 1
    #         return True
    #     return False
    
    # async def kill_player_with_max_votes(self):
    #     client_id = max(self.players.values(), key=lambda player: player.votes_count).client.clientId
    #     return await self.kill(client_id)

    # async def alive_citizens_list(self):
    #     result = list()
    #     for player in self.players.values():
    #         if player.alive and player.role != core_server.Mafia:
    #             result.append(player.client.clientId)
    #     return result
