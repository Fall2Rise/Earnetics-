from fastmcp import FastMCP
import os
import yaml
import json

mcp = FastMCP("Earnetics-Nexus")

# Update these paths if your agents.yaml is in a different spot
AGENTS_CONFIG = "../src/config/agents.yaml"
WEALTH_COVENANT = "../wealth_covenant.json"

@mcp.tool()
def list_all_agents() -> str:
    """Scans the agents.yaml file and returns a list of all 51 agents."""
    try:
        with open(AGENTS_CONFIG, "r") as f:
            config = yaml.safe_load(f)
            agents = config.get("agents", {})
            return f"Found {len(agents)} agents: " + ", ".join(agents.keys())
    except FileNotFoundError:
        return "Error: agents.yaml not found."

@mcp.tool()
def check_wealth_covenant() -> str:
    """Reads the Wealth Covenant status."""
    try:
        with open(WEALTH_COVENANT, "r") as f:
            data = json.load(f)
            status = data.get("safe_mode", True)
            return f"Wealth Covenant: Safe Mode is {'ON' if status else 'OFF'}."
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
