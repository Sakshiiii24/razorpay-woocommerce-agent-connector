"""Tests for agent-facing order tools (list_orders, get_order, search_orders)."""

import pytest
from tools import list_orders, get_order, search_orders, OrderTools
from client import WooCommerceClient


@pytest.mark.asyncio
async def test_list_orders_tool():
    """Test listing orders with and without status filter."""
    # List all orders
    res_all = await list_orders()
    assert res_all["success"] is True
    assert res_all["count"] >= 5
    assert len(res_all["orders"]) == res_all["count"]

    # List orders by status
    res_proc = await list_orders(status="processing")
    assert res_proc["success"] is True
    assert res_proc["status_filter"] == "processing"
    for order in res_proc["orders"]:
        assert order["status"] == "processing"


@pytest.mark.asyncio
async def test_list_orders_pagination():
    """Test pagination arguments in list_orders."""
    res_p1 = await list_orders(page=1, per_page=2)
    assert res_p1["success"] is True
    assert res_p1["page"] == 1
    assert res_p1["per_page"] == 2
    assert len(res_p1["orders"]) == 2

    res_p2 = await list_orders(page=2, per_page=2)
    assert res_p2["success"] is True
    assert res_p2["page"] == 2
    assert len(res_p2["orders"]) == 2
    assert res_p1["orders"][0]["order_id"] != res_p2["orders"][0]["order_id"]


@pytest.mark.asyncio
async def test_get_order_tool():
    """Test retrieving valid and invalid orders by ID."""
    # Valid order
    res_valid = await get_order(order_id=1001)
    assert res_valid["success"] is True
    assert res_valid["order"]["order_id"] == 1001
    assert "customer" in res_valid["order"]
    assert "items" in res_valid["order"]

    # Invalid order ID
    res_invalid = await get_order(order_id=99999)
    assert res_invalid["success"] is False
    assert "not found" in res_invalid["error"].lower()


@pytest.mark.asyncio
async def test_search_orders_tool():
    """Test searching orders by keyword."""
    # Search product
    res_product = await search_orders(query="Headphones")
    assert res_product["success"] is True
    assert res_product["count"] >= 1
    assert any("Headphones" in item["name"] for order in res_product["orders"] for item in order["items"])

    # Search customer name
    res_customer = await search_orders(query="Aarav")
    assert res_customer["success"] is True
    assert res_customer["count"] >= 1
    assert res_customer["orders"][0]["customer"]["name"] == "Aarav Sharma"


@pytest.mark.asyncio
async def test_invalid_tool_inputs():
    """Test tools error handling on invalid inputs."""
    # Invalid page number
    res_page = await list_orders(page=0)
    assert res_page["success"] is False
    assert "page" in res_page["error"].lower()

    # Invalid per_page
    res_per_page = await list_orders(per_page=150)
    assert res_per_page["success"] is False
    assert "per_page" in res_per_page["error"].lower()

    # Invalid order_id format/value
    res_order_id = await get_order(order_id=-5)
    assert res_order_id["success"] is False
    assert "positive integer" in res_order_id["error"].lower()

    # Empty search query
    res_search = await search_orders(query="   ")
    assert res_search["success"] is False
    assert "empty" in res_search["error"].lower()


@pytest.mark.asyncio
async def test_tool_handles_rate_limit():
    """Test that OrderTools gracefully formats RateLimitExceededError as clean JSON error."""
    client = WooCommerceClient()
    client.simulate_transient_failures(failure_count=5, status_code=429)
    tools = OrderTools(client=client)

    res = await tools.list_orders()
    assert res["success"] is False
    assert "rate limit exceeded" in res["error"].lower()
