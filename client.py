"""WooCommerce HTTP Client with authentication, rate-limiting retry logic, and demo mode support."""

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional, Union
from email.utils import parsedate_to_datetime

import httpx

from config import Config
from exceptions import (
    WooCommerceAPIError,
    WooCommerceAuthError,
    OrderNotFoundError,
    RateLimitExceededError,
)
from mock_data import get_mock_orders, get_mock_order_by_id, search_mock_orders

logger = logging.getLogger("woocommerce_client")
logger.setLevel(logging.INFO)


class WooCommerceClient:
    """Async client for interacting with WooCommerce REST API v3."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.from_env()
        self._simulate_failures_count: int = 0
        self._simulate_failure_status: int = 429

    def _get_auth(self) -> Optional[httpx.BasicAuth]:
        """Return BasicAuth object for WooCommerce REST API."""
        if self.config.demo_mode or not self.config.wc_consumer_key:
            return None
        return httpx.BasicAuth(
            username=self.config.wc_consumer_key,
            password=self.config.wc_consumer_secret,
        )

    def _sanitize_url(self, url: str) -> str:
        """Remove sensitive credentials or tokens from URL strings for safe logging."""
        sanitized = re.sub(r"(consumer_key=)[^&]+", r"\1***MASKED***", url)
        sanitized = re.sub(r"(consumer_secret=)[^&]+", r"\1***MASKED***", sanitized)
        return sanitized

    def _parse_retry_after(self, response: httpx.Response, default_delay: float) -> float:
        """Parse Retry-After header if present, returning backoff delay in seconds."""
        header_val = response.headers.get("Retry-After")
        if not header_val:
            return default_delay

        try:
            return max(0.1, float(header_val))
        except ValueError:
            try:
                dt = parsedate_to_datetime(header_val)
                now = parsedate_to_datetime(response.headers.get("Date", ""))
                delay = (dt - now).total_seconds()
                return max(0.1, delay)
            except Exception:
                return default_delay

    def simulate_transient_failures(self, failure_count: int = 2, status_code: int = 429):
        """Simulate transient HTTP 429 or 5xx failures for demonstration and testing purposes."""
        self._simulate_failures_count = failure_count
        self._simulate_failure_status = status_code

    async def _make_request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Execute HTTP request with authentication, retries, and rate limit handling."""
        endpoint = endpoint.lstrip("/")
        full_url = f"{self.config.wc_base_url}/{endpoint}"
        sanitized_url = self._sanitize_url(full_url)

        attempt = 0
        while attempt <= self.config.max_retries:
            attempt += 1

            # Handle Demo Mode simulation & execution
            if self.config.demo_mode:
                if self._simulate_failures_count > 0:
                    self._simulate_failures_count -= 1
                    status = self._simulate_failure_status
                    log_type = "Rate limit (429)" if status == 429 else f"Server error ({status})"
                    
                    if attempt <= self.config.max_retries:
                        delay = 0.05 * (2 ** (attempt - 1))
                        logger.warning(
                            "[DEMO SIMULATION] %s encountered on %s. Retrying in %.2fs (Attempt %d/%d)",
                            log_type, sanitized_url, delay, attempt, self.config.max_retries
                        )
                        await asyncio.sleep(delay)
                        continue
                    
                    if status == 429:
                        raise RateLimitExceededError("Simulated rate limit exceeded after retries.")
                    raise WooCommerceAPIError(f"Simulated server error ({status})", status_code=status)

                return await self._handle_demo_request(endpoint, params)

            # Live API Execution
            auth = self._get_auth()
            logger.info("Executing %s %s (Attempt %d/%d)", method, sanitized_url, attempt, self.config.max_retries + 1)

            try:
                async with httpx.AsyncClient(timeout=self.config.request_timeout) as client:
                    response = await client.request(
                        method=method,
                        url=full_url,
                        auth=auth,
                        params=params,
                        headers={"Accept": "application/json", "User-Agent": "WooCommerce-Merchant-Connector/1.0"},
                    )

                if response.status_code in (200, 201):
                    return response.json()

                if response.status_code in (401, 403):
                    raise WooCommerceAuthError(
                        message=f"Authentication failed for WooCommerce API at {sanitized_url}",
                        status_code=response.status_code,
                    )

                if response.status_code == 404:
                    if "orders/" in endpoint:
                        try:
                            order_id = int(endpoint.split("orders/")[-1])
                            raise OrderNotFoundError(order_id)
                        except ValueError:
                            pass
                    raise WooCommerceAPIError(
                        message=f"Resource not found at {sanitized_url}",
                        status_code=404,
                        response_data=response.text,
                    )

                is_429 = response.status_code == 429
                is_5xx = 500 <= response.status_code < 600

                if (is_429 or is_5xx) and attempt <= self.config.max_retries:
                    base_delay = 1.0 * (2 ** (attempt - 1))
                    delay = self._parse_retry_after(response, base_delay)
                    log_msg = "Rate limit (429)" if is_429 else f"Server error ({response.status_code})"
                    logger.warning("%s encountered on %s. Retrying in %.2fs (Attempt %d/%d)",
                                   log_msg, sanitized_url, delay, attempt, self.config.max_retries)
                    await asyncio.sleep(delay)
                    continue

                if is_429:
                    raise RateLimitExceededError(
                        message=f"Rate limit exceeded after {self.config.max_retries} retries."
                    )

                raise WooCommerceAPIError(
                    message=f"WooCommerce API error: {response.status_code}",
                    status_code=response.status_code,
                    response_data=response.text,
                )

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                if attempt <= self.config.max_retries:
                    delay = 1.0 * (2 ** (attempt - 1))
                    logger.warning("Network/Timeout error on %s: %s. Retrying in %.2fs", sanitized_url, str(e), delay)
                    await asyncio.sleep(delay)
                    continue
                raise WooCommerceAPIError(f"Network request failed after retries: {str(e)}")

        raise WooCommerceAPIError(f"Failed to execute request to {sanitized_url} after retries.")

    async def _handle_demo_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Process requests locally using mock data in DEMO_MODE."""
        params = params or {}

        if endpoint == "orders" or endpoint == "orders/":
            search_query = params.get("search")
            if search_query:
                return search_mock_orders(search_query)

            status = params.get("status")
            page = int(params.get("page", 1))
            per_page = int(params.get("per_page", 20))
            return get_mock_orders(status=status, page=page, per_page=per_page)

        if endpoint.startswith("orders/"):
            try:
                order_id = int(endpoint.split("orders/")[-1])
                order = get_mock_order_by_id(order_id)
                if not order:
                    raise OrderNotFoundError(order_id)
                return order
            except ValueError:
                raise WooCommerceAPIError("Invalid order ID format.", status_code=400)

        raise WooCommerceAPIError(f"Demo endpoint not implemented for: {endpoint}", status_code=404)

    async def fetch_orders(
        self, status: Optional[str] = None, page: int = 1, per_page: int = 20
    ) -> List[Dict[str, Any]]:
        """Fetch list of WooCommerce orders."""
        params: Dict[str, Any] = {"page": page, "per_page": per_page}
        if status:
            params["status"] = status
        res = await self._make_request("GET", "orders", params=params)
        return res if isinstance(res, list) else [res]

    async def fetch_order(self, order_id: int) -> Dict[str, Any]:
        """Fetch a specific WooCommerce order by ID."""
        res = await self._make_request("GET", f"orders/{order_id}")
        if isinstance(res, dict):
            return res
        raise WooCommerceAPIError("Unexpected API response format for order detail.", status_code=500)

    async def search_orders(self, query: str) -> List[Dict[str, Any]]:
        """Search WooCommerce orders by query keyword."""
        res = await self._make_request("GET", "orders", params={"search": query})
        return res if isinstance(res, list) else [res]
