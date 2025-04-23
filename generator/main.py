import asyncio
from kafka.consumer import consumer
from kafka.producer import producer
from handlers.prompt_handler import handle_prompt
from core.logger import logger

async def main():
    try:
        logger.info("Запуск продюсера и консьюмера...")

        await producer.start()
        await consumer.start()

        task = asyncio.create_task(consumer.consume(callback=handle_prompt))

        logger.info("Система запущена. Ожидание сообщений...")

        await task

    except Exception as e:
        logger.exception(f"Ошибка при запуске: {e}")

    finally:
        logger.info("Остановка компонентов...")
        await consumer.stop()
        await producer.stop()
        logger.info("Все компоненты остановлены.")


if __name__ == "__main__":
    asyncio.run(main())
