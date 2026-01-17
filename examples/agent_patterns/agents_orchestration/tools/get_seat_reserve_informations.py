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
    name_override="get_seat_reserve_informations",
    description_override="Fetch official seat reservation information from iACV knowledge base",
)
def get_seat_reserve_informations() -> str:
    result = call_mcp_tool("get_seat_reserve_informations")
    content = result["result"]["content"]
    answers = []
    for item in content:
        answers.append(item["text"])
    return "\n\n".join(answers)