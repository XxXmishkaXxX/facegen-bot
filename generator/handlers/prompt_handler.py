from core.logger import logger
from kafka.producer import producer



async def handle_prompt(user_id: int, prompt: str, model_name: str = "stable_diffusion"):
    try:
        logger.info(f"Получен запрос на генерацию изображения для пользователя {user_id} с запросом: {prompt}")
        
        # image = model_generator.generate_image(model_name, prompt)
        
        # await producer.send_image(user_id=user_id, image=image, request_id=request_id)
        
        logger.info(f"Изображение успешно сгенерировано и отправлено для пользователя {user_id}")

    except ValueError as e:
        logger.error(f"Ошибка при генерации изображения для пользователя {user_id}: {e}")
    except Exception as e:
        logger.exception(f"Неизвестная ошибка при обработке запроса для пользователя {user_id}: {e}")
