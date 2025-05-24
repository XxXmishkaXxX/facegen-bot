import base64
from io import BytesIO

import cv2
import numpy as np
from PIL import Image

class ImageConverter:
    @staticmethod
    def base64_to_cv2_img(base64_str: str) -> np.ndarray:
        img_data = base64.b64decode(base64_str)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Не удалось декодировать base64 изображение.")
        return img

    @staticmethod
    def cv2_to_base64(img: np.ndarray) -> str:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        return ImageConverter.pil_to_base64(pil_img)

    @staticmethod
    def pil_to_base64(img: Image.Image, format: str = "JPEG", quality: int = 95) -> str:
        buf = BytesIO()
        img.save(buf, format=format, quality=quality)
        return base64.b64encode(buf.getvalue()).decode()

    @staticmethod
    def base64_to_pil(base64_str: str) -> Image.Image:
        img_data = base64.b64decode(base64_str)
        return Image.open(BytesIO(img_data))
