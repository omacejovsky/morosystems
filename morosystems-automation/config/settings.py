import os
from dataclasses import dataclass

@dataclass
class Settings:
    google_url: str = os.getenv("GOOGLE_URL", "https://www.google.com/?hl=cs")
    morosystems_url: str = os.getenv("MOROSYSTEMS_URL", "https://www.morosystems.cz")
    todo_api_url: str = os.getenv("TODO_API_URL", "http://localhost:8080")
    api_timeout_ms: float = float(os.getenv("API_TIMEOUT_MS", "10000"))

settings = Settings()
