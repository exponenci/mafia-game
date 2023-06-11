import os
import sys
import inspect

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0, parentdir + '/proto')
sys.path.insert(0, parentdir + '/test_helpers')

import asyncio
import grpc

from core import ClientCore
from grpc_stub import GrpcClientStub
import proto.core_pb2_grpc as core_pb2_grpc


async def main() -> None:
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = core_pb2_grpc.GameCoreStub(channel)
        client_core = ClientCore()
        client = GrpcClientStub(stub, client_core)
        await client.connect_client()
        await client.stack_tasks()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
