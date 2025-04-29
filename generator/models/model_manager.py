import torch
torch.cuda.empty_cache()

import asyncio
from diffusers import StableDiffusionPipeline, StableDiffusion3Pipeline
from typing import Dict
from io import BytesIO
import base64
from PIL import Image

class ModelManager:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models: Dict[str, torch.nn.Module] = {}
        self.model_paths = {
            "realistic_v40": "SG161222/Realistic_Vision_V4.0",
            "sd15":          "runwayml/stable-diffusion-v1-5",
        }

    def load_models(self):
        for name, path in self.model_paths.items():
            print(f"🔄 Загрузка модели: {name} из {path}")

            # Очистка памяти перед загрузкой
            if self.device == "cuda":
                torch.cuda.empty_cache()

            if "3" in path:
                pipe = StableDiffusion3Pipeline.from_pretrained(
                    path,
                    torch_dtype=torch.float16,
                    variant="fp16",
                    low_cpu_mem_usage=True  # 🔽 уменьшение нагрузки на память
                ).to(self.device)
            else:
                pipe = StableDiffusionPipeline.from_pretrained(
                    path,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    low_cpu_mem_usage=True
                ).to(self.device)

            pipe.safety_checker = None
            self.models[name] = pipe

            # Очистка после загрузки
            if self.device == "cuda":
                torch.cuda.empty_cache()

    def generate_image(self, prompt: str, model_name: str, negative_prompt: str,
                       steps: int = 20, cfg: float = 7.0, seed: int | None = None) -> str:
        if model_name not in self.models:
            raise ValueError(f"Модель {model_name} не загружена")
        
        generator = torch.Generator(device=self.device).manual_seed(seed) if seed else None

        image = self.models[model_name](
            prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=steps,
            guidance_scale=cfg,
            generator=generator
        ).images[0]
        
        return self.conver_img_to_base64(image)
    
    async def async_generate_image(self, prompt: str, model_name: str, negative_prompt: str,
                                   steps: int = 20, cfg: float = 7.0, seed: int | None = None) -> str:
        return await asyncio.to_thread(
            self.generate_image,
            prompt,
            model_name,
            negative_prompt,
            steps,
            cfg,
            seed
        )

    def conver_img_to_base64(self, img: Image.Image) -> str:
        buf = BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

def get_model_manager():
    mm = ModelManager()
    mm.load_models()
    return mm
