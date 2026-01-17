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
    name_override="get_luggage_regulations",
    description_override="Fetch official luggage regulations from iACV knowledge base",
)
def get_luggage_regulations() -> str:
    result = call_mcp_tool("get_luggage_regulations")
    content = result["result"]["content"]
    answers = []
    for item in content:
        answers.append(item["text"])
    return "\n\n".join(answers)
