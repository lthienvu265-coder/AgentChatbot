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
    name_override="get_pet_transportation_regulations",
    description_override="Fetch official pet transportation regulations from iACV knowledge base",
)
def get_pet_transportation_regulations() -> str:
    result = call_mcp_tool("get_pet_transportation_regulations")
    content = result["result"]["content"]
    answers = []
    for item in content:
        answers.append(item["text"])
    return "\n\n".join(answers)