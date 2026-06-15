"""RiskWatch tool and HTTP endpoint for monitoring shipments."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from mcp_resources.converter_resources import shipping_line_updates


router = APIRouter(prefix="", tags=["riskwatch"])


CARGO_RISK_SCORES = {
    "General": 10,
    "Temperature Sensitive": 40,
    "Perishable": 40,
}


class MonitorShipmentRequest(BaseModel):
    shipment_id: str = Field(min_length=1)


class DelayCommunicationRequest(BaseModel):
    shipment_id: str = Field(min_length=1)
    delay_severity: str = Field(min_length=1)

    @field_validator("delay_severity")
    @classmethod
    def validate_delay_severity(cls, value):
        value = value.strip().lower()

        if value not in ["minor", "major"]:
            raise ValueError(
                "delay_severity must be either 'minor' or 'major'"
            )

        return value


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


def monitor_shipment_value(shipment_id: str):
    """
    Retrieve shipment information and calculate cargo risk.
    """

    shipment_id = shipment_id.strip().upper()

    update_data = shipping_line_updates()
    updates = update_data["updates"]

    if shipment_id not in updates:
        return {
            "error": f"Shipment ID not found: {shipment_id}"
        }

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
        "cause_of_delay": update.get("update_note"),
    }


def generate_delay_communication_value(
    shipment_id: str,
    delay_severity: str,
):
    """
    Generate a customer communication message for a delayed shipment.
    """

    shipment_id = shipment_id.strip().upper()
    delay_severity = delay_severity.strip().lower()

    update_data = shipping_line_updates()
    updates = update_data["updates"]

    if shipment_id not in updates:
        return {
            "error": f"Shipment ID not found: {shipment_id}"
        }

    if delay_severity not in ["minor", "major"]:
        return {
            "error": "delay_severity must be either 'minor' or 'major'"
        }

    update = updates[shipment_id]

    shipping_line = update.get("shipping_line")
    current_status = update.get("current_status")
    current_location = update.get("current_location")
    eta = update.get("eta")
    delay_days = update.get("delay_days", 0)
    cause_of_delay = update.get("update_note")

    if delay_severity == "minor":
        customer_message = (
            f"Shipment {shipment_id} with {shipping_line} is experiencing a minor delay. "
            f"The shipment is currently at {current_location}, with an estimated arrival date of {eta}. "
            "We are monitoring the shipment and will provide further updates if required."
        )
        follow_up_required = False

    else:
        customer_message = (
            f"Shipment {shipment_id} with {shipping_line} is experiencing a major delay. "
            f"The shipment is currently at {current_location}, with an estimated arrival date of {eta}. "
            f"Reason noted: {cause_of_delay} "
            "Our logistics team is actively monitoring the issue and will provide further updates as soon as possible."
        )
        follow_up_required = True

    return {
        "shipment_id": shipment_id,
        "shipping_line": shipping_line,
        "current_status": current_status,
        "current_location": current_location,
        "eta": eta,
        "delay_days": delay_days,
        "delay_severity": delay_severity,
        "cause_of_delay": cause_of_delay,
        "customer_message": customer_message,
        "follow_up_required": follow_up_required,
    }


@router.post("/monitor-shipment")
def monitor_shipment(request: MonitorShipmentRequest):
    """
    HTTP endpoint: monitor shipment status and cargo risk.
    """

    result = monitor_shipment_value(
        request.shipment_id
    )

    if "error" in result:
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )

    return result


@router.post("/generate-delay-communication")
def generate_delay_communication(request: DelayCommunicationRequest):
    """
    HTTP endpoint: generate customer delay communication.
    """

    result = generate_delay_communication_value(
        request.shipment_id,
        request.delay_severity,
    )

    if "error" in result:
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )

    return result


TOOL_DEFINITIONS = [
    {
        "name": "monitor_shipment",
        "description": "Monitor shipment status and assess basic cargo risk.",
        "func": monitor_shipment_value,
        "tags": {"shipment", "monitoring", "cargo-risk", "logistics"},
    },
    {
        "name": "generate_delay_communication",
        "description": "Generate a customer communication message for a delayed shipment.",
        "func": generate_delay_communication_value,
        "tags": {"shipment", "delay", "customer-communication", "logistics"},
    },
]