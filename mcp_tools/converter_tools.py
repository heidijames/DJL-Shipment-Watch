"""RiskWatch tool and HTTP endpoint for monitoring shipments."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from mcp_resources.converter_resources import shipping_line_updates


router = APIRouter(prefix="", tags=["riskwatch"])


CARGO_RISK_SCORES = {
    "General": 10,
    "Temperature Sensitive": 40,
    "Perishable": 40,
}

#---------- Request Model -----------------------------------

class MonitorShipmentRequest(BaseModel):
    shipment_id: str = Field(min_length=1)

#-------- Helper Function -------------------------------------
def get_risk_level(risk_score: int) -> str:
    """
    Convert a numerical risk score into a risk level.
    """

    if risk_score >= 70:
        return "High"

    elif risk_score >= 40:
        return "Medium"

    else:
        return "Low"

#-------Core Business Logic Function----------------------------
def monitor_shipment_value(shipment_id: str):
    shipment_id = shipment_id.strip().upper()

    update_data = shipping_line_updates()
    updates = update_data["updates"]

    if shipment_id not in updates:
        raise HTTPException(
            status_code=404,
            detail=f"Shipment ID not found: {shipment_id}"
        )

    update = updates[shipment_id]

    cargo_category = update.get("cargo_category")
    delay_days = update.get("delay_days", 0)

    cargo_risk_score = CARGO_RISK_SCORES.get(cargo_category, 10)
    risk_score = cargo_risk_score + (delay_days * 10)
    risk_level = get_risk_level(risk_score)

    return {
        "shipment_id": shipment_id,
        "shipping_line": update.get("shipping_line"),
        "cargo_category": cargo_category,
        "current_status": update.get("current_status"),
        "current_location": update.get("current_location"),
        "eta": update.get("eta"),
        "delay_days": delay_days,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "update_note": update.get("update_note"),
    }


@router.post("/monitor-shipment")
def monitor_shipment(request: MonitorShipmentRequest):
    return monitor_shipment_value(request.shipment_id)

TOOL_DEFINITIONS = [
    {
        "name": "monitor_shipment",
        "description": "Monitor shipment status and assess basic cargo risk.",
        "func": monitor_shipment_value,
        "tags": {"shipment", "monitoring", "cargo-risk", "logistics"},
    }
]