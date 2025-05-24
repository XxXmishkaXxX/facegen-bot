import asyncio
import torch
torch.cuda.empty_cache()
from typing import Optional
from diffusers import StableDiffusion3Pipeline, StableDiffusionPipeline

from generator.utils.convetor import ImageConverter

class FaceGenerator:
    def __init__(self, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.pipe: Optional[StableDiffusionPipeline] = None
        self.converter = ImageConverter()
        self.model_path = "runwayml/stable-diffusion-v1-5"

    def load_model(self):
        print("→ Загрузка модели генерации: Stable Diffusion")
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_path,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            variant="fp16",
            low_cpu_mem_usage=True
        ).to(self.device)
        self.pipe.safety_checker = None
        print("✅ Stable Diffusion загружена")

    def generate_image(self, prompt: str, negative_prompt: str = "",
                       steps: int = 20, cfg: float = 7.0, seed: Optional[int] = None) -> str:
        if not self.pipe:
            raise RuntimeError("Модель генерации не загружена. Вызовите load_model().")

        generator = torch.Generator(device=self.device).manual_seed(seed) if seed else None

        image = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=steps,
            guidance_scale=cfg,
            generator=generator
        ).images[0]

        return self.converter.pil_to_base64(image)

    async def async_generate_image(self, prompt: str, negative_prompt: str = "",
                                   steps: int = 20, cfg: float = 7.0, seed: Optional[int] = None) -> str:
        return await asyncio.to_thread(
            self.generate_image,
            prompt,
            negative_prompt,
            steps,
            cfg,
            seed
        )