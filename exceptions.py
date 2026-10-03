"""Custom exceptions for the WooCommerce Merchant Connector."""

from typing import Optional, Any


class WooCommerceError(Exception):
    """Base exception for all WooCommerce connector errors."""
    pass


class WooCommerceAPIError(WooCommerceError):
    """Raised when the WooCommerce API returns an error response."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

    def __str__(self) -> str:
        if self.status_code:
            return f"[HTTP {self.status_code}] {super().__str__()}"
        return super().__str__()


class OrderNotFoundError(WooCommerceAPIError):
    """Raised when an order with a specific ID is not found."""

    def __init__(self, order_id: int):
        super().__init__(
            message=f"Order with ID {order_id} was not found.",
            status_code=404,
            response_data={"code": "woocommerce_rest_shop_order_invalid_id", "message": "Invalid ID."}
        )
        self.order_id = order_id


class RateLimitExceededError(WooCommerceAPIError):
    """Raised when WooCommerce rate limits (429) are exceeded after retries."""

    def __init__(self, message: str = "Rate limit exceeded. Maximum retry attempts reached.", retry_after: Optional[float] = None):
        super().__init__(message=message, status_code=429)
        self.retry_after = retry_after


class WooCommerceAuthError(WooCommerceAPIError):
    """Raised when authentication with WooCommerce API fails (401 / 403)."""

    def __init__(self, message: str = "Invalid WooCommerce API credentials or unauthorized access.", status_code: int = 401):
        super().__init__(message=message, status_code=status_code)
