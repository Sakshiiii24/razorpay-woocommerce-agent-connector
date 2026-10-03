"""Interactive Demo Script for WooCommerce Merchant Connector.

Demonstrates listing, retrieving, searching orders, and automated 429 rate-limit backoff retry behavior in DEMO_MODE.
"""

import asyncio
import json
import logging
from config import Config
from client import WooCommerceClient
from tools import OrderTools

# Setup clean console logging for demo
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f" {title.upper()} ")
    print("=" * 80)


def print_json(data: dict):
    """Print formatted JSON data."""
    print(json.dumps(data, indent=2))


async def run_demo():
    """Run full demonstration workflow."""
    print_section("1. Configuration & Initialization")
    config = Config.from_env()
    print("Loaded configuration (Masked Secrets):")
    print_json(config.get_masked_summary())

    tools = OrderTools(client=WooCommerceClient(config))

    # Demo 1: List Orders
    print_section("2. Agent Tool Call: list_orders(status='processing')")
    orders_resp = await tools.list_orders(status="processing")
    print_json(orders_resp)

    # Demo 2: Get Order by ID
    print_section("3. Agent Tool Call: get_order(order_id=1001)")
    order_resp = await tools.get_order(order_id=1001)
    print_json(order_resp)

    print_section("4. Agent Tool Call (Error Case): get_order(order_id=9999)")
    missing_order_resp = await tools.get_order(order_id=9999)
    print_json(missing_order_resp)

    # Demo 3: Search Orders
    print_section("5. Agent Tool Call: search_orders(query='Keyboard')")
    search_resp = await tools.search_orders(query="Keyboard")
    print_json(search_resp)

    # Demo 4: Rate-Limit (429) Retry Scenario Simulation
    print_section("6. Resilience Scenario: Simulated HTTP 429 Rate-Limit & Backoff Retry")
    print("Initializing client with 2 transient 429 failures before recovery...")
    resilient_client = WooCommerceClient(config)
    resilient_client.simulate_transient_failures(failure_count=2, status_code=429)
    resilient_tools = OrderTools(client=resilient_client)

    print("Agent executing list_orders(). Observe log output showing 429 backoff retries:")
    retry_demo_resp = await resilient_tools.list_orders(status="completed")
    print("\nFinal Result after automated retry recovery:")
    print_json(retry_demo_resp)

    print_section("DEMO COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_demo())
