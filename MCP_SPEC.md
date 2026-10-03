# Model Context Protocol (MCP) Tool Specification

This document details the MCP tool definitions exposed by the **WooCommerce Merchant Connector** for Agent Studio and LLM Agents.

---

## Tool 1: `list_orders`

### Description
Lists WooCommerce orders from the store with optional status filtering and pagination support.

### Input Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "description": "Optional filter by order status",
      "enum": ["pending", "processing", "on-hold", "completed", "cancelled", "refunded", "failed", "trash"]
    },
    "page": {
      "type": "integer",
      "default": 1,
      "minimum": 1,
      "description": "Page number for pagination"
    },
    "per_page": {
      "type": "integer",
      "default": 20,
      "minimum": 1,
      "maximum": 100,
      "description": "Number of orders returned per page"
    }
  },
  "required": []
}
```

### Output Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "count": { "type": "integer" },
    "page": { "type": "integer" },
    "per_page": { "type": "integer" },
    "status_filter": { "type": ["string", "null"] },
    "orders": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "order_id": { "type": "integer" },
          "status": { "type": "string" },
          "currency": { "type": "string" },
          "total": { "type": "string" },
          "total_tax": { "type": "string" },
          "date_created": { "type": "string" },
          "payment_method": { "type": "string" },
          "customer": {
            "type": "object",
            "properties": {
              "customer_id": { "type": "integer" },
              "name": { "type": "string" },
              "email": { "type": "string" },
              "phone": { "type": "string" },
              "city": { "type": "string" },
              "state": { "type": "string" },
              "country": { "type": "string" }
            }
          },
          "items": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "product_id": { "type": "integer" },
                "name": { "type": "string" },
                "quantity": { "type": "integer" },
                "unit_price": { "type": "string" },
                "line_total": { "type": "string" },
                "sku": { "type": "string" }
              }
            }
          },
          "customer_note": { "type": "string" }
        }
      }
    }
  },
  "required": ["success", "count", "orders"]
}
```

---

## Tool 2: `get_order`

### Description
Retrieves details for a single WooCommerce order specified by its integer order ID.

### Input Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "order_id": {
      "type": "integer",
      "minimum": 1,
      "description": "The unique integer ID of the WooCommerce order"
    }
  },
  "required": ["order_id"]
}
```

### Output Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "order": {
      "type": "object",
      "properties": {
        "order_id": { "type": "integer" },
        "status": { "type": "string" },
        "currency": { "type": "string" },
        "total": { "type": "string" },
        "total_tax": { "type": "string" },
        "date_created": { "type": "string" },
        "payment_method": { "type": "string" },
        "customer": { "type": "object" },
        "items": { "type": "array" },
        "customer_note": { "type": "string" }
      }
    },
    "error": { "type": "string" }
  },
  "required": ["success"]
}
```

---

## Tool 3: `search_orders`

### Description
Searches WooCommerce orders by matching customer names, billing emails, product names, SKUs, or order IDs against a search query.

### Input Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "minLength": 1,
      "description": "Keyword search query"
    }
  },
  "required": ["query"]
}
```

### Output Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "query": { "type": "string" },
    "count": { "type": "integer" },
    "orders": { "type": "array" },
    "error": { "type": "string" }
  },
  "required": ["success", "query", "count", "orders"]
}
```

---

## Errors & Safety Limitations

### Error Format
All tool responses follow a standardized JSON envelope:
```json
{
  "success": false,
  "error": "Human readable error description"
}
```

### Common Error Categories
1. **Invalid Parameters**: Passed when arguments fail schema or range validations (e.g., negative page numbers).
2. **Order Not Found**: Returned when an order ID does not exist (`HTTP 404`).
3. **Authentication Failure**: Returned when API key/secret authentication fails (`HTTP 401/403`).
4. **Rate Limit Exceeded**: Returned after maximum backoff retries fail due to severe upstream rate limits (`HTTP 429`).
5. **Upstream Server Error**: Returned when WooCommerce API experiences unrecoverable 5xx failures.

### Safety Limitations & Read-Only Scope
- **Strict Read-Only Access**: No tools exist for creating, updating, canceling, or deleting orders.
- **No Credential Exposure**: Consumer secrets, passwords, or authentication keys are masked in all logs and outputs.
- **Data Scrubbing**: Unnecessary internal database metadata is omitted to keep LLM context light and secure.
