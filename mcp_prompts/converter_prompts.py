from __future__ import annotations


def shipment_monitoring_prompt():
    """
    Prompt the assistant to check shipment status and explain cargo risk.
    """

    return (
        "You are a logistics operations advisor. "
        "When a user asks about a shipment, identify the shipment ID and use the "
        "monitor_shipment tool to retrieve shipment details. "
        "Then provide a concise shipment status summary, cargo risk assessment, "
        "cause of delay, and recommended operational action."
    )


PROMPT_DEFINITIONS = [
    {
        "name": "shipment_monitoring",
        "description": "Prompt the assistant to check shipment status and explain cargo risk.",
        "func": shipment_monitoring_prompt,
    }
]