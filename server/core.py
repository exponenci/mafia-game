from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any

import asyncio

from player import Player
from session import Session, PLAYERS_COUNT, Notification

from threading import Lock
import threading


class Core:
    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = dict()
        self._players: Dict[str, Player] = dict()
        self._players_queue = asyncio.Queue(maxsize=PLAYERS_COUNT)
        self._recent_notifications = list()

    async def create_session(self):
        session_id = 'random_session_id'
        players: Dict[str, Player] = dict()
        for _ in range(PLAYERS_COUNT):
            username = self._players_queue.get_nowait()
            players[username] = self._players[username]
            players[username].session_id = session_id
        session = Session(session_id, players)
        session.distribute_roles()
        session.prepare_notifications()
        session.reset()
        self._sessions[session_id] = session

    async def connect_player(self, username: str) -> bool:
        if username in self._players:
            return {
                'message': 'error: username already taken'
            }

        self._players[username] = Player(session_id='', username=username)

        self._recent_notifications = self._recent_notifications[-9:]
        self._recent_notifications.append(username + ' connected')
        self._players_queue.put_nowait(username)

        print("QSIZE: ", self._players_queue.qsize())
        if self._players_queue.full():
            await self.create_session()
        
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

        self._recent_notifications = self._recent_notifications[-9:]
        self._recent_notifications.append(username + ' disconnected')

        return {
            'message': 'see you soon'
        }

    async def core_notifications(self, username: str):
        print(username)
        if username not in self._players:
            yield Notification(
                {'message': 'error: no username in db'}, 
                Notification.NotificationType.REGULAR,
                receiver=''
            )
        else:
            player: Player = self._players[username]
 
            while player.accept_core_notifications:
                print("CORE NOTIFICATION FOR USER ", player.username)
                yield Notification(
                    {'message': 'recently notifications players:\n' + '\n'.join(self._recent_notifications[::-1])}, 
                    Notification.NotificationType.REGULAR,
                    receiver=''
                )
                await asyncio.sleep(1.5)
            print("FINISHED CORE NOTIFICATIONS")
            if player.session_id is None or player.session_id not in self._sessions:
                return
            session = self._sessions[player.session_id]
            async for notif in session.send_notifications(username):
                print("SESSION NOTIFICATION FOR USER", player.username)
                print(notif)
                yield notif
    
    async def count_vote(self, username: str, target: str, session_id: str):
        if session_id not in self._sessions:
            return # throw error
        await self._sessions[session_id].accept_vote(username, target)


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
