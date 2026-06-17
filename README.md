
# DJL Shipment Watch API + MCP Server

DJL Shipment Watch is a simplified logistics monitoring system built using FastAPI and FastMCP.

The system provides:

* Shipment monitoring by shipment ID
* Shipping line status lookup
* Basic cargo risk assessment
* Customer delay communication generation
* Two MCP tools
* Two MCP resources
* Two MCP prompts
* HTTP API endpoints through FastAPI
* MCP access through Streamable HTTP

---

## Prerequisites

* Python 3.10+
* Virtual environment
* npm for MCP Inspector

---

## Setup from this Folder

```bash
python -m venv .venv

# Git Bash
source .venv/Scripts/activate

# Windows PowerShell
.venv\Scripts\activate

python -m pip install -r requirements.txt
```

---

## Run the HTTP + MCP Server

```bash
python converter_streamable_http_server.py
```

You should see:

```text
Swagger UI:
http://localhost:8003/docs

ReDoc:
http://localhost:8003/redoc

MCP Endpoint:
http://localhost:8003/mcp/

SSE Endpoint:
http://localhost:8003/sse
```

---

## MCP Components

Tools
* monitor_shipment_monitor_shipment_post
* generate_delay_communication_generate_delay_communicatio

Resources
* resource://shipping_line_updates
* resource://delay_communication_templates

Prompts
* shipment_monitoring
* delay_communication

---

## Supported Input

### Shipment ID Examples

```text
SHP001
SHP002
SHP003
SHP004
SHP005
```

---

# Testing Guide

## 1. Swagger Testing

Open:

```text
http://localhost:8003/docs
```

Expand:

```text
POST /monitor-shipment
```

Click **Try it Out** and enter:

```json
{
  "shipment_id": "SHP002"
}
```

Expected response:

```json
{
  "shipment_id": "SHP002",
  "shipping_line": "MSC",
  "cargo_category": "Temperature Sensitive",
  "current_status": "Delayed",
  "current_location": "Port Klang",
  "eta": "2026-06-18",
  "delay_days": 3,
  "risk_score": 70,
  "risk_level": "High",
  "cause_of_delay": "Shipment is delayed due to port congestion."
}
```

---

## 2. HTTP Endpoint Testing Using curl

### Monitor Shipment

```bash
curl -X POST "http://localhost:8003/monitor-shipment" \
-H "Content-Type: application/json" \
-d '{
  "shipment_id":"SHP002"
}'
```

Expected response:

```json
{
  "shipment_id": "SHP002",
  "shipping_line": "MSC",
  "cargo_category": "Temperature Sensitive",
  "current_status": "Delayed",
  "current_location": "Port Klang",
  "eta": "2026-06-18",
  "delay_days": 3,
  "risk_score": 70,
  "risk_level": "High",
  "cause_of_delay": "Shipment is delayed due to port congestion."
}
```
### Generate Delay Communication

```bash
curl -X POST "http://localhost:8003/generate-delay-communication" \
-H "Content-Type: application/json" \
-d '{
  "shipment_id":"SHP002",
  "delay_severity":"major"
}'
```

Expected response:

```json
{
  "shipment_id": "SHP002",
  "shipping_line": "MSC",
  "current_status": "Delayed",
  "current_location": "Port Klang",
  "eta": "2026-06-18",
  "delay_days": 3,
  "delay_severity": "major",
  "cause_of_delay": "Shipment is delayed due to port congestion.",
  "customer_message": "Shipment SHP002 with MSC is experiencing a major delay. The shipment is currently at Port Klang, with an estimated arrival date of 2026-06-18. Reason noted: Shipment is delayed due to port congestion. Our logistics team is actively monitoring the issue and will provide further updates as soon as possible.",
  "follow_up_required": true
}
```
---

## 3. MCP Inspector Testing

Keep the server running.

Open a new terminal and run:

```bash
npx @modelcontextprotocol/inspector@latest \
-e DUMMY=1 \
--url http://localhost:8003/mcp/ \
--transport streamable-http
```

The terminal will display an Inspector URL.

Open the URL in your browser.

Verify the following components are visible:

### Tools

* monitor_shipment_monitor_shipment_post
* generate_delay_communication_generate_delay_communicatio

### Resources

* resource://shipping_line_updates
* resource://delay_communication_templates

### Prompts

* shipment_monitoring
* delay_communication
---

## 4. MCP JSON-RPC Testing Using curl

### Step 1 – Obtain an MCP Session ID and Initiliaze MCP Session

The Streamable HTTP MCP endpoint requires a valid session ID.

Run:

```bash
curl -i "http://localhost:8003/mcp/" \
-H "Accept: application/json, text/event-stream"
```

Example response:

```text
HTTP/1.1 400 Bad Request

mcp-session-id: de6a50e0292e4302bb22519122b5ac10
```

Copy the value returned in:

```text
mcp-session-id
```

and use it in subsequent MCP requests.

## Initialize MCP Session

Replace `<SESSION_ID>` with the session ID returned in the previous step.

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "MCP-Protocol-Version: 2025-06-18" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl-test","version":"1.0.0"}},"id":0}'
```

Expected result:

The MCP session is initialized successfully and ready to accept JSON-RPC requests.

### Step 2 – List Tools


Replace <SESSION_ID> with your MCP session ID.

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "MCP-Protocol-Version: 2025-06-18" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```
Expected tools:

Expected tools:

monitor_shipment_monitor_shipment_post
generate_delay_communication_generate_delay_communicatio


### Step 3 – List Resources

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "MCP-Protocol-Version: 2025-06-18" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"resources/list","params":{},"id":2}'
```

Expected resource:

```text
resource://shipping_line_updates
resource://delay_communication_templates
```

---

### Step 4 – Read Resources

Resource 1 - Shipping Line Updates

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "MCP-Protocol-Version: 2025-06-18" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"resources/read","params":{"uri":"resource://shipping_line_updates"},"id":3}'

Resource 2 - delay_communication_templates
```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "MCP-Protocol-Version: 2025-06-18" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"resources/read","params":{"uri":"resource://delay_communication_templates"},"id":4}'



### Step 5 – List Prompts

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "MCP-Protocol-Version: 2025-06-18" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"prompts/list","params":{},"id":5}'
```

Expected prompt:

```text
shipment_monitoring 
delay_communication
```

---

### Step 6 – Get Prompt

Prompt 1 - Shipment Monitoring Prompt
```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "MCP-Protocol-Version: 2025-06-18" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"prompts/get","params":{"name":"shipment_monitoring","arguments":{}},"id":6}'
```

Prompt 2 - Delay Communication

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "MCP-Protocol-Version: 2025-06-18" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"prompts/get","params":{"name":"delay_communication","arguments":{}},"id":7}'
```
### Step 7 – Call Tools

Tool 1 - Call Tool 1: Monitor Shipment

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "MCP-Protocol-Version: 2025-06-18" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"monitor_shipment_monitor_shipment_post","arguments":{"shipment_id":"SHP002"}},"id":8}'
```

Tool 2 - Generate Delay Communication

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "MCP-Protocol-Version: 2025-06-18" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"generate_delay_communication_generate_delay_communicatio","arguments":{"shipment_id":"SHP002","delay_severity":"major"}},"id":9}'



---

## Project Structure

```text
DJL Shipment Watch/

├── converter_streamable_http_server.py
├── converter_stdio_server.py
├── requirements.txt

├── mcp_tools/
│   └── converter_tools.py

├── mcp_resources/
│   ├── converter_resources.py
│   ├── shipping_line_updates.json
│   └── delay_communication_templates.json

├── mcp_prompts/
│   └── converter_prompts.py

├── utils/
│   └── logging_utils.py

├── logs/
└── README.md
```

---

## Error Handling

### Common HTTP Errors

* 400 Bad Request
* 404 Not Found
* 422 Validation Error

### Common JSON-RPC Errors

* -32700 Parse Error
* -32600 Invalid Request
* -32601 Method Not Found
* -32602 Invalid Parameters
* -32603 Internal Error

---

## Development Notes

Key issues discovered and resolved during testing:

1. Shipment ID input cleaning using Pydantic
2. Shipment ID lookup against the JSON resource
3. Cargo risk calculation based on cargo category and delay days
4. MCP session ID requirement
5. Streamable HTTP MCP endpoint requires Accept headers and session-based communication
6. MCP resource serialization using `json.dumps()` for successful `resources/read` operations

Testing was completed using:

* Swagger
* curl
* MCP Inspector
* Git version control
