# pydantic v2 split BaseSettings into a separate package
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # optional strings need typing
    adt_base_url: Optional[str] = None
    adt_auth_header: Optional[str] = None
    db_url: str = "sqlite:///./data/poc.db"
    ocr_enabled: bool = True
    tesseract_cmd: Optional[str] = None
    mock_adt: bool = False
    adt_timeout: int = 5
    adt_retries: int = 1

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()