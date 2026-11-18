
import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

llm = OpenAI(
    api_key=os.environ["UNIVERSITY_API_KEY"],
    base_url=os.environ["UNIVERSITY_API_BASE_URL"],
)

MODEL = os.getenv("UNIVERSITY_MODEL", "gpt-oss:20b")


def convert_mcp_tools(mcp_tools):
    """Convert MCP tool definitions to OpenAI tool format."""

    tools = []

    for tool in mcp_tools:
        tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            },
        })

    return tools


def select_tool(user_message, tools):
    """Ask the university LLM to select an MCP tool."""

    response = llm.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You control a simulated EV charger. "
                    "Select at most one appropriate tool. "
                    "Use only the supplied tools. "
                    "Do not invent missing parameters. "
                    "For unclear, unrelated, or multi-action "
                    "requests, do not call a tool. "
                    "Never claim a tool has already executed."
                ),
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        tools=tools,
        tool_choice="auto",
        temperature=0,
    )

    return response.choices[0].message


async def main():

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.server"],
    )

    print("Dynamic MCP EV Charging Assistant")
    print("Type 'exit' to quit.\n")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()
            print("Connected to MCP server!")

            discovered = await session.list_tools()
            tools = convert_mcp_tools(discovered.tools)

            tool_lookup = {
                tool.name: tool
                for tool in discovered.tools
            }

            print("\nDynamically discovered tools:")
            for tool in tools:
                print("-", tool["function"]["name"])

            while True:
                user_input = input("\nYou: ").strip()

                if user_input.lower() == "exit":
                    break

                if not user_input:
                    continue

                try:
                    message = await asyncio.to_thread(
                        select_tool, user_input, tools
                    )

                    if not message.tool_calls:
                        print(
                            "Assistant: No suitable tool selected."
                        )
                        continue

                    if len(message.tool_calls) != 1:
                        print(
                            "Assistant: Multiple tool calls "
                            "are not supported yet."
                        )
                        continue

                    call = message.tool_calls[0]

                    if call.type != "function":
                        print("Assistant: Unsupported tool call.")
                        continue

                    tool_name = call.function.name

                    if tool_name not in tool_lookup:
                        print("Assistant: Unknown tool rejected.")
                        continue

                    arguments = json.loads(
                        call.function.arguments
                    )

                    if not isinstance(arguments, dict):
                        print("Assistant: Invalid arguments.")
                        continue

                    # Validate the model's arguments against
                    # the MCP tool's JSON Schema.
                    from jsonschema import validate

                    validate(
                        instance=arguments,
                        schema=tool_lookup[tool_name].inputSchema,
                    )

                    # Extra safety check for simulated current.
                    if tool_name == "set_charging_current":
                        current = arguments.get("current")

                        if (
                            isinstance(current, bool)
                            or not isinstance(
                                current, (int, float)
                            )
                        ):
                            print(
                                "Assistant: Invalid current."
                            )
                            continue

                    print("\nSelected tool:", tool_name)
                    print("Arguments:", arguments)

                    if tool_name != "get_charger_status":
                        confirm = input(
                            "Execute simulated action? (yes/no): "
                        )

                        if confirm.strip().lower() != "yes":
                            print("Assistant: Cancelled.")
                            continue

                    result = await session.call_tool(
                        tool_name,
                        arguments=arguments,
                    )

                    if result.isError:
                        print("Assistant: MCP tool error.")

                    for item in result.content:
                        if item.type == "text":
                            print("Assistant:", item.text)

                except Exception as error:
                    print("Error:", error)


if __name__ == "__main__":
    asyncio.run(main())
