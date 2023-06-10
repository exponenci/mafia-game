from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any

import asyncio

from player import Player
from session import Session

from threading import Lock
import threading


class Core:
    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = dict()
        self._players: Dict[str, Player] = dict()
        self._recent_notifications = list()

    async def connect_player(self, username: str) -> bool:
        if username in self._players:
            return {
                'message': 'username already taken'
            }

        self._players[username] = Player(session_id='', username=username)

        self._recently_connected = self._recently_connected[-9:]
        self._recent_notifications.append(username + ' connected')
        
        return {
            'message': 'welcome'
        }

    async def disconnect_player(self, username: str):
        if username not in self._players:
            return {
                'message': 'username not found'
            }
        player: Player = self._players.pop(username)
        player.accept_core_notifications = False

        self._recently_connected = self._recently_connected[-9:]
        self._recent_notifications.append(username + ' disconnected')

        return {
            'message': 'see you soon'
        }

    async def core_notifications(self, username: str):
        print("core_notifications")
        if username not in self._players:
            yield {
                'message': 'username not found'
            }
        else:
            player: Player = self._players[username]
 
            while player.accept_core_notifications:
                print("NOTIFICATION FOR USER ", player.username)
                yield {
                    'message': 'recently notifications players:\n' + '\n'.join(self._recent_notifications[::-1])
                }
                await asyncio.sleep(1.5)

    # def get_session_info(self, session_id: str) -> Dict[str, Any]:
    #     if session_id not in self._sessions:
    #         return {
    #             'message': 'SESSION NOT FOUND'
    #         }
    #     session: Session = self._sessions[session_id]
    #     return {
    #         'message': 'SESSION INFO',
    #         'session_id': session_id,
    #         'players_count': session.players_count,
    #         'mafia_count': session.mafia_count,
    #         'players': session.players.keys()
    #     }

    # def start_session(self, username: str, players_count: int = 4, mafia_count: int = 1) -> Dict[str, str]:
    #     if players_count < 4 or players_count > 10 or mafia_count < 1 or mafia_count > players_count / 4:
    #         return {
    #             'message': 'game settings error: provide valid players count'
    #         }
    #     if username not in self._players:
    #         return {
    #             'message': 'game settings error: firstly register player'
    #         }

    #     while True:
    #         # generaing session_id
    #         session_id = self.generate_session_id()
    #         if session_id not in self._sessions:
    #             break

    #     # creating session instance
    #     session = Session(
    #         session_id=session_id,
    #         players_count=players_count,
    #         mafia_count=mafia_count
    #     )
    #     self._sessions[session_id] = session
    #     session.distribute_roles()

    #     # adding player to session
    #     player: Player = self._players[username]
    #     player.reset()
    #     session.add_player(player)
