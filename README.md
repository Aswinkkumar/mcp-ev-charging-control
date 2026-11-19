# MCP-Based EV Charging Control

**Ongoing Academic Research Project | Hochschule Bremen | 2026**

## Overview

This project explores how Large Language Models (LLMs) and the Model Context Protocol (MCP) can be used to control an EV charging system through natural-language commands.

The idea is to allow users to interact with a charger using simple instructions, such as "Start charging" or "Set the charging current to 12 A." I am currently developing and testing this approach with a Python-based charger simulator before exploring integration with real hardware.

## Current Implementation

The project currently includes:

- **Python EV charger simulator:** Supports charging status, start/stop operations, and current adjustment within a 6–16 A range.
- **MCP server:** Exposes four tools: `get_charger_status`, `start_charging`, `stop_charging`, and `set_charging_current`.
- **LLM integration:** Interprets natural-language commands and dynamically selects MCP tools using an OpenAI-compatible API.
- **Command validation:** Checks tool arguments and requests user confirmation before executing state-changing operations.
- **LLM evaluation:** Tests how accurately the model selects tools and identifies their parameters.

## System Workflow

```text
User Command
     |
     v
LLM Tool Selection
     |
     v
Tool & Argument Validation
     |
     v
User Confirmation (if required)
     |
     v
MCP Server
     |
     v
Python Charger Simulator
     |
     v
Execution Result
```

## Initial Evaluation

I created an evaluation script with 25 test instructions covering charging operations, status queries, current adjustments, ambiguous commands, and unsupported requests.

| Metric | Result |
|---|---|
| Test cases | 25 |
| Tool-selection accuracy | 96% (24/25) |
| Full command accuracy | 96% (24/25) |
| Average LLM response time | 1.03 seconds |

One interesting observation was that the LLM interpreted "Make charging faster" as a request to set the current to 50 A, exceeding the simulator's 16 A limit. This highlighted the importance of validating LLM-generated arguments before executing commands.

These results are from an initial evaluation of tool selection, not a complete end-to-end system benchmark.

The evaluation script and recorded results are available in `tests/test_llm_accuracy.py` and `tests/llm_accuracy_results.csv`.

## Technologies

Python · MCP · LLMs · OpenAI-compatible API · JSON Schema

## Getting Started

Install the required Python packages:

```bash
pip install mcp openai python-dotenv jsonschema
```

Configure the LLM connection using environment variables:

```env
UNIVERSITY_API_KEY=your_api_key
UNIVERSITY_API_BASE_URL=your_api_endpoint
UNIVERSITY_MODEL=your_model_name
```

Run the LLM-based MCP client from the project root:

```bash
python -m ai.dynamic_tool_client
```

The client connects to the MCP server and allows interaction with the simulated charger through natural-language commands.

## Next Steps

The project is still in development. My next steps include improving LLM command validation, expanding automated testing, and evaluating different models and instructions. I also plan to explore OCPP integration and eventually investigate how the simulator can be connected to real charging hardware.

## Project Status

**Ongoing — November 2026**

This repository documents my current implementation and research progress. The system currently operates with simulated charging hardware and is not intended for controlling a physical charger.
