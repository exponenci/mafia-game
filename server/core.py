import asyncio
import random
import string
from typing import Dict

from session import Session, Notification, Player, PLAYERS_COUNT


class Core:
    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = dict()
        self._players: Dict[str, Player] = dict()
        self._players_queue = asyncio.Queue(maxsize=PLAYERS_COUNT)
        self._recent_notifications = list()

    @staticmethod
    def generate_string_id(n: int = 6):
        return ''.join(
            random.choice(
                string.ascii_uppercase + string.digits
            ) for _ in range(n)
        )

    def _create_session(self):
        while True:
            session_id = self.generate_string_id()
            if session_id not in self._sessions:
                break

        session_clients: Dict[str, Player] = dict()
        for _ in range(PLAYERS_COUNT):
            username = self._players_queue.get_nowait()
            session_clients[username] = self._players[username]
            session_clients[username].session_id = session_id

        session = Session(session_id, session_clients)
        session.preprocess()
        self._sessions[session_id] = session

    async def connect_player(self, username: str):
        if username in self._players:
            return {'message': 'error: username already taken'}

        self._players[username] = Player(session_id='', username=username)

        self._recent_notifications = self._recent_notifications[-9:]
        self._recent_notifications.append(username + ' connected')

        await self._players_queue.put(username)
        if self._players_queue.full():
            self._create_session()
        
        return {}

    async def wait_in_queue(self, username: str):
        if username not in self._players:
            return {'message': 'error: username not found'}

        self._players[username].accept_core_notifications = True
        self._recent_notifications = self._recent_notifications[-9:]
        self._recent_notifications.append(username + ' added in queue')

        await self._players_queue.put(username)
        if self._players_queue.full():
            await self.create_session()
        
        return {}

    async def disconnect_player(self, username: str):
        if username not in self._players:
            return {'message': 'error: username not found'}

        player: Player = self._players.pop(username)
        player.accept_core_notifications = False

        self._recent_notifications = self._recent_notifications[-9:]
        self._recent_notifications.append(username + ' disconnected')

        return {}

    async def send_notifications(self, username: str):
        if username not in self._players:
            yield Notification(
                {'message': 'error: username not found'}, 
                Notification.NotificationType.REGULAR,
            )
            return
        player: Player = self._players[username]
        while player.accept_core_notifications:
            yield Notification(
                {'message': 'recently notifications players:\n\n  ' + 
                            '\n  '.join(self._recent_notifications[::-1])}, 
                Notification.NotificationType.REGULAR,
            )
            await asyncio.sleep(1.5)
        if player.session_id is None or player.session_id not in self._sessions:
            return
        session = self._sessions[player.session_id]
        async for notif in session.send_notifications(username):
            yield notif

    async def accept_vote(self, username: str, target: str, session_id: str):
        if session_id not in self._sessions:
            return {'message': 'session_id is not found'}
        return await self._sessions[session_id].accept_vote(username, target)
