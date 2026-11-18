
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ai.interpreter import interpret_command


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.server"],
    )

    print("EV Charging Assistant")
    print("Type 'exit' to quit.\n")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()
            print("Connected to MCP server!\n")

            tools = await session.list_tools()
            available_tools = {
                tool.name for tool in tools.tools
            }

            while True:
                user_input = input("You: ").strip()

                if user_input.lower() == "exit":
                    break

                if not user_input:
                    continue

                try:
                    command = await asyncio.to_thread(
                        interpret_command,
                        user_input,
                    )

                    action = command["action"]
                    current = command["current"]

                    if action == "unsupported":
                        print("Assistant: Unsupported instruction.\n")
                        continue

                    if action not in available_tools:
                        print("Assistant: MCP tool not available.\n")
                        continue

                    arguments = {}

                    if action == "set_charging_current":
                        arguments["current"] = current

                    if action != "get_charger_status":
                        print(f"Proposed action: {action}")
                        if arguments:
                            print(f"Parameters: {arguments}")

                        confirmation = input(
                            "Execute this simulated action? (yes/no): "
                        )

                        if confirmation.strip().lower() != "yes":
                            print("Assistant: Action cancelled.\n")
                            continue

                    result = await session.call_tool(
                        action,
                        arguments=arguments,
                    )

                    if result.isError:
                        print("Assistant: MCP tool reported an error.")
                    else:
                        for item in result.content:
                            if item.type == "text":
                                print("Assistant:", item.text)

                    print()

                except Exception as error:
                    print("Error:", error, "\n")


if __name__ == "__main__":
    asyncio.run(main())
