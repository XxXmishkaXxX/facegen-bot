from models.face_generator import FaceGenerator
from models.faceswaper import FaceSwapper


def get_models():
    fs= FaceSwapper()
    fs.load_models()

    fg  = FaceGenerator()
    fg.load_model()
    return fs, fg 
