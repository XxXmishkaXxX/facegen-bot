import json
from aiokafka import AIOKafkaConsumer

from core.config import settings
from core.logger import logger


class Consumer:
    def __init__(self, topic: str, bootstrap_server: str, group_id: str):
        self.topic = topic
        self.server = bootstrap_server
        self.group_id = group_id
        self.consumer: AIOKafkaConsumer | None = None   # пока None

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.server,
            group_id=self.group_id,
            enable_auto_commit=True,
            auto_offset_reset="latest",
        )
        await self.consumer.start()

    async def stop(self):
        await self.consumer.stop()

    async def consume(self, callback):
        try:
            async for msg in self.consumer:
                try:
                    logger.info("GOT NEW IMAGE")
                    payload = json.loads(msg.value.decode())
                    user_id = payload["user_id"]
                    img_b64 = payload["image_base64"]

                    await callback(user_id=user_id, img_b64=img_b64)

                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"[KafkaConsumer] Error decoding message: {e}")
        finally:
            await self.stop()


consumer = Consumer(topic=settings.TOPIC_RESPONSE,
                    bootstrap_server=settings.BOOTSTRAP_SERVERS,
                    group_id=settings.GROUP_ID)