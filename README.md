# WooCommerce Merchant Connector

A Python connector that enables LLM agents and Agent Studio to read WooCommerce store orders securely via Model Context Protocol (MCP) or a FastAPI REST service.

---

## Overview

The WooCommerce Merchant Connector provides a clean, read-only interface for AI agents to query order history, inspect order details, and search customer purchases.

Key technical features:
- **Read-Only Scope**: Implements only HTTP `GET` endpoints to prevent accidental data modifications.
- **Resilience & Rate-Limiting**: Handles HTTP 429/5xx status codes with exponential backoff and `Retry-After` header parsing.
- **Security & Privacy**: Automatically masks API keys and credentials in application logs.
- **Offline Demo Mode**: Includes fictional mock dataset for testing without requiring live API credentials.

---

## Architecture

```
+-------------------------------------------------------+
|                 LLM Agent / Agent Studio              |
+-------------------------------------------------------+
                           |
            (MCP Stdio / HTTP REST Call)
                           v
+-------------------------------------------------------+
|                    server.py                          |
|         (MCP Server / FastAPI Application)            |
+-------------------------------------------------------+
                           |
                           v
+-------------------------------------------------------+
|                    tools.py                           |
|  [list_orders]    [get_order]    [search_orders]      |
|           (Formats clean JSON for LLM)                |
+-------------------------------------------------------+
                           |
                           v
+-------------------------------------------------------+
|                    client.py                          |
|  - WooCommerceClient (httpx AsyncClient)             |
|  - HTTP BasicAuth (Consumer Key / Secret)             |
|  - Rate-Limit 429 & 5xx Exponential Backoff           |
|  - Log Secret Sanitization                            |
+-------------------------------------------------------+
              /                         \
  (DEMO_MODE=true)                  (DEMO_MODE=false)
            /                             \
           v                               v
+-----------------------+     +-------------------------+
|     mock_data.py      |     |  WooCommerce REST API   |
| (Fictional Orders)    |     |  https://<store>/wc/v3  |
+-----------------------+     +-------------------------+
```

### Component Structure
- `config.py`: Loads environment variables, validates configuration, and masks secrets in logs.
- `client.py`: Async `httpx` HTTP client supporting BasicAuth, timeouts, error parsing, and retry logic.
- `tools.py`: Agent-facing functions (`list_orders`, `get_order`, `search_orders`) that return structured JSON.
- `server.py`: MCP stdio server and optional FastAPI HTTP REST endpoints.
- `mock_data.py`: Fictional dataset covering various WooCommerce order statuses and edge cases.
- `exceptions.py`: Custom exception hierarchy (`WooCommerceAPIError`, `OrderNotFoundError`, etc.).
- `demo.py`: Executable demonstration script showcasing tool execution and rate-limit handling.
- `tests/`: Pytest suite for unit and integration testing.

---

## Quick Setup

### Prerequisites
- Python 3.11+
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Sakshiiii24/razorpay-woocommerce-agent-connector.git
   cd razorpay-woocommerce-agent-connector
   ```

2. Create virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

---

## Environment Variables

| Variable | Type | Default | Description |
|---|---|---|---|
| `WC_CONSUMER_KEY` | String | `""` | WooCommerce REST API Consumer Key (`ck_...`) |
| `WC_CONSUMER_SECRET` | String | `""` | WooCommerce REST API Consumer Secret (`cs_...`) |
| `WC_BASE_URL` | String | `https://example.com/wp-json/wc/v3` | Store REST API base URL |
| `DEMO_MODE` | Boolean | `true` | When `true`, uses offline mock data without external API calls |
| `MAX_RETRIES` | Integer | `3` | Maximum retries for HTTP 429 and transient 5xx errors |
| `REQUEST_TIMEOUT` | Float | `10.0` | Request timeout duration in seconds |

---

## Running the Demo

To test the project without live WooCommerce credentials:

```bash
.venv/bin/python demo.py
```

The script will:
1. Print the active configuration with masked secrets.
2. Query orders by status (`processing`).
3. Fetch a specific order (`#1001`) and test error handling (`#9999`).
4. Perform search queries across orders.
5. Demonstrate simulated 429 rate-limit backoff and recovery.

---

## Running Tests

Execute the test suite:

```bash
.venv/bin/pytest -v
```

All 17 tests execute offline using mock data and do not require external network access.

---

## Connecting to a Live WooCommerce Store

To connect to a live store:

1. Log in to WordPress Admin.
2. Go to **WooCommerce > Settings > Advanced > REST API**.
3. Create a new key with **Read** permissions.
4. Update your `.env` file:
   ```env
   WC_CONSUMER_KEY=ck_your_actual_consumer_key
   WC_CONSUMER_SECRET=cs_your_actual_consumer_secret
   WC_BASE_URL=https://your-store.com/wp-json/wc/v3
   DEMO_MODE=false
   ```
5. Run the server:
   - **MCP Stdio Server**:
     ```bash
     .venv/bin/python server.py
     ```
   - **FastAPI HTTP REST Server**:
     ```bash
     .venv/bin/python server.py --http
     ```

---

## Example Tool Signatures

### `list_orders`
```python
result = await list_orders(status="processing", page=1, per_page=20)
```

### `get_order`
```python
result = await get_order(order_id=1001)
```

### `search_orders`
```python
result = await search_orders(query="Headphones")
```

---

## Capabilities and Scope

### Supported Operations
- List orders with status filtering and pagination.
- Retrieve order details by ID.
- Search orders by customer name, email, product title, SKU, or order ID.

### Restricted Operations
- Creating or updating orders.
- Modifying order status or issuing refunds.
- Accessing customer credentials, store settings, or non-order resources.

---

## Documentation

- [MCP Tool Specification](MCP_SPEC.md)
- [Limitations & Architecture Notes](LIMITATIONS.md)
