from pydantic_settings import BaseSettings
from typing import Dict, Any


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./research_docs.db"
    redis_url: str = "redis://localhost:6379"
    
    # AI Models
    openai_api_key: str = ""
    huggingface_token: str = ""
    
    # Web Scraping
    max_concurrent_requests: int = 5
    request_delay: float = 1.0
    user_agent: str = "Research-Analysis-System/1.0 (academic)"
    
    # File Storage
    upload_dir: str = "./uploads"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    
    # AI Model Configuration
    base_model: str = "bert-base-uncased"
    legal_model: str = "nlpaueb/legal-bert-base-uncased"
    translation_model: str = "Helsinki-NLP/opus-mt-hi-en"
    max_length: int = 512
    batch_size: int = 16
    
    # Pydantic v2 configuration
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


def get_settings() -> Settings:
    return Settings() 