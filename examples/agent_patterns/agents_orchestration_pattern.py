import asyncio
import requests
import json
from agents import Agent, AgentToolStreamEvent, ModelSettings, Runner, function_tool, trace

MCP_URL = "http://localhost:3000/api/mcp"


def parse_sse_json(text: str) -> dict:
    """
    Extract JSON from MCP SSE response:
    event: message
    data: {...}
    """
    for line in text.splitlines():
        if line.startswith("data:"):
            return json.loads(line[len("data:"):].strip())

    raise ValueError("No JSON found in SSE response")


def call_mcp_tool(tool_name: str, arguments: dict):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }

    response = requests.post(
        MCP_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )

    response.raise_for_status()

    # 🔑 MCP uses SSE
    return parse_sse_json(response.text)

@function_tool(
    name_override="get_popular_question",
    description_override="Getting popular questions then getting the questions and answers related to the question of the asker",
)
def get_popular_question(customer_id: str | None = None, question: str = "") -> str:
    """Getting popular questions then getting the questions and answers related to the question of the asker"""
    result = call_mcp_tool(
        tool_name="get_popular_question",
        arguments={}   # no parameters
    )

    print("Raw MCP response:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Tool result is inside result.content
    content = result["result"]["content"]

    print("\nPopular questions:\n")
    for item in content:
        text = item["text"]
        for question, answer in text.items():
            print("❓", question)
            print("👉", answer)
            print()


def handle_stream(event: AgentToolStreamEvent) -> None:
    """Print streaming events emitted by the nested popular questions agent."""
    stream = event["event"]
    tool_call = event.get("tool_call")
    tool_call_info = tool_call.call_id if tool_call is not None else "unknown"
    print(f"[stream] agent={event['agent'].name} call={tool_call_info} type={stream.type} {stream}")


async def main() -> None:
    with trace("Agents as tools streaming example"):
        get_popular_question_agent = Agent(
            name="Answer The Question Agent",
            instructions="You are a agent that answers popular questions.",
            model_settings=ModelSettings(tool_choice="required"),
            tools=[get_popular_question],
        )

        get_popular_agent_tool = get_popular_question_agent.as_tool(
            tool_name="get_popular_question_agent",
            tool_description="You are a agent that answers popular questions.",
            on_stream=handle_stream,
        )

        main_agent = Agent(
            name="Customer Support Agent",
            instructions=(
                "You are a customer support agent. Always call the popular question agent to answer the questions "
                "and return the response to the user."
            ),
            tools=[get_popular_agent_tool],
        )

        result = await Runner.run(
            main_agent,
            "Hello, my customer ID is ABC123. How much is my bill for this month?",
        )

    print(f"\nFinal response:\n{result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())


