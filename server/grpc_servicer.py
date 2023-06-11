from typing import AsyncIterable

from core import Core 
from session import Role
import proto.core_pb2 as core_pb2
import proto.core_pb2_grpc as core_pb2_grpc


class GrpcCoreServicer(core_pb2_grpc.GameCoreServicer):
    def __init__(self) -> None:
        super().__init__()
        self.core: Core = Core()

    @staticmethod
    def match_role(role: Role):
        if role == Role.MAFIA:
            return core_pb2.TSystemNotification.MAFIA_ROLE
        elif role == Role.COMMISSAR:
            return core_pb2.TSystemNotification.COMMISSAR_ROLE
        return core_pb2.TSystemNotification.CITIZEN_ROLE

    async def ConnectClient(self, 
                            request: core_pb2.TPingRequest, 
                            context) -> core_pb2.TPingResponse:
        result = await self.core.connect_player(request.username)
        return core_pb2.TPingResponse(
            message=result.get('message')
        )

    async def WaitInQueue(self, 
                          request: core_pb2.TPingRequest, 
                          context) -> core_pb2.TPingResponse:
        result = await self.core.wait_in_queue(request.username)
        return core_pb2.TPingResponse(
            message=result.get('message')
        )

    async def DisconnectClient(self, 
                               request: core_pb2.TPingRequest, 
                               context) -> core_pb2.TPingResponse:
        result = await self.core.disconnect_player(request.username)
        return core_pb2.TPingResponse(
            message=result.get('message')
        )

    async def SubscribeForNotifications(self, 
                                        request: core_pb2.TPingRequest, 
                                        context) -> AsyncIterable[core_pb2.TSystemNotification]:
        async for notif in self.core.send_notifications(request.username):
            if notif.type == notif.NotificationType.REGULAR:
                yield core_pb2.TSystemNotification(
                    type=core_pb2.TSystemNotification.REGULAR_MESSAGE,
                    message=notif.data['message']
                )
            elif notif.type == notif.NotificationType.SESSION_INFO:
                yield core_pb2.TSystemNotification(
                    type=core_pb2.TSystemNotification.SESSION_INFO_MESSAGE,
                    session_info=core_pb2.TSystemNotification.SessionInfo(
                        session_id=notif.data['session_id'],
                        role=self.match_role(notif.data['role']),
                        players=notif.data['players']
                    )
                )
            elif notif.type == notif.NotificationType.TURN_INFO:
                target_role = notif.data.get('target_role')
                if target_role is not None:
                    target_role = self.match_role(target_role)
                yield core_pb2.TSystemNotification(
                    type=core_pb2.TSystemNotification.TURN_INFO_MESSAGE,
                    turn_info=core_pb2.TSystemNotification.TurnInfo(
                        turn=self.match_role(notif.data['turn']),
                        vote_options=notif.data.get('vote_options', []),
                        target_username=notif.data.get('target_username'),
                        target_role=target_role,
                    )
                )
            elif notif.type == notif.NotificationType.RESULT:
                clients = list(
                    map(
                        lambda el: core_pb2.TSystemNotification.SessionResult.Client(
                            username=el['username'],
                            alive=el['alive'],
                            role=self.match_role(el['role'])
                        ), 
                        notif.data['clients']
                    )
                )
                yield core_pb2.TSystemNotification(
                    type=core_pb2.TSystemNotification.RESULT_MESSAGE,
                    result=core_pb2.TSystemNotification.SessionResult(
                        citizens_wins=notif.data['citizens_wins'],
                        clients=clients
                    )
                )
    
    async def SessionMove(self, 
                          request: core_pb2.TSessionMoveRequest,
                          context) -> core_pb2.TSessionMoveResponse:
        result = await self.core.accept_vote(
            request.username,
            request.vote_for,
            request.session_id,
        )
        return core_pb2.TSessionMoveResponse(
            message=result.get('message')
        )
