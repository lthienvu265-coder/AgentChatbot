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
    name_override="get_vietjet_air_ticket_condition",
    description_override="Fetch official Vietjet air ticket conditions from iACV knowledge base",
)
def get_vietjet_air_ticket_condition() -> str:
    result = call_mcp_tool("get_vietjet_air_ticket_condition")
    content = result["result"]["content"]
    answers = []
    for item in content:
        answers.append(item["text"])
    return "\n\n".join(answers)