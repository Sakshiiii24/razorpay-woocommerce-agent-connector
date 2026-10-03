"""Tests for environment configuration and secret masking."""

import os
import pytest
from config import Config


def test_config_demo_mode_default(monkeypatch):
    """Test that DEMO_MODE defaults to True when credentials are not present."""
    monkeypatch.delenv("WC_CONSUMER_KEY", raising=False)
    monkeypatch.delenv("WC_CONSUMER_SECRET", raising=False)
    monkeypatch.delenv("DEMO_MODE", raising=False)

    config = Config.from_env()
    assert config.demo_mode is True


def test_config_explicit_demo_mode(monkeypatch):
    """Test explicit DEMO_MODE environment variable settings."""
    monkeypatch.setenv("DEMO_MODE", "true")
    config = Config.from_env()
    assert config.demo_mode is True

    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setenv("WC_CONSUMER_KEY", "ck_test123")
    monkeypatch.setenv("WC_CONSUMER_SECRET", "cs_test123")
    config2 = Config.from_env()
    assert config2.demo_mode is False


def test_config_missing_credentials_live_mode(monkeypatch):
    """Test that Config raises ValueError if DEMO_MODE is False but credentials are missing."""
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.delenv("WC_CONSUMER_KEY", raising=False)
    monkeypatch.delenv("WC_CONSUMER_SECRET", raising=False)

    with pytest.raises(ValueError, match="WC_CONSUMER_KEY and WC_CONSUMER_SECRET must be set"):
        Config.from_env()


def test_config_secret_masking(monkeypatch):
    """Test that get_masked_summary masks consumer secret and key."""
    monkeypatch.setenv("WC_CONSUMER_KEY", "ck_1234567890abcdef")
    monkeypatch.setenv("WC_CONSUMER_SECRET", "cs_1234567890abcdef")
    monkeypatch.setenv("DEMO_MODE", "true")

    config = Config.from_env()
    summary = config.get_masked_summary()

    assert "cs_1234567890abcdef" not in str(summary)
    assert summary["wc_consumer_secret"] == "***MASKED***"
    assert "ck_1" in summary["wc_consumer_key"]
    assert "...cdef" in summary["wc_consumer_key"]
