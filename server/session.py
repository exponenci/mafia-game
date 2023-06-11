import asyncio
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional

from vote_pool import VotePool


PLAYERS_COUNT = 4
MAFIA_COUNT = 1


class Role(Enum):
    MAFIA = 1
    CITIZEN = 2
    COMMISSAR = 3


@dataclass
class Player:
    username: str
    session_id: Optional[str] = None

    accept_core_notifications: bool = True


@dataclass
class Notification:
    class NotificationType(Enum):
        REGULAR = 1
        SESSION_INFO = 2
        TURN_INFO = 3
        RESULT = 4

    data: Dict[str, str] # field - value
    type: NotificationType # notification type
    receiver: Optional[str] = None


@dataclass
class Session:
    session_id: str
    players: Dict[str, Player] = field(default_factory=dict) # players pool

    turn: Role = Role.CITIZEN
    session_is_over: bool = False
    notifications: List[Notification] = field(default_factory=list) # session notifications [notification, receiver group]

    roles_distribution: Dict[str, Role] = field(default_factory=dict) # roles for players
    citizens: List[str] = field(default_factory=list) # alive citizen players
    mafia: List[str] = field(default_factory=list) # alive mafia players
    commissar: Optional[str] = None # commissar player if alive, none otherwise
    killed_players: List[str] = field(default_factory=list) # killed session players

    vote_pool: VotePool = VotePool() # vote pool
    
    next_turn_map = {
        Role.CITIZEN: Role.MAFIA,
        Role.MAFIA: Role.COMMISSAR,
        Role.COMMISSAR: Role.CITIZEN,
    }

    def preprocess(self):
        self._distribute_roles()
        self._prepare_notifications()
        self._reset()

    def _distribute_roles(self):
        players = list(self.players.keys())
        self.commissar = list(random.choices(players))[0]
        self.roles_distribution[self.commissar] = Role.COMMISSAR

        players = list(set(players) - set([self.commissar]))
        self.mafia = random.choices(players, k=MAFIA_COUNT)
        for mafia_player in self.mafia:
            self.roles_distribution[mafia_player] = Role.MAFIA

        self.citizens = list(set(players) - set(self.mafia))
        for citizen in self.citizens:
            self.roles_distribution[citizen] = Role.CITIZEN

    def _prepare_notifications(self):
        self.notifications += [
            Notification(
                {
                    'message': 'Session found...'
                },
                Notification.NotificationType.REGULAR,
                'all'
            ),
            Notification(
                {
                    'session_id': self.session_id, 
                    'role': Role.MAFIA, 
                    'players': list(self.players.keys())
                }, 
                Notification.NotificationType.SESSION_INFO,
                'mafia'
            ),
            Notification(
                {
                    'session_id': self.session_id, 
                    'role': Role.CITIZEN, 
                    'players': list(self.players.keys())
                }, 
                Notification.NotificationType.SESSION_INFO,
                'citizen'
            ),
            Notification(
                {
                    'session_id': self.session_id, 
                    'role': Role.COMMISSAR, 
                    'players': list(self.players.keys())
                }, 
                Notification.NotificationType.SESSION_INFO,
                'commissar' 
            ),
            Notification(
                {
                    'message': 'The night is coming...'
                },
                Notification.NotificationType.REGULAR,
                'all'
            ),
        ]
        for player in self.players.values():
            player.accept_core_notifications = False

    def _reset(self, update_turn: bool = True, **kwargs):
        if update_turn:
            self.turn = self.next_turn_map[self.turn]
        
        commissar_list = []
        if self.commissar:
            commissar_list.append(self.commissar)

        if self.turn == Role.MAFIA:
            self.vote_pool.reset(self.mafia, self.citizens + commissar_list)
        elif self.turn == Role.CITIZEN:
            alive_players = self.mafia + self.citizens + commissar_list
            self.vote_pool.reset(alive_players, alive_players)
        elif commissar_list:
            self.vote_pool.reset(commissar_list, self.citizens + self.mafia)

        kwargs['turn'] = self.turn
        kwargs['vote_options'] = list(self.vote_pool.target_votes.keys())
        print(kwargs)
        self.notifications.append(Notification(
            data=kwargs,
            type=Notification.NotificationType.TURN_INFO,
            receiver='all'
        ))

    def _kill(self, username: str):
        role: Role = self.roles_distribution[username]
        self.killed_players.append(username)
        if role == Role.MAFIA:
            self.mafia.remove(username)
        elif role == Role.CITIZEN:
            self.citizens.remove(username)
        else:
            self.commissar = None
            self.next_turn_map[Role.MAFIA] = Role.CITIZEN

    def _is_game_over(self):
        if self.commissar is not None:
            commissar_i = 1
        else:
            commissar_i = 0
        return len(self.mafia) == 0 or len(self.mafia) >= len(self.citizens) + commissar_i

    async def send_notifications(self, username: str):
        role = self.roles_distribution[username]
        notif_i = 0
        while not self.session_is_over or notif_i < len(self.notifications):
            while notif_i < len(self.notifications):
                notif: Notification = self.notifications[notif_i]
                print("SENDING NOTIF")
                if notif.receiver == 'all':
                    print(notif)
                    if notif.type == Notification.NotificationType.TURN_INFO:
                        # we don't want send options to all clients, only to the appropriate ones
                        if (role != Role.MAFIA and notif.data['turn'] == Role.MAFIA) or \
                                (role != Role.COMMISSAR and notif.data['turn'] == Role.COMMISSAR):
                            copy_data = notif.data.copy()
                            copy_data['vote_options'] = []
                            modified_notif = Notification(copy_data, notif.type, notif.receiver)
                            print('MODIFIED', modified_notif)
                            yield modified_notif
                        else:
                            yield notif
                    else:
                        yield notif
                elif username in self.killed_players or \
                        (role == Role.MAFIA and notif.receiver == 'mafia') or \
                        (role == Role.COMMISSAR and notif.receiver == 'commissar') or \
                        (role == Role.CITIZEN and notif.receiver == 'citizen'):
                    yield notif
                notif_i += 1
            await asyncio.sleep(1)

    async def accept_vote(self, username: str, target: str):
        print("ACCEPT VOTE FROM", username, "TO", target)
        if self.session_is_over:
            print("BROKE 1")
            return {
                'message': 'Session is over!'
            }
        if not self.vote_pool.accept_vote(username, target):
            print("BROKE 2")
            return {
                'message': 'Invalid vote params! Check your username and the one you are picking!'
            }
        print("CONT")
        if self.vote_pool.is_full():
            print("IS FULL")
            if self.vote_pool.is_valid():
                target_username = self.vote_pool.get_poll_result()
                target_role = self.roles_distribution[target_username]
                if self.turn != Role.COMMISSAR:
                    self._kill(target_username)
                    self._reset(
                        target_role=target_role, 
                        target_username=target_username
                    )
                else:
                    self._reset(
                        target_role=target_role, 
                        target_username='<?>'
                    )
 
                if self._is_game_over():
                    self.session_is_over = True
                    clients = list()
                    for username in self.players.keys():
                        clients.append(
                            {
                                'username': username,
                                'alive': username not in self.killed_players,
                                'role': self.roles_distribution[username]
                            }
                        )
                    self.notifications.append(Notification(
                        data={
                            'citizens_wins': len(self.mafia) == 0,
                            'clients': clients
                        },
                        type=Notification.NotificationType.RESULT,
                        receiver='all'
                    ))
            else:
                self._reset(update_turn=False)
                self.notifications.append(Notification(
                    data={
                        'message': 'There are several candidates with equal max vote-counts... Revote is required!'
                    },
                    type=Notification.NotificationType.REGULAR,
                    receiver='all'
                ))
        return {}
