import os
import sys
import inspect

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir + '/proto')

import asyncio
import grpc

from core import ClientCore
from grpc_stub import GrpcClientStub
from async_chat import Chat
import proto.core_pb2_grpc as core_pb2_grpc


async def main() -> None:
    grpc_host = os.getenv('GRPC_HOST', 'localhost')
    grpc_port = os.getenv('GRPC_PORT', '50051')
    
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
    rabbitmq_port = os.getenv('RABBITMQ_PORT', '5672')

    chat = Chat(rabbitmq_host, rabbitmq_port)
    client_core = ClientCore(chat=chat)

    async with grpc.aio.insecure_channel(f'{grpc_host}:{grpc_port}') as channel:
        stub = core_pb2_grpc.GameCoreStub(channel)
        client = GrpcClientStub(stub, client_core)
        await client.connect_client()
        await client.stack_tasks()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
