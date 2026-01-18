import asyncio
import requests
import json
import os
from agents import (
    Agent,
    ModelSettings,
    Runner,
    function_tool,
    trace,
)
from call_mcp_tool import call_mcp_tool

@function_tool(
    name_override="calculate_route",
    description_override=(
        "Calculate route using TomTom Routing API with dynamic routing options. "
        "Returns travel time, traffic delay, and distance."
    ),
)
def calculate_route(
    from_latitude: float,
    from_longitude: float,
    to_latitude: float,
    to_longitude: float,
    travel_mode: str = "car",
    traffic: bool = True,
    route_type: str = "fastest",
) -> str:
    """
    Calls MCP tool: calculate_route
    """

    payload = {
        "fromLatitude": from_latitude,
        "fromLongitude": from_longitude,
        "toLatitude": to_latitude,
        "toLongitude": to_longitude,
        "travelMode": travel_mode,
        "traffic": traffic,
        "routeType": route_type,
    }

    # Call MCP tool
    result = call_mcp_tool("calculate_route", payload)

    # MCP standard response extraction
    content = result["result"]["content"]

    return content