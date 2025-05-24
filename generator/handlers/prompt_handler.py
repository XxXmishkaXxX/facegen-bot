from core.logger import logger
from kafka.producer import producer
from models.model_manager import get_models

fs, fg = get_models()

async def handle_prompt(user_id: int, event: str, **kwargs):
    try:
        if event == "face_swap":
            source_path = kwargs.get("source_photo")
            target_path = kwargs.get("target_photo")

            if not source_path or not target_path:
                raise ValueError("Необходимо указать source_path и target_path для face_swap")

            image_str = fs.swap_faces(source_path, target_path)
        
        elif event == "face_generate":
            prompt = kwargs.get("prompt")
            negative_prompt = kwargs.get("negative_prompt")
            image_str = await fg.async_generate_image(prompt, negative_prompt)
        
        await producer.send_image(user_id=user_id, image_string=image_str)
        
        logger.info(f"Изображение успешно сгенерировано и отправлено для пользователя {user_id}")

    except ValueError as e:
        logger.error(f"Ошибка при генерации изображения для пользователя {user_id}: {e}")
    except Exception as e:
        logger.exception(f"Неизвестная ошибка при обработке запроса для пользователя {user_id}: {e}")
