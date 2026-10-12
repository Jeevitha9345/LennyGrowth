import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # App Settings
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    log_level: str = "INFO"
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # AI Model Providers ("ollama" | "openai" | "anthropic" | "mock")
    active_provider: str = "mock"

    # Ollama
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5:0.5b"
    ollama_timeout_seconds: float = 15.0

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: float = 20.0

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-haiku-latest"
    anthropic_timeout_seconds: float = 20.0

    # Generation Constraints (Strict ~1GB RAM profile)
    max_response_tokens: int = 1024
    temperature: float = 0.3
    top_k_chunks: int = 4
    max_context_char_limit: int = 4000
    min_relevance_score: float = 0.12

    # Database
    database_url: str = ""
    sqlite_fallback_path: str = str(BASE_DIR / "data" / "lenny_growth.db")

    # Knowledge Base
    transcripts_dir: str = str(BASE_DIR / "data" / "transcripts")
    chunks_cache_file: str = str(BASE_DIR / "data" / "processed" / "chunks_cache.json")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
