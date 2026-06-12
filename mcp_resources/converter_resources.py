"""Reusable MCP resources for DJL RiskWatch."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


# File location
BASE_DIR = Path(__file__).parent
SHIPPING_LINE_FILE = BASE_DIR / "shipping_line_updates.json"


def load_json(file_path: Path) -> Dict[str, Any]:
    """
    Loads a JSON file and returns it as a Python dictionary.
    """
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def shipping_line_updates() -> Dict[str, Any]:
    """
    Provides current shipping line updates and shipment information.

    Returns:
        Dictionary containing shipment status, location,
        estimated arrival dates, delay information,
        and cargo category.
    """
    return {
        "id": "shipping-line-updates",
        "title": "Shipping Line Updates",
        "updates": load_json(SHIPPING_LINE_FILE),
    }


RESOURCE_DEFINITIONS = [
    {
        "name": "shipping_line_updates",
        "description": "Current shipment status, location, ETA and delay information.",
        "mime_type": "application/json",
        "func": shipping_line_updates,
    }
]