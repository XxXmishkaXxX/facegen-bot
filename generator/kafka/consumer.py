import json
from aiokafka import AIOKafkaConsumer

from generator.core.config import settings
from generator.core.logger import logger


class Consumer:
    def __init__(self, topic: str, bootstrap_server: str, group_id: str):
        self.topic = topic
        self.server = bootstrap_server
        self.group_id = group_id
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.server,
            group_id=self.group_id,
            enable_auto_commit=True,
            auto_offset_reset='latest'
        )

    async def start(self):
        await self.consumer.start()

    async def stop(self):
        await self.consumer.stop()

    async def consume(self, callback):
        try:
            async for msg in self.consumer:
                try:
                    data = json.loads(msg.value.decode("utf-8"))
                    user_id = data.get("user_id")
                    prompt = data.get("prompt")
                    model_name = data.get("model_name", "stable_diffusion")
                    
                    logger.info(f"GOT NEW MESSAGE: user:{user_id}, model={model_name}, prompt={prompt}")


                    await callback(user_id=user_id, prompt=prompt, model_name=model_name)


                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"[KafkaConsumer] Error decoding message: {e}")
        finally:
            await self.stop()


consumer = Consumer(topic=settings.TOPIC_REQUEST,
                    bootstrap_server=settings.BOOTSTRAP_SERVERS,
                    group_id=settings.GROUP_ID)