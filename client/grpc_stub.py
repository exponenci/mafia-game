import os
import asyncio

from core import ClientCore
import proto.core_pb2 as core_pb2
import proto.core_pb2_grpc as core_pb2_grpc


class GrpcClientStub:
    def __init__(self, stub: core_pb2_grpc.GameCoreStub, core: ClientCore) -> None:
        self._stub: core_pb2_grpc.GameCoreStub = stub
        self._username: str = ''
        self._core: ClientCore = core

    @staticmethod
    def match_role(role: core_pb2.TSystemNotification.Role):
        if role == core_pb2.TSystemNotification.MAFIA_ROLE:
            return 'Mafia'
        elif role == core_pb2.TSystemNotification.COMMISSAR_ROLE:
            return 'Commissar'
        return 'Citizen'

    async def connect_client(self) -> None:
        while True:
            self._core.print('Set your username below')
            username = input()
            self._core.print(username, prefix='unauth') # to show the input in output
            if len(username) < 3 or not username.isalnum():
                self._core.print('Set name with 3 and more alnum symbols')
                continue
            response = await self._stub.ConnectClient(core_pb2.TPingRequest(
                username=username
            )) 
            if not response.message:
                self._core.print(f'Welcome, {username}!')
                break
            self._core.print(response.message)
        self._core.username = username
        self._username = username

    async def _get_system_notifications(self) -> None:
        notifications = self._stub.SubscribeForNotifications(core_pb2.TPingRequest(
            username=self._username
        ))
        async for notif in notifications:
            if notif.type == core_pb2.TSystemNotification.REGULAR_MESSAGE:
                self._core.print(notif.message)
                # # uncomment block if want clear output for each core-notification - no need in auto-test case
                # if self._core.session_id == '':
                #     await asyncio.sleep(0.5) # set 0.5 for auto-test case, increase if want to read messages 
                #     os.system('clear')
            elif notif.type == core_pb2.TSystemNotification.SESSION_INFO_MESSAGE:
                session_info: core_pb2.TSystemNotification.SessionInfo = notif.session_info
                self._core.set_session_info(
                    session_id=session_info.session_id, 
                    role=self.match_role(session_info.role), 
                    session_players=session_info.players,
                    all_key=session_info.all_key,
                    mafia_key=session_info.mafia_key
                )
                self._core.print_session_info()
            elif notif.type == core_pb2.TSystemNotification.TURN_INFO_MESSAGE:
                turn_info: core_pb2.TSystemNotification.TurnInfo = notif.turn_info
                self._core.set_turn_info(
                    turn=self.match_role(turn_info.turn),
                    target=(turn_info.target_username, self.match_role(turn_info.target_role)),
                    vote_options=turn_info.vote_options
                )
                self._core.print_turn_info()
            elif notif.type == core_pb2.TSystemNotification.RESULT_MESSAGE:
                self._core.turn = 'over'
                data = dict()
                for client in notif.result.clients:
                    data[client.username] = (client.alive, self.match_role(client.role))
                self._core.print_result(notif.result.citizens_wins, data)
            await asyncio.sleep(1)

    async def _new_session(self):
        response = await self._stub.WaitInQueue(core_pb2.TPingRequest(
            username=self._username
        )) 
        if response.message:
            self._core.print('new session: ' + response.message)
    
    async def _pick_request(self, vote_for: str):
        response = await self._stub.SessionMove(core_pb2.TSessionMoveRequest(
            username=self._username, 
            vote_for=vote_for,
            session_id=self._core.session_id
        ))
        if response.message:
            self._core.print('pick: ' + response.message)

    async def _disconnect_client(self) -> None:
        response = await self._stub.DisconnectClient(core_pb2.TPingRequest(
            username=self._username
        )) 
        if response.message:
            self._core.print('exit: ' + response.message)
            return
        self._core.reset()
        self._core.print('See you soon!')

    async def _run_sessions(self, events: asyncio.Queue):
        if self._core.username == '':
            raise RuntimeError('client must be connected!')
        witsh_to_exit = False
        while not witsh_to_exit:
            while self._core.turn == '':
                await asyncio.sleep(1)
            event = await events.get()
            if event['cmd'] == '!new':
                await self._new_session()
            elif event['cmd'] == '!pick':
                await self._pick_request(event['arg'])
            else:
                witsh_to_exit = True
                await self._disconnect_client()
                break
            events.task_done()

    async def stack_tasks(self):
        events = asyncio.Queue(maxsize=10)
        inputs = asyncio.Queue(maxsize=10)
        self._core.chat_receive_task = asyncio.create_task(self._core.chat.receive(inputs))
        task_group = asyncio.gather(
            self._get_system_notifications(),
            self._run_sessions(events), # read from events
            self._core.chat_receive_task, # write in inputs
            self._core.run(events, inputs) # write in events, read from inputs
        )
        await task_group
