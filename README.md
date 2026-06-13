# DJL Shipment Watch API + MCP Server

DJL Shipment Watch is a simplified logistics monitoring system built using FastAPI and FastMCP.

The system provides:

* Shipment monitoring by shipment ID
* Shipping line status lookup
* Basic cargo risk assessment
* One MCP tool
* One MCP resource
* One MCP prompt
* HTTP API endpoint through FastAPI
* MCP access through Streamable HTTP

---

## Prerequisites

* Python 3.10+
* Virtual environment
* npm for MCP Inspector

---

## Setup from this folder

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

## Open MCP Inspector

With the server running, open a new terminal and run:

```bash
npx @modelcontextprotocol/inspector@latest \
-e DUMMY=1 \
--url http://localhost:8003/mcp/ \
--transport streamable-http
```
npx @modelcontextprotocol/inspector python converter_stdio_server.py

Open the displayed Inspector URL in your browser.

---

## MCP Components

### Tool

* monitor_shipment

### Resource

* resource://shipping_line_updates

### Prompt

* shipment_monitoring

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

## HTTP Endpoint Testing

### Monitor Shipment

```bash
curl -X POST "http://localhost:8003/monitor-shipment" \
-H "Content-Type: application/json" \
-d '{
  "shipment_id":"SHP002"
}'
```

Example response:

```json
{
  "shipment_id": "SHP002",
  "shipping_line": "MSC",
  "cargo_category": "Temperature Sensitive",
  "current_status": "Delayed",
  "current_location": "Port Klang",
  "eta": "2026-06-18",
  "delay_days": 3,
  "risk_score": 60,
  "risk_level": "Medium",
  "update_note": "Shipment is delayed due to port congestion."
}
```

---

## Obtaining an MCP Session ID

The Streamable HTTP MCP endpoint requires a valid session ID before JSON-RPC requests can be executed.

Run:

```bash
curl -i http://localhost:8003/mcp/
```

Copy the value returned in:

```text
mcp-session-id
```

Use it in subsequent MCP JSON-RPC requests.

---

## MCP JSON-RPC Testing

Replace `<SESSION_ID>` with your actual MCP session ID.

### List Tools

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```

### List Resources

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"resources/list","params":{},"id":2}'
```

### Read Shipping Line Updates Resource

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"resources/read","params":{"uri":"resource://shipping_line_updates"},"id":3}'
```

### List Prompts

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"prompts/list","params":{},"id":4}'
```

### Get Shipment Monitoring Prompt

```bash
curl -N -X POST "http://localhost:8003/mcp/" \
-H "Content-Type: application/json" \
-H "Accept: application/json, text/event-stream" \
-H "mcp-session-id:<SESSION_ID>" \
-d '{"jsonrpc":"2.0","method":"prompts/get","params":{"name":"shipment_monitoring"},"id":5}'
```

---

## MCP Inspector Testing

Use MCP Inspector to verify:

### Tool

* monitor_shipment

### Resource

* shipping_line_updates

### Prompt

* shipment_monitoring

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
│   └── shipping_line_updates.json

├── mcp_prompts/
│   └── converter_prompts.py

├── utils/
│   └── logging_utils.py

├── logs/
└── README.md
```

---

## Error Handling

Common HTTP errors:

* 400 Bad Request
* 404 Not Found
* 422 Validation Error

Common JSON-RPC errors:

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

Testing was completed using:

* Swagger
* curl
* MCP Inspector
* Git version control
