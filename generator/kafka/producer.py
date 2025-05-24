import json
from aiokafka import AIOKafkaProducer

from core.config import settings

class Producer:
    def __init__(self, topic: str, bootstrap_server: str):
        self.topic = topic
        self.server = bootstrap_server
        self.producer: AIOKafkaProducer | None = None

    async def start(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=self.server, max_request_size=10_000_000)
        await self.producer.start()


    async def stop(self):
        await self.producer.stop()


    async def send_image(self, user_id: int, image_string: str):

        message = {
            "user_id": user_id,
            "image_base64": image_string
        }

        await self.producer.send_and_wait(
            self.topic,
            json.dumps(message).encode("utf-8")
        )


producer = Producer(topic=settings.TOPIC_RESPONSE, 
                    bootstrap_server=settings.BOOTSTRAP_SERVERS)