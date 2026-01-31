from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict
import json

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    MAX_CONCURRENCY: int = 50
    REQUEST_TIMEOUT_SECONDS: int = 120
    MAX_REQUEST_BYTES: int = 2_000_000  # 2MB
    GATEWAY_API_KEY: Optional[str] = None
    
    OLLAMA_HOST: str = "localhost"
    OLLAMA_PORT: int = 11434

    @property
    def OLLAMA_BASE_URL(self) -> str:
        return f"http://{self.OLLAMA_HOST}:{self.OLLAMA_PORT}"

    # For pricing, we expect a JSON string in the .env file
    PRICING_JSON: str = '{}'

    @property
    def PRICING_DATA(self) -> Dict:
        try:
            return json.loads(self.PRICING_JSON)
        except json.JSONDecodeError:
            # Handle cases where the JSON is malformed
            return {}

settings = Settings()
