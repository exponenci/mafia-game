import os
import sys
import inspect

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0, parentdir + '/proto')

from typing import List, Dict, AsyncIterable

import proto.server_pb2 as core_server
import proto.server_pb2_grpc as core_server_grpc

from server.core import Core 
from server.session import Player, Session, Notification, Role


class Server(core_server_grpc.IServerServicer):
    def __init__(self) -> None:
        super().__init__()
        self.core: Core = Core()

    async def ConnectClient(self, 
                            request: core_server.TPingRequest, 
                            context):
        metadata = dict(context.invocation_metadata())
        print(metadata)
        print("AWAITING resp")
        resp = await self.core.connect_player(request.username)
        print("RECIEVED resp")
        return core_server.TPingResponse(
            message=resp['message']
        )

    async def DisconnectClient(self, 
                               request: core_server.TPingRequest, 
                               context):
        resp = await self.core.disconnect_player(request.username)
        return core_server.TPingResponse(
            message=resp['message']
        )

    @staticmethod
    def match_role(role: Role):
        if role == Role.MAFIA:
            return core_server.TSystemNotification.MAFIA_ROLE
        elif role == Role.COMMISSAR:
            return core_server.TSystemNotification.COMMISSAR_ROLE
        return core_server.TSystemNotification.CITIZEN_ROLE

    async def SubscribeForNotifications(self, 
                                        request: core_server.TPingRequest, 
                                        context):
        async for notif in self.core.core_notifications(request.username):
            if notif.type == notif.NotificationType.REGULAR:
                yield core_server.TSystemNotification(
                    type=core_server.TSystemNotification.REGULAR_MESSAGE,
                    message=notif.data['message']
                )
            elif notif.type == notif.NotificationType.SESSION_INFO:
                yield core_server.TSystemNotification(
                    type=core_server.TSystemNotification.SESSION_INFO_MESSAGE,
                    session_info=core_server.TSystemNotification.SessionInfo(
                        session_id=notif.data['session_id'],
                        role=self.match_role(notif.data['role']),
                        players=notif.data['players']
                    )
                )
            elif notif.type == notif.NotificationType.TURN_INFO:
                target_role = notif.data.get('target_role')
                if target_role is not None:
                    target_role = self.match_role(target_role)
                yield core_server.TSystemNotification(
                    type=core_server.TSystemNotification.TURN_INFO_MESSAGE,
                    turn_info=core_server.TSystemNotification.TurnInfo(
                        turn=self.match_role(notif.data['turn']),
                        vote_options=notif.data.get('vote_options'),
                        target_username=notif.data.get('target_username'),
                        target_role=target_role,
                    )
                )
    
    async def RunGame(self, 
                      request: core_server.TSessionMoveRequest, 
                      context):
        await self.core.count_vote(
            request.username,
            request.vote_for,
            request.session_id,
        )
        return core_server.TSessionMoveResponse(message="RUN GAME STEP DONE")


from concurrent import futures
from grpc import aio


async def serve():
    server = aio.server()
    core_server_grpc.add_IServerServicer_to_server(
        Server(), server
    )
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()


import asyncio
if __name__ == '__main__':
    asyncio.run(serve())
