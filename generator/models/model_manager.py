import torch
import asyncio
from diffusers import StableDiffusionPipeline
from typing import Dict
from io import BytesIO
import base64
from PIL import Image

class ModelManager:
    def __init__(self):
        self.device = "cpu"
        self.models: Dict[str, StableDiffusionPipeline] = {}
        self.model_paths = {
            "sd15":          "runwayml/stable-diffusion-v1-5",
            "realistic_v40": "SG161222/Realistic_Vision_V4.0",
        }

    def load_models(self):
        for name, path in self.model_paths.items():
            print(f"Loading {name}")
            pipe = StableDiffusionPipeline.from_pretrained(
                path,
                torch_dtype=torch.float32
            ).to(self.device)
            pipe.safety_checker = None
            self.models[name] = pipe

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
        
        img_str = self.conver_img_to_base64(image)

        return img_str
    
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

