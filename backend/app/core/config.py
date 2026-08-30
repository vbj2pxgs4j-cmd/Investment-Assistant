"""Application configuration module using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import List, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base project root directory (Investment-Assistant root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    """Application settings and environment variables manager."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application & Environment
    app_name: str = Field(
        default="Mutual Fund FAQ Assistant",
        description="Name of the application",
    )
    app_version: str = Field(
        default="1.0.0",
        description="Application version",
    )
    environment: str = Field(
        default="development",
        description="Runtime environment (development, staging, production)",
    )
    debug: bool = Field(
        default=False,
        description="Debug mode toggle",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Server Network Settings
    host: str = Field(
        default="0.0.0.0",
        description="Host to bind the server",
    )
    port: int = Field(
        default=8000,
        description="Port to bind the server",
    )
    allow_origins: Union[List[str], str] = Field(
        default=["*"],
        description="Allowed CORS origins",
    )

    # Groq Inference Settings & Quota Limits (openai/gpt-oss-120b)
    groq_api_key: str = Field(
        default="",
        description="Groq API key for LPU model inference",
    )
    groq_model: str = Field(
        default="openai/gpt-oss-120b",
        description="Primary Groq model for fast factual generation",
    )
    groq_fallback_model: str = Field(
        default="openai/gpt-oss-120b",
        description="Fallback Groq model in case of rate limits or high latency",
    )
    groq_temperature: float = Field(
        default=0.0,
        description="Sampling temperature strictly set to 0.0 for deterministic facts",
    )
    groq_max_tokens: int = Field(
        default=150,
        description="Maximum tokens for factual response generation (capped to fit 8K TPM quota)",
    )
    groq_rpm_limit: int = Field(
        default=30,
        description="Maximum requests per minute for Groq model",
    )
    groq_rpd_limit: int = Field(
        default=1000,
        description="Maximum requests per day for Groq model",
    )
    groq_tpm_limit: int = Field(
        default=8000,
        description="Maximum tokens per minute for Groq model",
    )
    groq_tpd_limit: int = Field(
        default=200000,
        description="Maximum tokens per day for Groq model",
    )

    # Corpus, Vector Store & Embeddings
    data_source_path: str = Field(
        default="data/processed/schemes.json",
        description="Relative or absolute path to structured schemes JSON",
    )
    vector_store_path: str = Field(
        default="data/vector_store",
        description="Relative or absolute path to ChromaDB vector store directory",
    )
    embedding_model_name: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence-transformers embedding model name or path",
    )

    # Regulatory & Guardrail Constraints
    max_sentence_limit: int = Field(
        default=3,
        description="Strict upper limit of sentences in generated factual answer",
    )
    default_disclaimer: str = Field(
        default="Facts-only. No investment advice.",
        description="Mandatory compliance disclaimer",
    )
    whitelisted_domain: str = Field(
        default="groww.in",
        description="Authoritative domain for citation validation",
    )

    @field_validator("allow_origins", mode="before")
    @classmethod
    def parse_allow_origins(cls, value: Union[List[str], str]) -> List[str]:
        """Normalize comma-separated strings or stringified lists into a List[str]."""
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                import json
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed]
                except Exception:
                    pass
            # Comma-separated list fallback
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def absolute_data_source_path(self) -> Path:
        """Resolve absolute path to structured schemes JSON dataset."""
        path = Path(self.data_source_path)
        if path.is_absolute():
            return path
        return PROJECT_ROOT / path

    @property
    def absolute_vector_store_path(self) -> Path:
        """Resolve absolute path to vector store directory."""
        path = Path(self.vector_store_path)
        if path.is_absolute():
            return path
        return PROJECT_ROOT / path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton instance of application settings."""
    return Settings()
