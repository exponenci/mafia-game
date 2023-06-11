import os
import sys
import inspect

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0, parentdir + '/proto')

import grpc
import time
import re
import asyncio

import logging
import random
from typing import Iterable, List, Optional, Tuple, Dict

import grpc
import proto.server_pb2 as server_pb2
import proto.server_pb2_grpc as server_pb2_grpc
from dataclasses import dataclass, field



@dataclass
class ClientCore:
    # session info for client
    username: str = ''
    session_id: str = ''
    role: str = ''
    alive: bool = True
    voted: bool = False
    session_players: List[str] = field(default_factory=list) # username
    killed_players: List[Tuple[str, str]] = field(default_factory=list) # username, role

    # turn info
    turn: str = ''
    prev_turn: str = ''
    target: Optional[Tuple[str, str]] = None # username, role
    vote_options: Optional[List[str]] = None # usernames

    def print(self, line, prefix: str = ''):
        if prefix == '':
            if self.session_id == '':
                os.system('clear')
                prefix = 'core'
            else:
                prefix = 'session'
        print(f'${prefix}> ' + line, flush=True)
    
    def input(self, prefix: str = 'me'):
        return input(f'${prefix}> ').strip()

    def print_session_info(self):
        self.print(f'You are connected to session#{self.session_id}')
        self.print(f'Your role: {self.role}')
        self.print(f'Players in session:')
        for player_username in self.session_players:
            self.print(f'- {player_username}')

    def print_turn_info(self):
        if self.target is not None and self.target[0] != '':
            if self.prev_turn == 'Citizens':
                self.print(f'{self.target[0]} was hanged by citizens! He was {self.target[1]}...')
                self.print(f'The night is coming...')
            elif self.prev_turn == 'Mafia':
                self.print(f'{self.target[0]} was killed! He was {self.target[1]}...')
            elif self.prev_turn == 'Commissar':
                self.print(f'The player who was checked by commissar is {self.target[1]}!')
        self.print(f'{self.turn}\'s turn...')
        if self.alive and self.vote_options is not None and \
                len(self.vote_options) != 0 and \
                (self.turn == self.role or self.turn == 'Citizen'):
            self.print(f'pick someone from options below')
            for option in self.vote_options:
                self.print(f'- {option}')

    def print_result(self, citizens_wins: bool, data: dict):
        self.print(f"===  GAME OVER!   ===")
        if citizens_wins:
            self.print(f"=== CITIZENS WIN! ===")
        else:
            self.print(f"===  MAFIA WINS!  ===")
        for username, info in data.items():
            status = 'alive' if info[0] else 'dead'
            self.print(f"- {username}-{status}-{info[1]}")
    
    def reset(self):
        self.session_id = ''
        self.role = ''
        self.alive = True
        self.voted = False
        self.turn = ''
        self.prev_turn = ''
        self.target = None
        self.vote_options = None

    def set_session_info(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def set_turn_info(self, **kwargs):
        self.prev_turn = self.turn
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        if self.target is not None and self.target[0] == self.username:
            self.alive = False
        self.voted = False

    async def run(self) -> Iterable[Dict[str, str]]:        
        # !help = help
        # !tab = players info (username-alive-Role)
        # !status = role & is alive
        # !pick <name> = vote for <name>
        # !skip = skip vote (at least 1 vote must be provided) ?
        # !clear = clear terminal
        # !quit = quit, only when game is over
        print("RUN")
        while self.session_id != '':
            # print("TURN", self.turn)
            if not self.voted and self.alive and (self.turn == self.role or self.turn == 'Citizen'):
                data = self.input()
                # self.print('!pick')
                print("YOUR DATA:", data)
                if data.startswith('!'):
                    data = data.split()
                    if data[0] == '!help':
                        self.print('\n !tab            shows session info'
                                    '\n !status         shows your role and status'
                                    '\n !pick <name>    vote for/pick <name> for poll'
                                    '\n !clear          clears terminal'
                                    '\n !new            stay in queue to new session (only after the session is over)'
                                    '\n !exit           exit (only after the session is over)')
                    elif data[0] == '!tab':
                        self.print('Players:')
                        killed = dict(self.killed_players)
                        for username in self.session_players:
                            if username in killed:
                                self.print(f' - {username}-killed-{killed[username]}')
                            else:
                                self.print(f' - {username}-alive')
                    elif data[0] == '!status':
                        status = 'alive' if self.alive else 'dead'
                        self.print(f'Role: {self.role}. Status: {status}')
                    elif data[0] == '!pick' and self.turn != 'over' and \
                            self.alive and not self.voted and \
                            (self.turn == self.role or self.turn == 'Citizen'):
                        if data[1] != self.username and data[1] in self.vote_options:
                            self.voted = True
                            yield {'cmd': 'pick', 'arg': data[1]}
                        else:
                            self.print('Invalid !pick param')
                    elif data[0] == '!clear':
                        os.system('clear')
                    elif data[0] == '!new' and self.turn == 'over':
                        self.reset()
                        yield {'cmd': 'new'}
                        break
                    elif data[0] == '!exit' and self.turn == 'over':
                        break
            await asyncio.sleep(5)
        print("OUTOUTOUTT")
    # async def make_votes(self) -> Iterable[str]: # picked user
    #     while self.turn != 'over' and self.alive: # game is not over
    #         if not self.voted and (self.turn == self.role or self.turn == 'Citizen'):
    #             self.voted = True
    #             while True:
    #                 picked = input(f'$me> ').strip()
    #                 if picked != self.username and picked in self.vote_options:
    #                     break
    #             yield picked
    #         await asyncio.sleep(1)


class Client:
    def __init__(self, stub: server_pb2_grpc.IServerStub, core: ClientCore) -> None:
        self._stub: server_pb2_grpc.IServerStub = stub
        self._username: str = ''
        self._core: ClientCore = core

    @staticmethod
    def match_role(role: server_pb2.TSystemNotification.Role):
        # print(role)
        if role == server_pb2.TSystemNotification.MAFIA_ROLE:
            return 'Mafia'
        elif role == server_pb2.TSystemNotification.COMMISSAR_ROLE:
            return 'Commissar'
        return 'Citizen'

    async def connect_client(self) -> None:
        while True:
            self._core.print('Set your username below')
            username = self._core.input()
            if len(username) < 3 or not username.isalnum():
                self._core.print('Set name with 3 and more alnum symbols')
                continue
            response = await self._stub.ConnectClient(server_pb2.TPingRequest(
                username=username
            )) 
            if not response.message:
                self._core.print(f'Welcome, {username}!')
                break
            self._core.print(response.message)
        self._core.username = username
        self._username = username

    async def _get_system_notifications(self) -> None:
        notifications = self._stub.SubscribeForNotifications(server_pb2.TPingRequest(
            username=self._username
        ))
        async for notif in notifications:
            print(notif)
            if notif.type == server_pb2.TSystemNotification.REGULAR_MESSAGE:
                self._core.print(notif.message)
            elif notif.type == server_pb2.TSystemNotification.SESSION_INFO_MESSAGE:
                session_info: server_pb2.TSystemNotification.SessionInfo = notif.session_info
                self._core.set_session_info(
                    session_id=session_info.session_id, 
                    role=self.match_role(session_info.role), 
                    session_players=session_info.players
                )
                self._core.print_session_info()
            elif notif.type == server_pb2.TSystemNotification.TURN_INFO_MESSAGE:
                turn_info: server_pb2.TSystemNotification.TurnInfo = notif.turn_info
                self._core.set_turn_info(
                    turn=self.match_role(turn_info.turn),
                    target=(turn_info.target_username, self.match_role(turn_info.target_role)),
                    vote_options=turn_info.vote_options
                )
                self._core.print_turn_info()
            elif notif.type == server_pb2.TSystemNotification.RESULT_MESSAGE:
                self._core.turn = 'over'
                data = dict()
                for client in notif.result.clients:
                    data[client.username] = (client.alive, self.match_role(client.role))
                self._core.print_result(notif.result.citizens_wins, data)
            await asyncio.sleep(0.1)
            print('kekekek')

    async def _new_session(self):
        response = await self._stub.WaitInQueue(server_pb2.TPingRequest(
            username=self._username
        )) 
        if response.message:
            self._core.print('new session: ' + response.message)
    
    async def _pick_request(self, vote_for: str):
        response = await self._stub.SessionMove(server_pb2.TSessionMoveRequest(
            username=self._username, 
            vote_for=vote_for,
            session_id=self._core.session_id
        ))
        self._core.print('pick: ' + response.message)
        if response.message:
            self._core.print('pick: ' + response.message)

    async def _disconnect_client(self) -> None:
        response = await self._stub.DisconnectClient(server_pb2.TPingRequest(
            username=self._username
        )) 
        if response.message:
            self._core.print('exit: ' + response.message)

    async def _run_sessions(self):
        print("RUN SESSIONS")
        if self._core.username == '':
            raise RuntimeError('client must be connected!')
        while True:
            while self._core.session_id == '' or self._core.role == '':
                await asyncio.sleep(2)
            async for cmd in self._core.run():
                print(cmd)
                if cmd['cmd'] == 'new':
                    await self._new_session()
                elif cmd['cmd'] == 'pick':
                    await self._pick_request(cmd['arg'])
                else:
                    await self._disconnect_client()
                    break
                await asyncio.sleep(1.5)

    async def stack_tasks(self):
        task_group = asyncio.gather(
            self._get_system_notifications(),
            self._run_sessions()
        )
        await task_group


async def main() -> None:
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = server_pb2_grpc.IServerStub(channel)
        client_core = ClientCore()
        client = Client(stub, client_core)
        await client.connect_client()
        await client.stack_tasks()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())
