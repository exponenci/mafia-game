
# class Client:
#     def __init__(name):
#         # registry name
#     def get_curr_session_players():
#         # get curr session info : players
#     def append_to_session(session_id):
#         # append client to session
#     def create_session():
#         # create session
#     def vote():
#     def kill():
#     def suspect():
import grpc

# Copyright 2020 The gRPC Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python AsyncIO implementation of the gRPC route guide client."""

import asyncio
import logging
import random
from typing import Iterable, List

import grpc
import server_pb2 as server_pb2
import server_pb2_grpc as server_pb2_grpc



# async def guide_get_feature(stub: route_guide_pb2_grpc.RouteGuideStub) -> None:
#     # The following two coroutines will be wrapped in a Future object
#     # and scheduled in the event loop so that they can run concurrently
#     task_group = asyncio.gather(
#         guide_get_one_feature(
#             stub, route_guide_pb2.Point(latitude=409146138,
#                                         longitude=-746188906)),
#         guide_get_one_feature(stub,
#                               route_guide_pb2.Point(latitude=0, longitude=0)))
#     # Wait until the Future is resolved
#     await task_group


# # Performs a server-streaming call
# async def guide_list_features(
#         stub: route_guide_pb2_grpc.RouteGuideStub) -> None:
#     rectangle = route_guide_pb2.Rectangle(
#         lo=route_guide_pb2.Point(latitude=400000000, longitude=-750000000),
#         hi=route_guide_pb2.Point(latitude=420000000, longitude=-730000000))
#     print("Looking for features between 40, -75 and 42, -73")

#     features = stub.ListFeatures(rectangle)

#     async for feature in features:
#         print(f"Feature called {feature.name} at {feature.location}")

async def connect_client(stub: server_pb2_grpc.IServerStub, username: str) -> None:
    print("-------------- CONNECT --------------")
    response = await stub.ConnectClient(server_pb2.TPingRequest(username=username)) 
    print(response.message, flush=True)

import time
import asyncio

async def disconnect_client(stub: server_pb2_grpc.IServerStub, username: str) -> None:
    print("-------------- DISCONNECT --------------")
    i = 0
    while i < 10:
        await asyncio.sleep(1)
        i += 1
    response = await stub.DisconnectClient(server_pb2.TPingRequest(username=username)) 
    print(response.message, flush=True)
    print("--------------OUT OF DISCONNECT-------------")

async def get_online_players(stub: server_pb2_grpc.IServerStub, username: str) -> None:
    print("-------------- GET NOTIFICATIONS --------------")
    async for notif in stub.GetOnlinePlayers(server_pb2.TPingRequest(username=username)):
        if notif:
            print('system notif: ', notif.message, flush=True)

async def run(stub: server_pb2_grpc.IServerStub, username: str):
    task_group = asyncio.gather(
        get_online_players(stub, username),
        disconnect_client(stub, username) # нужно научиться отключать таску
    )
    await task_group


async def main() -> None:
    username = input('set username: ')
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = server_pb2_grpc.IServerStub(channel)
        await connect_client(stub, username)
        await run(stub, username)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.get_event_loop().run_until_complete(main())
