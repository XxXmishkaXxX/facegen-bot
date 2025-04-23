import torch
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

    def generate_image(self, prompt: str, model_name: str,
                       steps: int = 20, cfg: float = 7.0, seed: int | None = None) -> Image.Image:
        if model_name not in self.models:
            raise ValueError(f"Модель {model_name} не загружена")
        generator = torch.Generator(device=self.device).manual_seed(seed) if seed else None
        return self.models[model_name](prompt,
                                       num_inference_steps=steps,
                                       guidance_scale=cfg,
                                       generator=generator).images[0]

    def generate_base64(self, prompt: str, model_name: str, **kw) -> str:
        img = self.generate_image(prompt, model_name, **kw)
        buf = BytesIO(); img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

def get_model_manager():
    mm = ModelManager()
    mm.load_models()
    return mm

