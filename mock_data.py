"""Mock data repository for WooCommerce Demo Mode.

Provides fictional orders for testing and demonstration without real customer data.
"""

from typing import List, Dict, Any, Optional

MOCK_ORDERS: List[Dict[str, Any]] = [
    {
        "id": 1001,
        "status": "processing",
        "currency": "INR",
        "total": "4999.00",
        "total_tax": "450.00",
        "prices_include_tax": False,
        "customer_id": 42,
        "billing": {
            "first_name": "Aarav",
            "last_name": "Sharma",
            "email": "aarav.sharma@example.com",
            "phone": "+91-9876543210",
            "city": "Bengaluru",
            "state": "Karnataka",
            "country": "IN",
            "postcode": "560001"
        },
        "shipping": {
            "first_name": "Aarav",
            "last_name": "Sharma",
            "city": "Bengaluru",
            "state": "Karnataka",
            "country": "IN",
            "postcode": "560001"
        },
        "payment_method": "razorpay",
        "payment_method_title": "Razorpay UPI / Cards",
        "date_created": "2026-10-01T10:30:00",
        "date_modified": "2026-10-01T10:32:00",
        "line_items": [
            {
                "id": 101,
                "name": "Wireless Noise Cancelling Headphones",
                "product_id": 501,
                "quantity": 1,
                "price": "4999.00",
                "total": "4999.00",
                "sku": "AUDIO-WNC-01"
            }
        ],
        "customer_note": "Please leave package at front desk."
    },
    {
        "id": 1002,
        "status": "completed",
        "currency": "INR",
        "total": "1250.00",
        "total_tax": "112.50",
        "prices_include_tax": False,
        "customer_id": 89,
        "billing": {
            "first_name": "Priya",
            "last_name": "Patel",
            "email": "priya.patel@example.com",
            "phone": "+91-9876543211",
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "IN",
            "postcode": "400001"
        },
        "shipping": {
            "first_name": "Priya",
            "last_name": "Patel",
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "IN",
            "postcode": "400001"
        },
        "payment_method": "razorpay",
        "payment_method_title": "Razorpay NetBanking",
        "date_created": "2026-09-28T14:15:00",
        "date_modified": "2026-09-29T09:00:00",
        "line_items": [
            {
                "id": 102,
                "name": "Ergonomic Mechanical Keyboard",
                "product_id": 502,
                "quantity": 1,
                "price": "1250.00",
                "total": "1250.00",
                "sku": "KB-MECH-RGB"
            }
        ],
        "customer_note": ""
    },
    {
        "id": 1003,
        "status": "pending",
        "currency": "INR",
        "total": "899.00",
        "total_tax": "80.91",
        "prices_include_tax": False,
        "customer_id": 104,
        "billing": {
            "first_name": "Rohan",
            "last_name": "Verma",
            "email": "rohan.verma@example.com",
            "phone": "+91-9876543212",
            "city": "Delhi",
            "state": "Delhi",
            "country": "IN",
            "postcode": "110001"
        },
        "shipping": {
            "first_name": "Rohan",
            "last_name": "Verma",
            "city": "Delhi",
            "state": "Delhi",
            "country": "IN",
            "postcode": "110001"
        },
        "payment_method": "cod",
        "payment_method_title": "Cash on Delivery",
        "date_created": "2026-10-02T18:45:00",
        "date_modified": "2026-10-02T18:45:00",
        "line_items": [
            {
                "id": 103,
                "name": "USB-C Fast Charging Hub",
                "product_id": 503,
                "quantity": 2,
                "price": "449.50",
                "total": "899.00",
                "sku": "ACC-USBC-HUB"
            }
        ],
        "customer_note": "Call before delivery."
    },
    {
        "id": 1004,
        "status": "on-hold",
        "currency": "INR",
        "total": "15499.00",
        "total_tax": "1394.91",
        "prices_include_tax": False,
        "customer_id": 55,
        "billing": {
            "first_name": "Ananya",
            "last_name": "Iyer",
            "email": "ananya.iyer@example.com",
            "phone": "+91-9876543213",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "country": "IN",
            "postcode": "600001"
        },
        "shipping": {
            "first_name": "Ananya",
            "last_name": "Iyer",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "country": "IN",
            "postcode": "600001"
        },
        "payment_method": "bacs",
        "payment_method_title": "Direct Bank Transfer",
        "date_created": "2026-10-02T11:20:00",
        "date_modified": "2026-10-02T11:20:00",
        "line_items": [
            {
                "id": 104,
                "name": "4K Ultra HD Monitor 27-inch",
                "product_id": 504,
                "quantity": 1,
                "price": "15499.00",
                "total": "15499.00",
                "sku": "DISP-4K-27"
            }
        ],
        "customer_note": "Bank wire confirmation pending."
    },
    {
        "id": 1005,
        "status": "refunded",
        "currency": "INR",
        "total": "3200.00",
        "total_tax": "288.00",
        "prices_include_tax": False,
        "customer_id": 12,
        "billing": {
            "first_name": "Vikram",
            "last_name": "Singh",
            "email": "vikram.singh@example.com",
            "phone": "+91-9876543214",
            "city": "Jaipur",
            "state": "Rajasthan",
            "country": "IN",
            "postcode": "302001"
        },
        "shipping": {
            "first_name": "Vikram",
            "last_name": "Singh",
            "city": "Jaipur",
            "state": "Rajasthan",
            "country": "IN",
            "postcode": "302001"
        },
        "payment_method": "razorpay",
        "payment_method_title": "Razorpay Credit Card",
        "date_created": "2026-09-20T08:00:00",
        "date_modified": "2026-09-22T16:30:00",
        "line_items": [
            {
                "id": 105,
                "name": "Smart Fitness Watch",
                "product_id": 505,
                "quantity": 1,
                "price": "3200.00",
                "total": "3200.00",
                "sku": "WEAR-SMART-W1"
            }
        ],
        "customer_note": "Customer requested cancellation due to wrong size."
    },
    {
        "id": 1006,
        "status": "cancelled",
        "currency": "INR",
        "total": "650.00",
        "total_tax": "58.50",
        "prices_include_tax": False,
        "customer_id": 78,
        "billing": {
            "first_name": "Neha",
            "last_name": "Gupta",
            "email": "neha.gupta@example.com",
            "phone": "+91-9876543215",
            "city": "Hyderabad",
            "state": "Telangana",
            "country": "IN",
            "postcode": "500001"
        },
        "shipping": {
            "first_name": "Neha",
            "last_name": "Gupta",
            "city": "Hyderabad",
            "state": "Telangana",
            "country": "IN",
            "postcode": "500001"
        },
        "payment_method": "razorpay",
        "payment_method_title": "Razorpay Wallet",
        "date_created": "2026-09-15T15:10:00",
        "date_modified": "2026-09-15T15:45:00",
        "line_items": [
            {
                "id": 106,
                "name": "Vertical Gaming Mouse Pad",
                "product_id": 506,
                "quantity": 1,
                "price": "650.00",
                "total": "650.00",
                "sku": "ACC-MOUSEPAD-XL"
            }
        ],
        "customer_note": "Payment timed out."
    },
    {
        "id": 1007,
        "status": "processing",
        "currency": "INR",
        "total": "7490.00",
        "total_tax": "674.10",
        "prices_include_tax": False,
        "customer_id": 91,
        "billing": {
            "first_name": "Karan",
            "last_name": "Mehta",
            "email": "karan.mehta@example.com",
            "phone": "+91-9876543216",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "country": "IN",
            "postcode": "380001"
        },
        "shipping": {
            "first_name": "Karan",
            "last_name": "Mehta",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "country": "IN",
            "postcode": "380001"
        },
        "payment_method": "razorpay",
        "payment_method_title": "Razorpay NetBanking",
        "date_created": "2026-10-03T09:12:00",
        "date_modified": "2026-10-03T09:14:00",
        "line_items": [
            {
                "id": 107,
                "name": "Portable NVMe SSD 1TB",
                "product_id": 507,
                "quantity": 1,
                "price": "7490.00",
                "total": "7490.00",
                "sku": "STOR-NVME-1TB"
            }
        ],
        "customer_note": "Express delivery requested."
    }
]


def get_mock_orders(status: Optional[str] = None, page: int = 1, per_page: int = 20) -> List[Dict[str, Any]]:
    """Filter and paginate mock orders."""
    results = MOCK_ORDERS
    if status:
        results = [o for o in results if o.get("status", "").lower() == status.lower()]

    start = (page - 1) * per_page
    end = start + per_page
    return results[start:end]


def get_mock_order_by_id(order_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single mock order by ID."""
    for order in MOCK_ORDERS:
        if order["id"] == order_id:
            return order
    return None


def search_mock_orders(query: str) -> List[Dict[str, Any]]:
    """Search mock orders by ID, customer name, email, product name, or SKU."""
    q = query.lower().strip()
    results = []
    for order in MOCK_ORDERS:
        match = False
        # Check order ID
        if q in str(order["id"]):
            match = True
        # Check billing details
        billing = order.get("billing", {})
        if (
            q in billing.get("first_name", "").lower()
            or q in billing.get("last_name", "").lower()
            or q in billing.get("email", "").lower()
            or q in billing.get("city", "").lower()
        ):
            match = True
        # Check line items
        for item in order.get("line_items", []):
            if q in item.get("name", "").lower() or q in item.get("sku", "").lower():
                match = True

        if match:
            results.append(order)
    return results
