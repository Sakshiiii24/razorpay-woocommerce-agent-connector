"""Configuration management for the WooCommerce Merchant Connector."""

import os
from dataclasses import dataclass
from typing import Dict
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


@dataclass
class Config:
    wc_consumer_key: str
    wc_consumer_secret: str
    wc_base_url: str
    demo_mode: bool
    max_retries: int = 3
    request_timeout: float = 10.0

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        raw_demo = os.getenv("DEMO_MODE", "").strip().lower()
        
        consumer_key = os.getenv("WC_CONSUMER_KEY", "").strip()
        consumer_secret = os.getenv("WC_CONSUMER_SECRET", "").strip()
        base_url = os.getenv("WC_BASE_URL", "https://example.com/wp-json/wc/v3").strip().rstrip("/")

        # Auto-enable demo mode if credentials are missing
        if raw_demo in ("true", "1", "yes"):
            demo_mode = True
        elif raw_demo in ("false", "0", "no"):
            demo_mode = False
        else:
            # If not explicitly specified, enable DEMO_MODE if credentials aren't provided
            demo_mode = not (bool(consumer_key) and bool(consumer_secret))

        # Validation: If demo mode is disabled, credentials MUST be provided
        if not demo_mode and (not consumer_key or not consumer_secret):
            raise ValueError(
                "WC_CONSUMER_KEY and WC_CONSUMER_SECRET must be set when DEMO_MODE is False."
            )

        max_retries = int(os.getenv("MAX_RETRIES", "3"))
        request_timeout = float(os.getenv("REQUEST_TIMEOUT", "10.0"))

        return cls(
            wc_consumer_key=consumer_key,
            wc_consumer_secret=consumer_secret,
            wc_base_url=base_url,
            demo_mode=demo_mode,
            max_retries=max_retries,
            request_timeout=request_timeout,
        )

    def get_masked_summary(self) -> Dict[str, str]:
        """Return a dictionary of configuration options with secrets masked for safe logging."""
        masked_key = (
            f"{self.wc_consumer_key[:4]}...{self.wc_consumer_key[-4:]}"
            if len(self.wc_consumer_key) > 8
            else "***"
        )
        return {
            "wc_base_url": self.wc_base_url,
            "demo_mode": str(self.demo_mode),
            "wc_consumer_key": masked_key if self.wc_consumer_key else "[NOT SET]",
            "wc_consumer_secret": "***MASKED***" if self.wc_consumer_secret else "[NOT SET]",
            "max_retries": str(self.max_retries),
            "request_timeout": str(self.request_timeout),
        }
