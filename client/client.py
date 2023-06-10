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
from typing import Iterable, List, Optional, Tuple

import grpc
import proto.server_pb2 as server_pb2
import proto.server_pb2_grpc as server_pb2_grpc
from dataclasses import dataclass, field


@dataclass
class ClientCore:
    # session info for client
    username: str
    session_id: str
    role: str
    alive: bool = True
    voted: bool = False
    session_players: List[str] = field(default_factory=list) # username
    killed_players: List[Tuple[str, str]] = field(default_factory=list) # username, role

    # turn info
    turn: str = ''
    target: Optional[Tuple[str, str]] = None # username, role
    vote_options: Optional[List[str]] = None

    def print_session_info(self):
        print(f'$system> You are connected to session#{self.session_id}', flush=True)
        print(f'$system> Your role: {self.role}', flush=True)
        print(f'$system> Other players in session:', flush=True)
        for player_username in self.session_players:
            print(f'$system> - {player_username}')
    
    def set_turn_info(self, **kwargs):
        for attr, value in kwargs.items():
            print("SETTING VALUE:", attr, value)
            setattr(self, attr, value)
        if self.target is not None and self.target[0] == self.username:
            self.alive = False
        self.voted = False
        
    def print_turn_info(self):
        if self.target is not None and self.target[0] != '':
            if self.turn != 'Citizen':
                print(f'$system> {self.target[0]} was killed! He was {self.target[1]}', flush=True)
            else:
                print(f'$system> the player who was checked by commissar is {self.target[1]}')
        print(f'$system> {self.turn} turn...', flush=True)
        if self.alive and self.vote_options is not None and (self.turn == self.role or self.turn == 'Citizen'):
            print(f'$system> pick someone from options below', flush=True)
            for option in self.vote_options:
                print(f'$system> - {option}', flush=True)

    async def make_votes(self) -> Iterable[str]: # picked user
        print("OUTER MAKE VOTES...")
        while self.turn != 'over' and self.alive: # game is not over
            print("IN LOOP: ", self.turn, self.role, self.alive)
            if not self.voted and (self.turn == self.role or self.turn == 'Citizen'):
                self.voted = True
                print("MAKE VOTES...")
                while True:
                    picked = input(f'$me> ').strip()
                    if picked != self.username and picked in self.vote_options:
                        break
                yield picked
            await asyncio.sleep(1)
        print('OUT OF MAKE_VOTES')


class Client:
    def __init__(self, stub: server_pb2_grpc.IServerStub) -> None:
        self._stub: server_pb2_grpc.IServerStub = stub
        self._username: str = ''
        self._core: Optional[ClientCore] = None

    async def connect_client(self) -> None:
        print("-------------- CONNECT --------------")
        while True:
            username = input('set your username: ').strip()
            if len(username) < 3 or re.search(r"\s", username):
                print('invalid name, set another please...')
                continue
            response = await self._stub.ConnectClient(server_pb2.TPingRequest(username=username)) 
            print(response.message, flush=True)
            if not response.message.startswith('error'):
                break
        self._username = username
        print("CONNECTED")

    async def disconnect_client(self) -> None:
        print("-------------- DISCONNECT --------------")
        i = 0
        while True:
            await asyncio.sleep(1)
            i += 1
        response = await self._stub.DisconnectClient(server_pb2.TPingRequest(username=self._username)) 
        print(response.message, flush=True)
        print("--------------OUT OF DISCONNECT-------------")

    @staticmethod
    def match_role(role: server_pb2.TSystemNotification.Role):
        print(role)
        if role == server_pb2.TSystemNotification.MAFIA_ROLE:
            return 'Mafia'
        elif role == server_pb2.TSystemNotification.COMMISSAR_ROLE:
            return 'Commissar'
        return 'Citizen'

    async def _get_system_notifications(self) -> None:
        notifications = self._stub.SubscribeForNotifications(server_pb2.TPingRequest(username=self._username))
        async for notif in notifications:
            if notif.type == server_pb2.TSystemNotification.REGULAR_MESSAGE:
                if notif.message == 'GAME OVER':
                    self._core.turn = 'over'
                print(f'$system> {notif.message}', flush=True)
            elif notif.type == server_pb2.TSystemNotification.SESSION_INFO_MESSAGE:
                session_info: server_pb2.TSystemNotification.SessionInfo = notif.session_info
                self._core = ClientCore(
                    username=self._username,
                    session_id=session_info.session_id, 
                    role=self.match_role(session_info.role), 
                    session_players=session_info.players
                )
                self._core.print_session_info()
            elif notif.type == server_pb2.TSystemNotification.TURN_INFO_MESSAGE:
                turn_info: server_pb2.TSystemNotification.TurnInfo = notif.turn_info
                print("TURN INFO:")
                print(turn_info)
                self._core.set_turn_info(
                    turn=self.match_role(turn_info.turn),
                    target=(turn_info.target_username, self.match_role(turn_info.target_role)),
                    vote_options=turn_info.vote_options
                )
                self._core.print_turn_info()
                await asyncio.sleep(1.5)


    async def generate_vote_requests(self):
        print("GENERATE")
        while self._core is None:
            await asyncio.sleep(1)
        async for vote in self._core.make_votes():
            print("TARGET VOTE: ", vote)
            response = await self._stub.RunGame(server_pb2.TSessionMoveRequest(
                username=self._username, 
                vote_for=vote, 
                session_id=self._core.session_id
            ))
            await asyncio.sleep(1.5) # ???
            print(response.message)
            print(vote)
        print('OUT OF GENERATE')

    # async def _run_core(self):
    #     call = self._stub.RunGame(self.generate_vote_requests())
    #     async for response in call:
    #         print("RUN CORE: ", response.message)
    #         # yield

        # await self.disconnect_client()

    async def stack_tasks(self):
        task_group = asyncio.gather(
            self._get_system_notifications(),
            # self._run_core()
            self.generate_vote_requests()
        )
        await task_group


async def main() -> None:
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = server_pb2_grpc.IServerStub(channel)
        client = Client(stub)
        await client.connect_client()
        await client.stack_tasks()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())
