"""Unit tests for application configuration and environment loading."""

import os
from pathlib import Path

import pytest

from backend.app.core.config import Settings, get_settings


def test_default_settings():
    """Verify default settings values match system specifications."""
    settings = Settings()

    assert settings.app_name == "Mutual Fund FAQ Assistant"
    assert settings.max_sentence_limit == 3
    assert settings.groq_temperature == 0.0
    assert settings.whitelisted_domain == "groww.in"
    assert settings.default_disclaimer == "Facts-only. No investment advice."
    assert "*" in settings.allow_origins


def test_cors_origins_parsing():
    """Verify comma-separated string origins are parsed into lists."""
    settings = Settings(allow_origins="http://localhost:3000, https://groww.in")
    assert settings.allow_origins == ["http://localhost:3000", "https://groww.in"]

    # Test JSON string parsing
    settings_json = Settings(allow_origins='["http://localhost:8000", "https://app.example.com"]')
    assert settings_json.allow_origins == ["http://localhost:8000", "https://app.example.com"]


def test_path_resolution():
    """Verify absolute path properties resolve correctly relative to project root."""
    settings = Settings(
        data_source_path="data/processed/schemes.json",
        vector_store_path="data/vector_store",
    )

    assert settings.absolute_data_source_path.name == "schemes.json"
    assert settings.absolute_vector_store_path.name == "vector_store"
    assert isinstance(settings.absolute_data_source_path, Path)
    assert isinstance(settings.absolute_vector_store_path, Path)


def test_get_settings_singleton():
    """Verify get_settings returns a cached instance."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
