from agents import function_tool
import json
from call_mcp_tool import call_mcp_tool


@function_tool(
    name_override="get_airport_locations",
    description_override=(
        "Retrieve airport latitude and longitude from the iACV knowledge base. "
        "Optionally accepts an airport name; the MCP server applies fuzzy matching "
        "to return the closest airport location."
    ),
)
def get_airport_locations(airport_name: str | None = None) -> str:
    # Call MCP tool with optional airport name
    if airport_name:
        result = call_mcp_tool(
            "get_airport_locations",
            arguments={"airportName": airport_name}
        )
    else:
        result = call_mcp_tool("get_airport_locations")

    # MCP tools usually return serialized JSON in content.text
    raw_content = result["result"]["content"][0]["text"]

    # Parse JSON string
    airport_locations = json.loads(raw_content)

    # Handle "no match found" response
    if isinstance(airport_locations, dict) and "message" in airport_locations:
        return airport_locations["message"]

    # Format response for agent consumption
    answers = []
    for airport_name, coordinates in airport_locations.items():
        latitude, longitude = coordinates.split(",")

        answers.append(
            f"Airport: {airport_name}\n"
            f"Latitude: {latitude.strip()}\n"
            f"Longitude: {longitude.strip()}"
        )

    return "\n\n".join(answers)
