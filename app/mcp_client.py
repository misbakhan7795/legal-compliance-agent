import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPToolBridge:
    """Bridge for executing agent actions through Model Context Protocol."""

    def __init__(self):
        self.server_params = StdioServerParameters(
            command="python",
            args=["-m", "app.mcp_server"],
            env=None
        )

    async def execute_mcp_redline(self, audit_result_dict: dict) -> str:
        """Calls the MCP generate_redline_report tool over STDIO transport."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                result = await session.call_tool(
                    "generate_redline_report",
                    arguments={"audit_result_json": json.dumps(audit_result_dict)}
                )
                return result.content[0].text

    async def fetch_mcp_policy(self) -> str:
        """Fetches enterprise policy dynamically from the MCP resource stream."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                resource_data = await session.read_resource("policy://corporate_rules")
                return resource_data.contents[0].text