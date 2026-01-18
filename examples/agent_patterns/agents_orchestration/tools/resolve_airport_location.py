from agents import function_tool
from call_mcp_tool import call_mcp_tool
import json


@function_tool(
    name_override="resolve_airport_location",
    description_override=(
        "Resolve airport location name using TomTom Geocoding API. "
        "Returns latitude, longitude, resolved name, and confidence score."
    ),
)
def resolve_airport_location(location_name: str) -> str:
    """
    Calls MCP tool: resolve_airport_location
    """

    payload = {
        "locationName": location_name
    }

    # Call MCP tool
    result = call_mcp_tool("resolve_airport_location", payload)

    # MCP standard response extraction
    content = result["result"]["content"]

    return content