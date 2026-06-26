from dotenv import load_dotenv
from google import genai
from mcp_prompts.converter_prompts import (
    shipment_monitoring_prompt,
    delay_communication_prompt,
)
import os
import requests

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def get_shipment_data(shipment_id: str):
    response = requests.post(
        "http://localhost:8003/monitor-shipment",
        json={"shipment_id": shipment_id},
        timeout=10,
    )

    response.raise_for_status()
    return response.json()


def get_delay_communication(
    shipment_id: str,
    delay_severity: str,
):
    response = requests.post(
        "http://localhost:8003/generate-delay-communication",
        json={
            "shipment_id": shipment_id,
            "delay_severity": delay_severity,
        },
        timeout=10,
    )

    response.raise_for_status()
    return response.json()


print("\nDJL Shipment Watch + Gemini\n")
print("1 - Shipment Monitoring")
print("2 - Delay Communication")

choice = input("\nSelect option: ").strip()

if choice == "1":

    shipment_id = input(
        "Enter Shipment ID: "
    ).strip().upper()

    data = get_shipment_data(
        shipment_id
    )

    prompt = f"""
{shipment_monitoring_prompt()}

Shipment Data:

{data}

Use only the shipment data provided.
Do not invent missing details.
"""

elif choice == "2":

    shipment_id = input(
        "Enter Shipment ID: "
    ).strip().upper()

    delay_severity = input(
        "Enter Delay Severity (minor/major): "
    ).strip().lower()

    data = get_delay_communication(
        shipment_id,
        delay_severity,
    )

    prompt = f"""
{delay_communication_prompt()}

Communication Data:

{data}

Use only the information provided.
Do not invent missing details.
"""

else:
    raise ValueError(
        "Invalid option selected."
    )

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

print("\nGemini Response:\n")
print(response.text)