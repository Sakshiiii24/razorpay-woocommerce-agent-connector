# WooCommerce Merchant Connector

Production-minded Python connector enabling Agent Studio / LLM agents to read WooCommerce store orders securely via standard Model Context Protocol (MCP) or FastAPI REST services.

---

## 📌 Project Overview

The **WooCommerce Merchant Connector** exposes a clean, read-only interface for AI agents to query order history, examine order details, and search customer purchases. Built with Python 3.11+, `httpx`, `FastAPI`, `pytest`, and `mcp`, it incorporates robust rate-limiting recovery (exponential backoff on HTTP 429/5xx), credential sanitization, and a zero-dependency **Demo Mode** for instant demonstration and testing without real credentials.

---

## 🏗️ Architecture

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

### Component Breakdown
- **`config.py`**: Environment configuration loader, credentials validator, and safe secret masking.
- **`mock_data.py`**: Rich set of 8 fictional orders representing various WooCommerce statuses and edge cases.
- **`exceptions.py`**: Domain exception hierarchy (`WooCommerceAPIError`, `OrderNotFoundError`, `RateLimitExceededError`, `WooCommerceAuthError`).
- **`client.py`**: Async HTTP client supporting authentication, timeout, error parsing, URL secret masking, and exponential backoff retry.
- **`tools.py`**: Agent tool functions (`list_orders`, `get_order`, `search_orders`) producing clean JSON optimized for LLMs.
- **`server.py`**: Model Context Protocol (MCP) server & FastAPI REST API.
- **`demo.py`**: Demonstration script showcasing tool execution and simulated 429 rate-limit recovery.
- **`tests/`**: Pytest test suite providing 100% offline unit/integration coverage.

---

## ⚡ Quick Setup

### Prerequisites
- Python 3.11+
- Git

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Razorpay
   ```

2. Create virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure environment file:
   ```bash
   cp .env.example .env
   ```

---

## 🔑 Environment Variables

The application is configured using standard environment variables (or `.env` file):

| Variable | Type | Default | Description |
|---|---|---|---|
| `WC_CONSUMER_KEY` | String | `""` | WooCommerce REST API Consumer Key (`ck_...`) |
| `WC_CONSUMER_SECRET` | String | `""` | WooCommerce REST API Consumer Secret (`cs_...`) |
| `WC_BASE_URL` | String | `https://example.com/wp-json/wc/v3` | Base URL of WooCommerce store REST API |
| `DEMO_MODE` | Boolean | `true` | When `true`, uses offline mock data without external API calls |
| `MAX_RETRIES` | Integer | `3` | Maximum retry attempts for HTTP 429 and 5xx transient failures |
| `REQUEST_TIMEOUT` | Float | `10.0` | HTTP request timeout in seconds |

---

## 🚀 How to Run Demo

Run the demo script in **DEMO_MODE**:
```bash
.venv/bin/python demo.py
```

### Expected Output Highlights:
1. Displays masked configuration (secrets protected).
2. Executes `list_orders(status='processing')`.
3. Executes `get_order(1001)` and error handling for `get_order(9999)`.
4. Executes `search_orders(query='Keyboard')`.
5. Demonstrates simulated HTTP 429 rate-limit backoff retry and recovery.

---

## 🧪 How to Run Tests

Run the complete pytest test suite:
```bash
.venv/bin/pytest -v
```

*Note: Tests run completely offline in DEMO_MODE and do not require real WooCommerce credentials.*

---

## 🌐 Running Against a Real WooCommerce Store

To connect to a live WooCommerce store:

1. Log in to your WordPress Admin dashboard.
2. Navigate to **WooCommerce -> Settings -> Advanced -> REST API**.
3. Click **Add Key**.
4. Set **Description** to `Agent Studio Read-Only Connector`.
5. Set **Permissions** strictly to **Read**.
6. Click **Generate API Key**.
7. Update your `.env` file:
   ```env
   WC_CONSUMER_KEY=ck_your_actual_consumer_key
   WC_CONSUMER_SECRET=cs_your_actual_consumer_secret
   WC_BASE_URL=https://your-store.com/wp-json/wc/v3
   DEMO_MODE=false
   ```
8. Start the MCP Server:
   - **MCP Stdio Server (for Claude Desktop / Agent Studio)**:
     ```bash
     .venv/bin/python server.py
     ```
   - **FastAPI HTTP REST Server**:
     ```bash
     .venv/bin/python server.py --http
     ```

---

## 🛠️ Example Agent Tool Calls

### 1. `list_orders`
```python
# List processing orders (Page 1, 20 per page)
result = await list_orders(status="processing", page=1, per_page=20)
```

### 2. `get_order`
```python
# Retrieve order #1001 details
result = await get_order(order_id=1001)
```

### 3. `search_orders`
```python
# Search orders containing "Headphones" or customer "Aarav"
result = await search_orders(query="Headphones")
```

---

## 🛡️ Security Considerations

- **No Secret Hardcoding**: Credentials are read dynamically from environment variables.
- **Log Masking**: API keys, consumer secrets, and basic auth headers are scrubbed from log statements and URL strings.
- **Git Hygiene**: `.env` and sensitive credentials are added to `.gitignore`. `.env.example` contains only placeholder mock keys.
- **Read-Only Enforced**: API methods only execute HTTP `GET` requests.

---

## 🔄 Rate-Limit & Resilience Handling

- **HTTP 429 Detection**: Automatically identifies rate-limiting responses.
- **`Retry-After` Support**: Parses standard `Retry-After` headers (seconds or HTTP date).
- **Exponential Backoff**: Applies `base_delay * 2^(attempt-1)` when headers are missing.
- **5xx Retry**: Automatically retries transient server errors (500, 502, 503, 504).
- **Max Retries Safeguard**: Raises clean `RateLimitExceededError` if limits persist beyond configured retries.

---

## 📋 What the Agent CAN & CANNOT Do

### ✅ What the agent CAN do:
- List store orders with optional status filters and pagination.
- Retrieve detailed information for any specific order by ID.
- Search orders by customer name, email, product title, SKU, or order ID.

### ❌ What the agent CANNOT do:
- Create new orders.
- Modify existing order statuses or quantities.
- Cancel or refund orders.
- Access customer passwords, payment gateway credentials, or store settings.
- Access non-order WooCommerce resources (e.g. coupon modification, system logs).

---

## 📄 Documentation Links

- [MCP Tool Specification](file:///run/media/ridhamverma/R/Sakshi_AI/company-projects/Razorpay/MCP_SPEC.md)
- [Limitations & Architecture Notes](file:///run/media/ridhamverma/R/Sakshi_AI/company-projects/Razorpay/LIMITATIONS.md)
