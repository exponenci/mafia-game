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
import proto.core_pb2_grpc as core_pb2_grpc


async def main() -> None:
    grpc_host = os.getenv('GRPC_HOST', 'localhost')
    grpc_port = os.getenv('GRPC_PORT', '50051')
    async with grpc.aio.insecure_channel(f'{grpc_host}:{grpc_port}') as channel:
        stub = core_pb2_grpc.GameCoreStub(channel)
        client_core = ClientCore()
        client = GrpcClientStub(stub, client_core)
        await client.connect_client()
        await client.stack_tasks()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
