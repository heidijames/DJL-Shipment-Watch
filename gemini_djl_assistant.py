from dotenv import load_dotenv
from google import genai
from mcp_prompts.converter_prompts import (
    shipment_monitoring_prompt,
    delay_communication_prompt,
)
import json
import os
import re
import requests


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def monitor_shipment(shipment_id: str):
    response = requests.post(
        "http://localhost:8003/monitor-shipment",
        json={"shipment_id": shipment_id},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def generate_delay_communication(shipment_id: str, delay_severity: str):
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


def extract_shipment_id(user_query: str):
    match = re.search(r"SHP\d{3}", user_query.upper())
    return match.group(0) if match else None


def classify_intent(user_query: str):
    query = user_query.lower()

    if "customer" in query or "email" in query or "message" in query or "communication" in query or "update" in query:
        return "delay_communication"

    return "shipment_monitoring"


def extract_delay_severity(user_query: str):
    query = user_query.lower()

    if "major" in query:
        return "major"

    if "minor" in query:
        return "minor"

    return "major"


print("\nDJL Logistics AI Assistant")
print("Type 'exit' to quit.\n")

while True:
    user_query = input("Ask DJL Assistant: ").strip()

    if user_query.lower() in ["exit", "quit"]:
        break

    shipment_id = extract_shipment_id(user_query)

    if not shipment_id:
        print("\nPlease include a shipment ID such as SHP002.\n")
        continue

    intent = classify_intent(user_query)

    try:
        if intent == "delay_communication":
            delay_severity = extract_delay_severity(user_query)
            data = generate_delay_communication(shipment_id, delay_severity)

            prompt = f"""
{delay_communication_prompt()}

User request:
{user_query}

Tool result:
{json.dumps(data, indent=2)}

Use only the tool result provided.
Do not invent missing details.
"""

        else:
            data = monitor_shipment(shipment_id)

            prompt = f"""
{shipment_monitoring_prompt()}

User request:
{user_query}

Tool result:
{json.dumps(data, indent=2)}

Use only the tool result provided.
Do not invent missing details.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        print("\nGemini Response:\n")
        print(response.text)
        print("\n" + "-" * 60 + "\n")

    except requests.exceptions.HTTPError as error:
        print("\nAPI Error:")
        print(error)
        print()

    except Exception as error:
        print("\nUnexpected Error:")
        print(error)
        print()