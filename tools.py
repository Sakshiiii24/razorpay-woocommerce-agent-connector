"""Agent-facing tools for WooCommerce order management.

Provides clean, structured JSON outputs optimized for LLM consumption.
"""

from typing import Any, Dict, List, Optional
from client import WooCommerceClient
from exceptions import WooCommerceAPIError, OrderNotFoundError, RateLimitExceededError


def clean_order_for_llm(order: Dict[str, Any]) -> Dict[str, Any]:
    """Format raw WooCommerce order JSON into a clean, concise representation for LLMs."""
    billing = order.get("billing", {})
    customer_name = f"{billing.get('first_name', '')} {billing.get('last_name', '')}".strip() or "Guest"

    items = []
    for item in order.get("line_items", []):
        items.append({
            "product_id": item.get("product_id"),
            "name": item.get("name"),
            "quantity": item.get("quantity"),
            "unit_price": item.get("price"),
            "line_total": item.get("total"),
            "sku": item.get("sku", "")
        })

    return {
        "order_id": order.get("id"),
        "status": order.get("status"),
        "currency": order.get("currency"),
        "total": order.get("total"),
        "total_tax": order.get("total_tax"),
        "date_created": order.get("date_created"),
        "payment_method": order.get("payment_method_title") or order.get("payment_method"),
        "customer": {
            "customer_id": order.get("customer_id"),
            "name": customer_name,
            "email": billing.get("email"),
            "phone": billing.get("phone"),
            "city": billing.get("city"),
            "state": billing.get("state"),
            "country": billing.get("country"),
        },
        "items": items,
        "customer_note": order.get("customer_note", "")
    }


class OrderTools:
    """Class containing agent-facing tools bound to a WooCommerceClient instance."""

    def __init__(self, client: Optional[WooCommerceClient] = None):
        self.client = client or WooCommerceClient()

    async def list_orders(
        self, status: Optional[str] = None, page: int = 1, per_page: int = 20
    ) -> Dict[str, Any]:
        """List WooCommerce orders with optional status filter and pagination.

        Args:
            status: Filter orders by status (e.g. 'pending', 'processing', 'completed', 'cancelled', 'refunded', 'on-hold').
            page: Page number for pagination (default: 1).
            per_page: Number of items per page (default: 20, max: 100).

        Returns:
            Dict containing status, metadata, and list of formatted orders.
        """
        if page < 1:
            return {"success": False, "error": "Parameter 'page' must be greater than or equal to 1."}
        if per_page < 1 or per_page > 100:
            return {"success": False, "error": "Parameter 'per_page' must be between 1 and 100."}

        try:
            raw_orders = await self.client.fetch_orders(status=status, page=page, per_page=per_page)
            cleaned = [clean_order_for_llm(o) for o in raw_orders]
            return {
                "success": True,
                "count": len(cleaned),
                "page": page,
                "per_page": per_page,
                "status_filter": status,
                "orders": cleaned
            }
        except RateLimitExceededError as e:
            return {"success": False, "error": f"Rate limit exceeded: {str(e)}"}
        except WooCommerceAPIError as e:
            return {"success": False, "error": f"WooCommerce API error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to list orders: {str(e)}"}

    async def get_order(self, order_id: int) -> Dict[str, Any]:
        """Retrieve details of a specific WooCommerce order by order ID.

        Args:
            order_id: The integer ID of the WooCommerce order to retrieve.

        Returns:
            Dict containing status and order details.
        """
        if not isinstance(order_id, int) or order_id <= 0:
            return {"success": False, "error": "Parameter 'order_id' must be a positive integer."}

        try:
            raw_order = await self.client.fetch_order(order_id=order_id)
            return {
                "success": True,
                "order": clean_order_for_llm(raw_order)
            }
        except OrderNotFoundError:
            return {"success": False, "error": f"Order #{order_id} not found."}
        except RateLimitExceededError as e:
            return {"success": False, "error": f"Rate limit exceeded: {str(e)}"}
        except WooCommerceAPIError as e:
            return {"success": False, "error": f"WooCommerce API error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to retrieve order #{order_id}: {str(e)}"}

    async def search_orders(self, query: str) -> Dict[str, Any]:
        """Search WooCommerce orders by query string (customer name, email, product, or order ID).

        Args:
            query: Search query string.

        Returns:
            Dict containing status, search query, match count, and matching orders.
        """
        if not query or not query.strip():
            return {"success": False, "error": "Parameter 'query' cannot be empty."}

        try:
            raw_orders = await self.client.search_orders(query=query.strip())
            cleaned = [clean_order_for_llm(o) for o in raw_orders]
            return {
                "success": True,
                "query": query.strip(),
                "count": len(cleaned),
                "orders": cleaned
            }
        except RateLimitExceededError as e:
            return {"success": False, "error": f"Rate limit exceeded: {str(e)}"}
        except WooCommerceAPIError as e:
            return {"success": False, "error": f"WooCommerce API error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to search orders: {str(e)}"}


# Default global tool instances for direct import
_default_tools = OrderTools()


async def list_orders(status: Optional[str] = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    """Agent tool: List WooCommerce orders."""
    return await _default_tools.list_orders(status=status, page=page, per_page=per_page)


async def get_order(order_id: int) -> Dict[str, Any]:
    """Agent tool: Get WooCommerce order by ID."""
    return await _default_tools.get_order(order_id=order_id)


async def search_orders(query: str) -> Dict[str, Any]:
    """Agent tool: Search WooCommerce orders."""
    return await _default_tools.search_orders(query=query)
