import asyncio
from aio_pika import ExchangeType, DeliveryMode, Message, connect
from aio_pika.abc import AbstractIncomingMessage

from typing import Optional


class Chat:
    def __init__(self,
                 host: str,
                 port: int) -> None:
        self.host = host
        self.port = port
        self._exchange = 'chat-type'

        self._queue_id = None
        self._all_key = None
        self._receiving = False
        self._mafia_key = None

    async def connect(self):
        return await connect(f"amqp://guest:guest@{self.host}:{self.port}", timeout=2)

    def set(self, 
            queue_id: str,
            all_key: str, 
            mafia_key: Optional[str] = None):
        self._queue_id = queue_id
        self._all_key = all_key
        self._mafia_key = mafia_key
        self._receiving = True

    def reset(self):
        self._queue_id = None
        self._all_key = None
        self._mafia_key = None
        self._receiving = False
    
    async def send(self, message: str, key: Optional[str]):
        connection = await self.connect()
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                self._exchange, ExchangeType.DIRECT,
            )
            message = Message(
                message.encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
            )
            await exchange.publish(message, routing_key=key)

    async def send_mafia(self, message: str):
        await self.send(message, key=self._mafia_key)

    async def send_all(self, message: str):
        await self.send(message, key=self._all_key)

    async def stop_receiving(self):
        self._receiving = False
        if self._receiving_connection:
            await self._receiving_connection.close()

    async def receive(self, inputs: asyncio.Queue):
        while not self._receiving:
            await asyncio.sleep(1)
        while self._receiving:
            self._receiving_connection = await self.connect()
            async with self._receiving_connection:
                channel = await self._receiving_connection.channel()

                exchange = await channel.declare_exchange(
                    self._exchange, ExchangeType.DIRECT,
                )

                queue = await channel.declare_queue('', durable=True)
                await queue.bind(exchange=exchange, routing_key=self._all_key)
                await queue.bind(exchange=exchange, routing_key=self._mafia_key)
                try:
                    async with queue.iterator() as iterator:
                        message: AbstractIncomingMessage
                        async for message in iterator:
                            async with message.process():
                                await inputs.put(message.body.decode())
                except asyncio.CancelledError:
                    return
