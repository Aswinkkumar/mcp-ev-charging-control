
import csv
import sys
import time
from pathlib import Path

# Allow imports from the project root.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from ai.dynamic_tool_client import (
    convert_mcp_tools,
    select_tool,
)

import asyncio
import json


TEST_CASES = [
    # Start / stop charging
    ("Start charging my car", "start_charging", None),
    ("Begin charging", "start_charging", None),
    ("Please start the charger", "start_charging", None),
    ("Stop charging", "stop_charging", None),
    ("End the charging session", "stop_charging", None),
    ("Please stop the charger", "stop_charging", None),

    # Charging status
    ("What is my charging status?", "get_charger_status", None),
    ("Is the charger running?", "get_charger_status", None),
    ("Show charger status", "get_charger_status", None),
    ("Is my car charging?", "get_charger_status", None),

    # Current adjustment
    ("Set charging current to 12 amps",
     "set_charging_current", 12),
    ("Limit charging to 8 A",
     "set_charging_current", 8),
    ("Change charging current to 10 amperes",
     "set_charging_current", 10),
    ("Set current to 16 A",
     "set_charging_current", 16),
    ("Set current to 25 A",
     "set_charging_current", 25),
    ("Adjust charging to 6 amps",
     "set_charging_current", 6),

    # Ambiguous instructions
    ("Change the charging current", None, None),
    ("Make charging faster", None, None),
    ("Do something with the charger", None, None),
    ("Start charging and set current to 12 A", None, None),
    ("Increase the charging current", None, None),

    # Unsupported instructions
    ("What is the weather today?", None, None),
    ("Unlock my car", None, None),
    ("Play some music", None, None),
    ("Book a train ticket", None, None),
]


async def main():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.server"],
        cwd=str(ROOT),
    )

    results = []

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            discovered = await session.list_tools()
            tools = convert_mcp_tools(discovered.tools)

            for instruction, expected_tool, expected_current in TEST_CASES:
                start = time.perf_counter()

                try:
                    message = await asyncio.to_thread(
                        select_tool, instruction, tools
                    )

                    calls = message.tool_calls or []

                    if len(calls) == 0:
                        predicted_tool = None
                        predicted_current = None

                    elif len(calls) == 1:
                        call = calls[0]

                        if call.type != "function":
                            predicted_tool = "INVALID_CALL"
                            predicted_current = None
                        else:
                            predicted_tool = call.function.name
                            arguments = json.loads(
                                call.function.arguments
                            )
                            predicted_current = arguments.get("current")

                    else:
                        predicted_tool = "MULTIPLE_CALLS"
                        predicted_current = None

                    error = ""

                except Exception as exc:
                    predicted_tool = "ERROR"
                    predicted_current = None
                    error = str(exc)

                elapsed = time.perf_counter() - start

                tool_correct = predicted_tool == expected_tool

                parameter_correct = (
                    tool_correct
                    and predicted_current == expected_current
                )

                results.append({
                    "instruction": instruction,
                    "expected_tool": expected_tool,
                    "predicted_tool": predicted_tool,
                    "expected_current": expected_current,
                    "predicted_current": predicted_current,
                    "tool_correct": tool_correct,
                    "parameter_correct": parameter_correct,
                    "latency_seconds": round(elapsed, 3),
                    "error": error,
                })

                status = "PASS" if parameter_correct else "FAIL"
                print(f"{status}: {instruction}")

    output = ROOT / "tests" / "llm_accuracy_results.csv"

    with open(output, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    total = len(results)

    tool_accuracy = (
        sum(r["tool_correct"] for r in results) / total * 100
    )

    full_accuracy = (
        sum(r["parameter_correct"] for r in results) / total * 100
    )

    average_latency = (
        sum(r["latency_seconds"] for r in results) / total
    )

    print("\n--- EVALUATION RESULTS ---")
    print(f"Total tests: {total}")
    print(f"Tool selection accuracy: {tool_accuracy:.2f}%")
    print(f"Full command accuracy: {full_accuracy:.2f}%")
    print(f"Average LLM latency: {average_latency:.3f} seconds")
    print(f"Results saved to: {output}")


if __name__ == "__main__":
    asyncio.run(main())
