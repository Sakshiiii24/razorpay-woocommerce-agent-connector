"""MCP Server & FastAPI REST API for WooCommerce Merchant Connector."""

import sys
from typing import Optional, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from mcp.server.mcpserver import MCPServer

from tools import list_orders as api_list_orders, get_order as api_get_order, search_orders as api_search_orders

# 1. Initialize MCP Server
mcp_server = MCPServer("WooCommerce Merchant Connector")


@mcp_server.tool()
async def list_orders(
    status: Optional[str] = None, page: int = 1, per_page: int = 20
) -> Dict[str, Any]:
    """List WooCommerce orders with optional status filtering and pagination.

    Args:
        status: Filter by status ('pending', 'processing', 'completed', 'cancelled', 'refunded', 'on-hold').
        page: Page number (default 1).
        per_page: Orders per page (default 20, max 100).
    """
    return await api_list_orders(status=status, page=page, per_page=per_page)


@mcp_server.tool()
async def get_order(order_id: int) -> Dict[str, Any]:
    """Retrieve details of a specific WooCommerce order by ID.

    Args:
        order_id: The integer ID of the WooCommerce order.
    """
    return await api_get_order(order_id=order_id)


@mcp_server.tool()
async def search_orders(query: str) -> Dict[str, Any]:
    """Search WooCommerce orders by customer name, email, product, SKU, or order ID.

    Args:
        query: Search string.
    """
    return await api_search_orders(query=query)


# 2. Initialize FastAPI Application
app = FastAPI(
    title="WooCommerce Merchant Connector API",
    description="Private WooCommerce Connector for Agent Studio and MCP Clients",
    version="1.0.0",
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "woocommerce-merchant-connector"}


@app.get("/tools/list_orders")
async def http_list_orders(
    status: Optional[str] = Query(None, description="Order status filter"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """HTTP endpoint to list orders."""
    res = await api_list_orders(status=status, page=page, per_page=per_page)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@app.get("/tools/get_order/{order_id}")
async def http_get_order(order_id: int):
    """HTTP endpoint to get an order by ID."""
    res = await api_get_order(order_id=order_id)
    if not res.get("success"):
        status_code = 404 if "not found" in res.get("error", "").lower() else 400
        raise HTTPException(status_code=status_code, detail=res.get("error"))
    return res


@app.get("/tools/search_orders")
async def http_search_orders(q: str = Query(..., description="Search query")):
    """HTTP endpoint to search orders."""
    res = await api_search_orders(query=q)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


def main():
    """Main CLI entry point."""
    if "--http" in sys.argv:
        import uvicorn
        print("Starting WooCommerce Connector HTTP REST Server on http://0.0.0.0:8000...")
        print("Documentation & Swagger UI available at: http://localhost:8000/docs")
        try:
            uvicorn.run(app, host="0.0.0.0", port=8000)
        except KeyboardInterrupt:
            print("\nHTTP REST Server stopped.")
    else:
        print("Starting WooCommerce Connector MCP Stdio Server...")
        print("Listening for JSON-RPC messages on stdin/stdout (Press Ctrl+C to exit)...")
        try:
            mcp_server.run()
        except KeyboardInterrupt:
            print("\nMCP Stdio Server stopped.")


if __name__ == "__main__":
    main()

