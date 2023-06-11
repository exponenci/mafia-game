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
from grpc import aio

from server.server import GrpcCoreServicer
import proto.core_pb2_grpc as core_server_grpc


async def serve():
    server = aio.server()
    core_server_grpc.add_GameCoreServicer_to_server(
        GrpcCoreServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(serve())
