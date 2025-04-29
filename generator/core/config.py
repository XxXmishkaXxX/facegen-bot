import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    BOOTSTRAP_SERVERS: str
    TOPIC_REQUEST: str
    TOPIC_RESPONSE: str
    GROUP_ID: str
    HF_TOKEN: str
    class Config:
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')


settings = Settings()


from huggingface_hub import login
login(token=settings.HF_TOKEN)
