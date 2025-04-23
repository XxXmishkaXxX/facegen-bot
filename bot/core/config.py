import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TOKEN_BOT: str
    BOOTSTRAP_SERVERS: str
    TOPIC_REQUEST: str
    TOPIC_RESPONSE: str
    GROUP_ID: str

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')


settings = Settings()
