from core.logger import logger
from kafka.producer import producer
from models.model_manager import get_model_manager

mm = get_model_manager()

async def handle_prompt(user_id: int, prompt: str, model_name: str = "stable_diffusion"):
    try:
        logger.info(f"Получен запрос на генерацию изображения для пользователя {user_id} с запросом: {prompt}")
        
        image_str = mm.generate_image(prompt, model_name)
        
        await producer.send_image(user_id=user_id, image_string=image_str)
        
        logger.info(f"Изображение успешно сгенерировано и отправлено для пользователя {user_id}")

    except ValueError as e:
        logger.error(f"Ошибка при генерации изображения для пользователя {user_id}: {e}")
    except Exception as e:
        logger.exception(f"Неизвестная ошибка при обработке запроса для пользователя {user_id}: {e}")
