# Limitations & Production Architectural Considerations

This document highlights the architectural boundaries, security trade-offs, and operational limitations of the **WooCommerce Merchant Connector**.

---

## 1. Read-Only Scope Enforcement
- **Design Intent**: This connector is strictly read-only.
- **Allowed Capabilities**: Listing orders, retrieving order details, and searching orders.
- **Forbidden Actions**: Creating orders, modifying status, issuing refunds, modifying pricing, or accessing store settings/customer credentials.
- **Key Enforcement**: The API client and tools only implement HTTP `GET` endpoints.

## 2. API Credentials & Permission Scopes
- **WooCommerce Key Scopes**: In a real deployment, the API credentials created in WooCommerce (`WooCommerce -> Settings -> Advanced -> REST API`) **must** be set to **Read** permission only (do not select *Read/Write* or *Write*).
- **Least Privilege**: Operating with minimal permissions ensures that even if credentials were compromised, attackers could not alter store state.

## 3. Production Secret Management
- **Environment Variables**: Local testing relies on `.env`.
- **Production Standard**: Hardcoding secrets in source control or deploying unencrypted `.env` files to production servers is dangerous.
- **Recommended Setup**: Production environments must inject secrets via dedicated secret managers such as:
  - AWS Secrets Manager / Parameter Store
  - GCP Secret Manager
  - HashiCorp Vault
  - Kubernetes Secrets (encrypted at rest)

## 4. Pagination & Query Limits
- **Page Size Limits**: WooCommerce REST API limits maximum `per_page` items to 100 per request.
- **Offset Bottlenecks**: Deep pagination (`page=1000`) on large stores (100k+ orders) can cause heavy MySQL database queries on WordPress servers.
- **Filtering**: Agents should prefer filtering by `status` or using specific `search` queries rather than requesting unbounded full store exports.

## 5. Rate Limits & Infrastructure Variation
- **Dynamic Infrastructure**: WooCommerce rate limits vary dramatically depending on hosting infrastructure:
  - Shared Hosting (e.g. Bluehost, Hostinger): Tight Nginx/PHP worker limits (often 10-20 requests/sec).
  - Managed WordPress (e.g. WP Engine, Kinsta): Cloudflare / Nginx rate limiting rules returning HTTP 429.
  - Enterprise WooCommerce: Dedicated Redis + Varnish layers.
- **Connector Handling**: The client detects `HTTP 429` and `Retry-After` headers, applying exponential backoff retry. However, persistent rate limiting requires queueing requests or throttling agent turns.

## 6. API Failures & Stale Data (Polling vs. Webhooks)
- **Polling Drawbacks**: Fetching order data on-demand via REST API introduces latency and potential race conditions if an order status changes between agent checks.
- **High-Volume Production Recommendation**: For real-time, high-volume production integrations, an **Event-Driven / Webhook Architecture** is strongly recommended:
  - WooCommerce triggers webhooks on `order.created` and `order.updated`.
  - An ingestion server receives webhooks and updates a low-latency cache / database (e.g., PostgreSQL / Redis).
  - The LLM agent queries the fast read-replica rather than directly querying WooCommerce REST endpoints on every request.

## 7. Audit Logging & Compliance
- **Audit Logging**: Production agent deployments must log every tool execution (who invoked the agent, which order was read, timestamp, and IP address) for compliance and auditing.
- **Privacy Considerations**: Customer PII (emails, phone numbers, addresses) should be sanitized or masked depending on compliance standards (GDPR, PCI-DSS, local privacy regulations).
