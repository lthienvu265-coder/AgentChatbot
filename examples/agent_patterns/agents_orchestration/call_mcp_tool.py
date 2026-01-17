import requests
import json
import os

# =========================
# Config
# =========================
os.environ["OPENAI_API_KEY"] = ""
MCP_URL = "http://localhost:3000/api/mcp"


# =========================
# MCP helpers
# =========================
def parse_sse_json(text: str) -> dict:
    for line in text.splitlines():
        if line.startswith("data:"):
            return json.loads(line[len("data:"):].strip())
    raise ValueError("No JSON found in SSE response")


def call_mcp_tool(tool_name: str, arguments: dict | None = None) -> dict:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {},
        },
    }

    response = requests.post(
        MCP_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
    )
    response.raise_for_status()
    return parse_sse_json(response.text)