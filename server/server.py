import os
import sys
import inspect


from typing import List, Dict

import server_pb2 as core_server
import server_pb2_grpc as core_server_grpc

from core import Core 
from session import Player, Session


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

    async def GetOnlinePlayers(self, 
                               request: core_server.TPingRequest, 
                               context):
        async for notif in self.core.core_notifications(request.username):
            yield core_server.TPingResponse(
                message=notif['message']
            )

    # async def GetSessionInfo(self, request: core_server.TClient, context):
    #     player_info = self.players_in_games.get(request.clientId)
    #     session = None
    #     if player_info is not None:
    #         session = self.games[player_info.session_id].session
    #     return core_server.TSessionInfo(session=session)

    # async def StartSession(self, request: core_server.TStartSessionRequest, context):
    #     while True:
    #         session_id = await self.GenerateStringId()
    #         if session_id not in self.games:
    #             break
    #     client_id = request.client.clientId
    #     settings = request.settings
    #     if settings is None:
    #         settings = core_server.TSessionSettings(
    #             playersCount=4,
    #             mafiaPlayersCount=1
    #         )
    #     session = core_server.TSession(
    #         sessionId=session_id,
    #         status=core_server.WaitingPlayers,
    #         sessionSettings=request.settings,
    #         members=[client_id]
    #     )
    #     self.players_in_games[client_id] = Player(
    #         session_id=session_id, 
    #         client=self.clients[client_id] 
    #     )
    #     self.games[session_id] = Game(
    #         session=session,
    #         players=self.players_in_games[client_id],
    #         alive_citizens_count=settings.playersCount - settings.mafiaPlayersCount,
    #         alive_mafia_count=settings.mafiaPlayersCount,
    #     )

    #     yield core_server.TStartSessionResponse(sessionId=session_id)
    #     # TODO block on condvar till not game started, then yield message
    #     role = await self.GetRole()
    #     self.players_in_games[client_id].role = role
    #     yield core_server.TStartSessionResponse(role=role)

    # async def AddMemberToSession(self, request: core_server.TAddMemberRequest, context):
    #     client_id = request.client.clientId
    #     session_id = request.session.sessionId
    #     session = self.games[session_id].session
    #     self.players_in_games[client_id] = Player(
    #         session_id, 
    #         self.clients[client_id]
    #     )
    #     session.members.append(client_id)
    #     self.games[session_id].notifications.append("new member added with name: " + self.clients[client_id].clientName)
    #     yield core_server.TAddMemberResponse()

    #     if len(session.members) >= session.sessionSettings.playersCount:
    #         self.sessions_chats[session_id].append("ready to start game...")
    #     else:
    #         # TODO block on condvar till not game started, then yield message
    #         pass
        
    #     # TODO code duplication
    #     # TODO sync every operation via mutex or sth else
    #     role = await self.GetRole()
    #     self.players_in_games[client_id].role = role
    #     yield core_server.TStartSessionResponse(role=role)

    # async def SubscribeForNotifications(self, request: core_server.TSubscribeRequest, context):
    #     notification_id = 0
    #     session_id: str = request.session.sessionId
    #     notifications: List[str] = self.games[session_id].notifications
    #     session: core_server.TSession = self.games[session_id].session
    #     while session.status != core_server.GameOver:
    #         if len(notifications) > notification_id:
    #             yield core_server.TResponse(message=notifications[notification_id])
    #             notification_id += 1
    #         else:
    #             pass
    #             # TODO
    #             # block until new messages will be here => cond var on all waiters

    # async def SessionNextMove(self, request_iterator: List[core_server.TSessionMoveRequest], context):
    #     first_move: bool = True
    #     for move in request_iterator:
    #         if first_move:
    #             session_id = move.session.sessionId
    #             game = self.games[session_id]
    #             session = game.session
    #             notifications = game.notifications
    #             # player_count = session.sessionSettings.playersCount
    #             # mafia_count = session.sessionSettings.mafiaPlayersCount
    #             player = self.players_in_games[move.client.clientId]
    #             first_move = False

    #         if session.status == core_server.MafiaPlayerTurn and \
    #                 player.role == core_server.Mafia and player.alive and not player.voted:
    #             citizens = await game.alive_citizens_list()

    #             # send message about player's roles except commissar
    #             # vote_per_alive_player[voteFor] += 1
    #             # voted = true
    #             if ans_count == mafia_count:
    #                 # kill man
    #                 # save info about citizen's kill
    #                 # change session status
    #                 # clear all mafia's Role wrapper
    #                 pass
    #         elif session.status == core_server.CommissarPlayerTurn and \
    #                 player.role == core_server.Commissar and player.alive and not player.voted:
    #             # voted = True
    #             # return info about voteFor man
    #             # change session statue
    #             # clear commissar's Role wrapper
    #             pass
    #         elif session.status == core_server.Voting and \
    #                 player.alive and not player.voted:
    #             # vote_per_alive_player[voteFor] += 1
    #             # voted = True
    #             if ans_count == player_count:
    #                 # choose one with max votes -> remove
    #                 # notify about player
    #                 # clear all players's Role wrapper
    #                 pass



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
