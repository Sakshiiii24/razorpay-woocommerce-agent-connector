"""Tests for the demo script workflow."""

import pytest
from demo import run_demo


@pytest.mark.asyncio
async def test_demo_execution():
    """Verify that demo script completes without raising any exceptions."""
    try:
        await run_demo()
    except Exception as e:
        pytest.fail(f"demo.py raised an unexpected exception: {e}")
