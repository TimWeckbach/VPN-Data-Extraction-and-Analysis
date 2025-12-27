from mcp.server.fastmcp import FastMCP
import datetime

mcp = FastMCP("TimeServer")

@mcp.tool()
def get_current_time():
    """Returns the current local time in ISO format."""
    return datetime.datetime.now().astimezone().isoformat()

if __name__ == "__main__":
    mcp.run()
