import json
from aiokafka import AIOKafkaProducer

from core.config import settings

class Producer:
    def __init__(self, topic: str, bootstrap_server: str):
        self.topic = topic
        self.server = bootstrap_server
        self.producer: AIOKafkaProducer | None = None

    async def start(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=self.server)
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def send_faceswap_request(self, user_id, source_base64, target_base64):
        message = {
            "user_id": user_id,
            "event": "face_swap",
            "source_photo": source_base64,
            "target_photo": target_base64
        }

        await self.producer.send_and_wait(
            self.topic,
            json.dumps(message).encode("utf-8")
        )


    async def send_request(self, user_id: int, prompt: str, model: str, negative_prompt: str):
        message = {
            "user_id": user_id,
            "event": "face_generate",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "model_name": model
        }

        await self.producer.send_and_wait(
            self.topic,
            json.dumps(message).encode("utf-8")
        )


producer = Producer(topic=settings.TOPIC_REQUEST, 
                    bootstrap_server=settings.BOOTSTRAP_SERVERS)