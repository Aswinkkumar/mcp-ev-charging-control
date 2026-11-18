
from mcp.server.fastmcp import FastMCP

from controller.charging_controller import ChargingController

mcp = FastMCP("LIAM Wallbox Controller")

controller = ChargingController()


@mcp.tool()
def get_charger_status() -> dict:
    """Get the current simulated wallbox status."""
    return controller.get_status()


@mcp.tool()
def start_charging() -> str:
    """Start a simulated EV charging session."""
    return controller.start_charging()


@mcp.tool()
def stop_charging() -> str:
    """Stop the simulated EV charging session."""
    return controller.stop_charging()

@mcp.tool()
def set_charging_current(current: float) -> str:
    """Set simulated charging current in amperes."""
    return controller.set_current(current)





if __name__ == "__main__":
    mcp.run(transport="stdio")
