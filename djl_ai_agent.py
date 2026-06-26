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

DJL_API_BASE_URL = "http://localhost:8003"


def monitor_shipment(shipment_id: str):
    response = requests.post(
        f"{DJL_API_BASE_URL}/monitor-shipment",
        json={"shipment_id": shipment_id},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def generate_delay_communication(shipment_id: str, delay_severity: str):
    response = requests.post(
        f"{DJL_API_BASE_URL}/generate-delay-communication",
        json={
            "shipment_id": shipment_id,
            "delay_severity": delay_severity,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def extract_json_from_text(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError("Gemini did not return JSON.")

    return json.loads(match.group(0))


def plan_tool_call(user_query: str, last_shipment_id: str | None):
    planning_prompt = f"""
You are a tool planner for DJL Shipment Watch.

Choose the correct tool for the user's request.

Available tools:

1. monitor_shipment
Use this when the user asks about shipment status, location, ETA, delay, cargo risk, or operational action.

Required arguments:
- shipment_id

2. generate_delay_communication
Use this when the user asks to draft, write, generate, prepare, or send a customer/client delay update, email, message, or letter.

Required arguments:
- shipment_id
- delay_severity: must be either "minor" or "major"

Conversation memory:
Last shipment ID: {last_shipment_id}

User request:
{user_query}

Rules:
- Return JSON only.
- Do not include markdown.
- Do not explain.
- If the user does not provide a shipment ID, use the last shipment ID if available.
- If no shipment ID is available, return tool "missing_information".
- If delay_severity is not provided for delay communication, default to "major".

Return format examples:

{{
  "tool": "monitor_shipment",
  "arguments": {{
    "shipment_id": "SHP002"
  }}
}}

{{
  "tool": "generate_delay_communication",
  "arguments": {{
    "shipment_id": "SHP002",
    "delay_severity": "major"
  }}
}}

{{
  "tool": "missing_information",
  "message": "Please provide a shipment ID such as SHP002."
}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=planning_prompt,
    )

    return extract_json_from_text(response.text)


def execute_tool(plan: dict):
    tool = plan.get("tool")
    arguments = plan.get("arguments", {})

    if tool == "monitor_shipment":
        return monitor_shipment(
            arguments["shipment_id"]
        )

    if tool == "generate_delay_communication":
        return generate_delay_communication(
            arguments["shipment_id"],
            arguments["delay_severity"],
        )

    return None


def build_final_prompt(tool_name: str, user_query: str, tool_result: dict):
    if tool_name == "generate_delay_communication":
        base_prompt = delay_communication_prompt()
    else:
        base_prompt = shipment_monitoring_prompt()

    return f"""
{base_prompt}

User request:
{user_query}

Tool result:
{json.dumps(tool_result, indent=2)}

Instructions:
- Use only the tool result provided.
- Do not invent missing details.
- If the user asks for a customer message, write it in a clear professional tone.
- If the user asks for shipment status, summarize status, location, ETA, delay, risk, and recommended action.
"""


last_shipment_id = None
last_tool_result = None


print("\n========================================")
print("      DJL Logistics AI Assistant")
print("========================================")
print("Type 'exit' to quit.\n")

while True:
    user_query = input("You: ").strip()

    if user_query.lower() in ["exit", "quit"]:
        print("\nGoodbye!\n")
        break

    try:
        plan = plan_tool_call(
            user_query,
            last_shipment_id,
        )

        if plan.get("tool") == "missing_information":
            print("\nAssistant:")
            print(plan.get("message", "Please provide more information."))
            print()
            continue

        tool_result = execute_tool(plan)

        last_tool_result = tool_result

        if "arguments" in plan and "shipment_id" in plan["arguments"]:
            last_shipment_id = plan["arguments"]["shipment_id"]

        final_prompt = build_final_prompt(
            plan["tool"],
            user_query,
            tool_result,
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=final_prompt,
        )

        print("\nAssistant:\n")
        print(response.text)
        print("\n----------------------------------------\n")

    except requests.exceptions.HTTPError as error:
        print("\nAPI Error:")
        print(error)
        print()

    except Exception as error:
        print("\nUnexpected Error:")
        print(error)
        print()