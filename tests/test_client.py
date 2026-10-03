"""Tests for WooCommerce Client authentication, retry handling, and rate limits."""

import pytest
import httpx
from config import Config
from client import WooCommerceClient
from exceptions import RateLimitExceededError, WooCommerceAPIError, OrderNotFoundError


@pytest.mark.asyncio
async def test_client_auth_object(monkeypatch):
    """Test BasicAuth creation in live mode vs demo mode."""
    # Live mode
    config_live = Config(
        wc_consumer_key="ck_test",
        wc_consumer_secret="cs_test",
        wc_base_url="https://example.com/wp-json/wc/v3",
        demo_mode=False
    )
    client_live = WooCommerceClient(config_live)
    auth = client_live._get_auth()
    assert isinstance(auth, httpx.BasicAuth)

    # Demo mode
    config_demo = Config(
        wc_consumer_key="",
        wc_consumer_secret="",
        wc_base_url="https://example.com/wp-json/wc/v3",
        demo_mode=True
    )
    client_demo = WooCommerceClient(config_demo)
    assert client_demo._get_auth() is None


def test_client_url_sanitization():
    """Test sanitization of consumer keys and secrets from log URL strings."""
    config = Config(
        wc_consumer_key="ck_test",
        wc_consumer_secret="cs_test",
        wc_base_url="https://example.com/wp-json/wc/v3",
        demo_mode=True
    )
    client = WooCommerceClient(config)
    dirty_url = "https://example.com/wp-json/wc/v3/orders?consumer_key=ck_secret123&consumer_secret=cs_secret456&status=processing"
    clean = client._sanitize_url(dirty_url)

    assert "ck_secret123" not in clean
    assert "cs_secret456" not in clean
    assert "consumer_key=***MASKED***" in clean
    assert "consumer_secret=***MASKED***" in clean


@pytest.mark.asyncio
async def test_client_retry_429_recovery():
    """Test transient 429 rate-limiting recovery using retry backoff."""
    config = Config(
        wc_consumer_key="",
        wc_consumer_secret="",
        wc_base_url="https://example.com/wp-json/wc/v3",
        demo_mode=True,
        max_retries=3
    )
    client = WooCommerceClient(config)
    client.simulate_transient_failures(failure_count=2, status_code=429)

    # Should retry twice, log 429 warnings, and succeed on 3rd attempt
    orders = await client.fetch_orders()
    assert isinstance(orders, list)
    assert len(orders) > 0


@pytest.mark.asyncio
async def test_client_retry_5xx_recovery():
    """Test transient 500 server error recovery using retry backoff."""
    config = Config(
        wc_consumer_key="",
        wc_consumer_secret="",
        wc_base_url="https://example.com/wp-json/wc/v3",
        demo_mode=True,
        max_retries=3
    )
    client = WooCommerceClient(config)
    client.simulate_transient_failures(failure_count=2, status_code=503)

    orders = await client.fetch_orders()
    assert isinstance(orders, list)


@pytest.mark.asyncio
async def test_client_retry_exhaustion():
    """Test that RateLimitExceededError is raised when max retries are exhausted."""
    config = Config(
        wc_consumer_key="",
        wc_consumer_secret="",
        wc_base_url="https://example.com/wp-json/wc/v3",
        demo_mode=True,
        max_retries=2
    )
    client = WooCommerceClient(config)
    # Set failures count higher than max_retries
    client.simulate_transient_failures(failure_count=5, status_code=429)

    with pytest.raises(RateLimitExceededError):
        await client.fetch_orders()


@pytest.mark.asyncio
async def test_client_order_not_found():
    """Test OrderNotFoundError on non-existent order ID in demo mode."""
    client = WooCommerceClient()
    with pytest.raises(OrderNotFoundError):
        await client.fetch_order(order_id=999999)
