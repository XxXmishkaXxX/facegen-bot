import asyncio
import signal
import base64
from io import BytesIO
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InputFile

from core.config import settings
from core.logger import logger
from kafka.producer import producer
from kafka.consumer import consumer
from handlers.handlers import router 

storage = MemoryStorage()

bot = Bot(
    token=settings.TOKEN_BOT,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=storage)
dp.include_router(router)

from aiogram.types import BufferedInputFile
import base64
from io import BytesIO

async def process_message(user_id: int, img_b64: str):
    await bot.send_message(user_id, "Получаю изображение...")

    img_bytes = base64.b64decode(img_b64)
    photo = BufferedInputFile(img_bytes, filename="image.png")

    await bot.send_photo(chat_id=user_id, photo=photo)

async def start_kafka_io():
    await producer.start()
    await consumer.start()

async def stop_kafka_io():
    await producer.stop()
    await consumer.stop()

async def run():

    await start_kafka_io()
    logger.info("BOT STARTED")
    
    bot_polling_task = asyncio.create_task(dp.start_polling(bot))
    kafka_consuming_task = asyncio.create_task(consumer.consume(callback=process_message))
    
    await asyncio.gather(bot_polling_task, kafka_consuming_task)

async def shutdown():
    logger.info("Shutting down…")
    await stop_kafka_io()
    await bot.session.close()

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def runner():
        try:
            await run()
        except asyncio.CancelledError:
            pass

    try:
        loop.run_until_complete(runner())
    except KeyboardInterrupt:
        # Ctrl‑C на Windows
        loop.run_until_complete(shutdown())
    finally:
        loop.close()

if __name__ == "__main__":
    main()
