# Unit Converter API + MCP (tools, resources, prompts)
# Uses FastAPI for HTTP routes and FastMCP to expose tools/resources/prompts over HTTP/SSE transports.
from fastapi import FastAPI, APIRouter
from fastmcp import FastMCP
import json

from mcp_tools.converter_tools import router as converter_router

from mcp_resources.converter_resources import shipping_line_updates

from mcp_prompts.converter_prompts import shipment_monitoring_prompt

from utils.logging_utils import build_log_config

import platform
import datetime
import os
import time
from pathlib import Path
import uvicorn


PORT = 8003

LOG_FILE = Path("logs/mcp_log_streamable_http.log")

LOG_CONFIG = build_log_config(
    LOG_FILE,
    logger_handlers={
        "uvicorn": ["rotating_file", "console"],
        "uvicorn.error": ["rotating_file", "console"],
        "uvicorn.access": ["rotating_file"],
    },
    root_level="INFO",
    logger_level="DEBUG",
)

# FastAPI app for plain HTTP
app = FastAPI(
    title="DJL Shipment Watch Server",
    description="FastAPI endpoints auto-exposed as MCP tools via FastMCP, with resources and prompts.",
    version="1.2.1",
)
app.include_router(converter_router)

# System health router
system_router = APIRouter(prefix="", tags=["system"])
_started_at = time.time()


# @system_router.get("/health")
# def health():
#     return {
#         "status": "ok",
#         "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
#         "python": platform.python_version(),
#         "platform": platform.platform(),
#         "pid": os.getpid(),
#         "cwd": os.getcwd(),
#         "uptime_seconds": round(time.time() - _started_at, 2),
#     }


app.include_router(system_router)

# FastMCP server generated from FastAPI OpenAPI (tools) plus manual resources/prompts
mcp = FastMCP.from_fastapi(
    app,
    name="DJL Shipment Watch MCP Server",
    instructions="Shipment risk assessment tools with supporting resources and prompts.",
)


# Resources
@mcp.resource(
    "resource://shipping_line_updates",
    name="Shipping Line Updates",
    mime_type="application/json",
)
def _resource_shipping_line_updates():
    return json.dumps(shipping_line_updates(), indent=2)


# Prompts
@mcp.prompt(
    name="shipment_monitoring",
    description="Explain shipment status, cargo risk, and recommended actions.",
)
def _prompt_shipment_monitoring():
    return shipment_monitoring_prompt()


# Build MCP sub-apps (need lifespan) and mount onto FastAPI
mcp_http_app = mcp.http_app(path="/", transport="streamable-http")
mcp_sse_app = mcp.http_app(path="/", transport="sse")
# Ensure FastAPI runs the MCP lifespan so streamable-http initializes properly
app.router.lifespan_context = mcp_http_app.lifespan

app.mount("/mcp", mcp_http_app)
app.mount("/sse", mcp_sse_app)


if __name__ == "__main__":
    import uvicorn

    PORT = 8003 # avoid conflicts/permissions on lower ports
    print("Starting the DJL Shipment Watch API server (HTTP + MCP tools/resources/prompts)...")
    print(f"HTTP docs:      http://localhost:{PORT}/docs")
    print(f"HTTP redoc:     http://localhost:{PORT}/redoc")
    print(f"MCP endpoint:   http://localhost:{PORT}/mcp (HTTP)")
    print(f"MCP endpoint:   http://localhost:{PORT}/sse (SSE)")

    uvicorn.run(
        app,
        host="localhost",
        port=PORT,
        log_level="trace",   # Uvicorn internal level
        log_config=LOG_CONFIG,
    )
