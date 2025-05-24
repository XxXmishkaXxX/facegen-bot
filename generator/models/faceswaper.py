import torch
torch.cuda.empty_cache()

from typing import Optional
import numpy as np
from huggingface_hub import hf_hub_download
from insightface.app import FaceAnalysis
from insightface.model_zoo.inswapper import INSwapper
from gfpgan import GFPGANer
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet


from generator.utils.convetor import ImageConverter

class FaceSwapper:
    def __init__(self, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.face_analyzer: Optional[FaceAnalysis] = None
        self.face_swapper: Optional[INSwapper] = None
        self.gfpgan: Optional[GFPGANer] = None
        self.esrgan: Optional[RealESRGANer] = None
        self.converter = ImageConverter()

    def load_models(self):
        print("→ Инициализация детектора лиц")
        self.face_analyzer = FaceAnalysis(name='buffalo_l', providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        self.face_analyzer.prepare(ctx_id=0)

        print("→ Загрузка InSwapper")
        inswapper_path = hf_hub_download(repo_id="FaceFusion/models-3.0.0", filename="inswapper_128.onnx")
        self.face_swapper = INSwapper(inswapper_path)

        print("→ Загрузка GFPGAN")
        gfpgan_path = hf_hub_download(repo_id="th2w33knd/GFPGANv1.4", filename="GFPGANv1.4.pth")
        self.gfpgan = GFPGANer(
            model_path=gfpgan_path,
            upscale=2,
            arch="clean",
            channel_multiplier=2,
            bg_upsampler=None,
            device=self.device
        )

        print("→ Загрузка Real-ESRGAN")
        esrgan_model_path = hf_hub_download(repo_id="schwgHao/RealESRGAN_x4plus", filename="RealESRGAN_x4plus.pth")
        rrdb_model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        self.esrgan = RealESRGANer(
            scale=4,
            model_path=esrgan_model_path,
            model=rrdb_model,
            tile=128,
            tile_pad=10,
            pre_pad=0,
            half=False,
            device=self.device
        )

        print("✅ Модели для замены лиц загружены")

    def enhance_face(self, img: np.ndarray) -> np.ndarray:
        _, _, output = self.gfpgan.enhance(img, has_aligned=False, only_center_face=False, paste_back=True)
        return output

    def upscale_image(self, img: np.ndarray) -> np.ndarray:
        output, _ = self.esrgan.enhance(img, outscale=2)
        return output

    def swap_faces(self, source_base64: str, target_base64: str) -> str:
        if not self.face_swapper or not self.face_analyzer:
            raise RuntimeError("Модели для Face Swap не загружены. Вызовите load_models().")

        source_img = self.converter.base64_to_cv2_img(source_base64)
        target_img = self.converter.base64_to_cv2_img(target_base64)

        source_faces = self.face_analyzer.get(source_img)
        target_faces = self.face_analyzer.get(target_img)

        if not source_faces or not target_faces:
            raise ValueError("❌ Не удалось обнаружить лицо на одном из изображений.")

        source_face = source_faces[0]
        result_img = target_img.copy()

        for target_face in target_faces:
            result_img = self.face_swapper.get(img=result_img, target_face=target_face, source_face=source_face)

        result_img = self.enhance_face(result_img)
        result_img = self.upscale_image(result_img)

        return self.converter.cv2_to_base64(result_img)
