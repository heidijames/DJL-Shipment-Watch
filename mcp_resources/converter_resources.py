"""Reusable MCP resources for DJL Shipment Watch."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


# File location
BASE_DIR = Path(__file__).parent
SHIPPING_LINE_FILE = BASE_DIR / "shipping_line_updates.json"
DELAY_TEMPLATES_FILE = BASE_DIR / "delay_communication_templates.json"


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


def delay_communication_templates() -> Dict[str, Any]:
    """
    Provides customer communication templates for shipment delays.

    Returns:
        Dictionary containing minor and major delay communication templates.
    """
    return load_json(DELAY_TEMPLATES_FILE)


RESOURCE_DEFINITIONS = [
    {
        "name": "shipping_line_updates",
        "description": "Current shipment status, location, ETA and delay information.",
        "mime_type": "application/json",
        "func": shipping_line_updates,
    },
    {
        "name": "delay_communication_templates",
        "description": "Customer communication templates for minor and major shipment delays.",
        "mime_type": "application/json",
        "func": delay_communication_templates,
    },
]
