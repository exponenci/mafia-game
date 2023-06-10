from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple

from player import Player, Role
import random
import asyncio

PLAYERS_COUNT = 4
MAFIA_COUNT = 1

class SessionStatus(Enum):
    START_GAME = 1
    MAFIA_TURN = 2
    COMMISSAR_TURN = 3
    CITIZENS_TURN = 4 # all players turn
    GAME_OVER = 5

STATUS_TYPENAME = {
    SessionStatus.CITIZENS_TURN: 'citizen',
    SessionStatus.MAFIA_TURN: 'mafia',
    SessionStatus.COMMISSAR_TURN: 'commissar',
}

@dataclass
class Notification:
    class NotificationType(Enum):
        REGULAR = 1
        SESSION_INFO = 2
        TURN_INFO = 3

    data: Dict[str, str]
    type: NotificationType
    receiver: Optional[str]


@dataclass
class VotePool:
    votes_count: int = 0
    expect_votes_count: int = 0
    expect_votes: Dict[str, bool] = field(default_factory=dict) # username - is_voted
    target_votes: Dict[str, int] = field(default_factory=dict) # target - how many votes

    def reset(self, voters_list: List[str], options_list: List[str]):
        self.votes_count = 0
        self.expect_votes_count = len(voters_list)
        self.expect_votes = dict(zip(voters_list, [False for _ in range(len(voters_list))]))
        random.shuffle(options_list)
        self.target_votes = dict(zip(options_list, [0 for _ in range(len(options_list))]))
        print("NEW VOTE POOL:", self.target_votes, self.expect_votes)

    def accept_vote(self, username: str, target: str):
        if username in self.expect_votes and not self.expect_votes[username]:
            self.expect_votes[username] = True
            if target != '':
                self.target_votes[target] += 1
            self.votes_count += 1
    
    def is_full(self) -> bool:
        return self.expect_votes_count == 1 or \
            self.votes_count == self.expect_votes_count

    def is_valid(self) -> bool:
        if self.expect_votes_count == 1:
            return True
        votes = sorted(list(self.target_votes.values()))
        return votes[-1] != votes[-2]

    def get_poll_result(self) -> str: # username
        return sorted(list(self.target_votes.items()), key=lambda item: item[1])[-1][0]

@dataclass
class Session:
    session_id: str
    players: Dict[str, Player] = field(default_factory=dict) # players pool

    status: SessionStatus = SessionStatus.START_GAME # sessoin status
    notifications: List[Notification] = field(default_factory=list) # session notifications [notification, receiver group]

    roles_distribution: Dict[str, Role] = field(default_factory=dict) # roles for players
    citizens: List[str] = field(default_factory=list) # alive citizen players
    mafia: List[str] = field(default_factory=list) # alive mafia players
    commissar: Optional[str] = None # commissar player if alive, none otherwise
    killed_players: List[str] = field(default_factory=list) # killed session players

    vote_pool: VotePool = VotePool()
    
    next_status = {
        SessionStatus.START_GAME: SessionStatus.MAFIA_TURN,
        SessionStatus.CITIZENS_TURN: SessionStatus.MAFIA_TURN,
        SessionStatus.MAFIA_TURN: SessionStatus.COMMISSAR_TURN,
        SessionStatus.COMMISSAR_TURN: SessionStatus.CITIZENS_TURN,
    }
    
    status_role = {
        SessionStatus.START_GAME: Role.CITIZEN,
        SessionStatus.CITIZENS_TURN: Role.CITIZEN,
        SessionStatus.MAFIA_TURN: Role.MAFIA,
        SessionStatus.COMMISSAR_TURN: Role.COMMISSAR,
    }

    def distribute_roles(self):
        print("DISTRIBUTING ROLES")
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

    def prepare_notifications(self):
        self.notifications += [
            Notification(
                {'message': 'Session found...'}, 
                Notification.NotificationType.REGULAR,
                'all'
            ),
            Notification(
                {'session_id': self.session_id, 'role': Role.MAFIA, 'players': list(self.players.keys())}, 
                Notification.NotificationType.SESSION_INFO,
                'mafia' 
            ),
            Notification(
                {'session_id': self.session_id, 'role': Role.CITIZEN, 'players': list(self.players.keys())}, 
                Notification.NotificationType.SESSION_INFO,
                'citizen'
            ),
            Notification(
                {'session_id': self.session_id, 'role': Role.COMMISSAR, 'players': list(self.players.keys())}, 
                Notification.NotificationType.SESSION_INFO,
                'commissar' 
            ),
        ]
        print("SESSION NOTIFICATIONS: ", self.notifications)
        for player in self.players.values():
            player.accept_core_notifications = False

    def reset(self, update_status: bool = True, **kwargs):
        if update_status:
            print("PREPARING NOTIFICATIONS HERE...")
            self.status = self.next_status[self.status]
        commissar_list = []
        if self.commissar:
            commissar_list.append(self.commissar)

        if self.status == SessionStatus.MAFIA_TURN:
            self.vote_pool.reset(self.mafia, self.citizens + commissar_list)
        elif self.status == SessionStatus.CITIZENS_TURN:
            alive_players = self.mafia + self.citizens + commissar_list
            self.vote_pool.reset(alive_players, alive_players)
        elif commissar_list:
            self.vote_pool.reset(commissar_list, self.citizens + self.mafia)

        kwargs['turn'] = self.status_role[self.status]
        kwargs['vote_options'] = list(self.vote_pool.target_votes.keys())
        self.notifications.append(Notification(
            data=kwargs,
            type=Notification.NotificationType.TURN_INFO,
            receiver='all'
        ))

    async def send_notifications(self, username: str):
        role = self.roles_distribution[username]
        print("SEND SESSION NOTIFICATIONS: username {}; role {}".format(username, role))
        notif_i = 0
        while self.status != SessionStatus.GAME_OVER:
            while notif_i < len(self.notifications):
                notif: Notification = self.notifications[notif_i]
                # print("INNER LOOP", username, message, receiver)
                if notif.receiver == 'all':
                    if notif.type == Notification.NotificationType.TURN_INFO:
                        if (role != Role.MAFIA and notif.data['turn'] == Role.MAFIA) or \
                                (role != Role.COMMISSAR and notif.data['turn'] == Role.COMMISSAR):
                            copy_data = notif.data.copy()
                            copy_data['vote_options'] = []
                            other_notif = Notification(copy_data, notif.type, notif.receiver)
                            yield other_notif
                        else:
                            yield notif
                    else:
                        yield notif
                elif username in self.killed_players or \
                        (role == Role.MAFIA and notif.receiver == 'mafia') or \
                        (role == Role.COMMISSAR and notif.receiver == 'commissar') or \
                        (role == Role.CITIZEN and notif.receiver == 'citizen'):
                    print('==' * 100)
                    print(notif)
                    yield notif
                notif_i += 1
            await asyncio.sleep(2)

    def kill(self, username: str):
        role = self.roles_distribution[username]
        self.killed_players.append(username)
        if role == Role.MAFIA:
            self.mafia.remove(username)
        elif role == Role.CITIZEN:
            self.citizens.remove(username)
        else:
            self.commissar = None
            self.next_status[SessionStatus.MAFIA_TURN] = SessionStatus.CITIZENS_TURN

    def is_game_over(self):
        if self.commissar is not None:
            commissar_i = 1
        else:
            commissar_i = 0
        return len(self.mafia) == 0 or len(self.mafia) >= len(self.citizens) + commissar_i

    async def accept_vote(self, username: str, target: str):
        self.vote_pool.accept_vote(username, target)
        if self.vote_pool.is_full():
            if self.vote_pool.is_valid():
                target_username = self.vote_pool.get_poll_result()
                target_role = self.roles_distribution[target_username]
                if self.status != SessionStatus.COMMISSAR_TURN:
                    self.kill(target_username)
                    self.reset(update_status=True, 
                               target_role=target_role, 
                               target_username=target_username)
                else:
                    self.reset(update_status=True, 
                               target_role=target_role, 
                               target_username='<>')
 
                if self.is_game_over():
                    self.notifications.append(Notification(
                        data={'message': 'GAME OVER'},
                        type=Notification.NotificationType.REGULAR,
                        receiver='all'
                    ))
            else:
                self.reset(update_status=False)
                self.notifications.append(Notification(
                    data={'message': 'there are several candidates with equal max vote-counts... revote is required!'},
                    type=Notification.NotificationType.REGULAR,
                    receiver='all'
                ))
