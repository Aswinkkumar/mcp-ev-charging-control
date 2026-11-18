
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            print("Connected to MCP server!")

            tools = await session.list_tools()

            print("\nAvailable tools:")
            for tool in tools.tools:
                print("-", tool.name)

            print("\nInitial status:")
            print((await session.call_tool(
                "get_charger_status"
            )).content)

            print("\nStarting charging:")
            print((await session.call_tool(
                "start_charging"
            )).content)

            print("\nSetting current to 12 A:")
            print((await session.call_tool(
                "set_charging_current",
                arguments={"current": 12}
            )).content)

            print("\nUpdated status:")
            print((await session.call_tool(
                "get_charger_status"
            )).content)

            print("\nStopping charging:")
            print((await session.call_tool(
                "stop_charging"
            )).content)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
