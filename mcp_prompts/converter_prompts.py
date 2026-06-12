"""Prompt templates used by the DJL RiskWatch system."""

from __future__ import annotations

from typing import Dict, List


def shipment_monitoring_prompt() -> List[Dict[str, str]]:
    """
    Explain shipment status, cargo risk, and recommended actions.
    """

    return [
        {
            "role": "system",
            "content": (
                "You are a logistics operations advisor. "
                "Review the shipment monitoring result and explain the shipment status, "
                "risk level, cause of delay, and recommended operational action. "
                "Keep the response concise and professional."
            ),
        },
        {
            "role": "user",
            "content": (
                "Review shipment {shipment_id}. "
                "Status: {current_status}. "
                "Cargo Category: {cargo_category}. "
                "Risk Level: {risk_level}. "
                "Cause of Delay: {cause_of_delay}. "
                "Provide a brief operational summary and recommended action."
            ),
        },
    ]