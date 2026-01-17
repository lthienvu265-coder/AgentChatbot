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
    name_override="get_popular_question",
    description_override="Fetch popular questions and official answers from the knowledge base",
)
def get_popular_question() -> str:
    result = call_mcp_tool("get_popular_question")
    content = result["result"]["content"]
    answers = []
    for item in content:
        answers.append(item["text"])
    return "\n\n".join(answers)