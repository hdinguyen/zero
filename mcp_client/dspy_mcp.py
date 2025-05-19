import dspy

from mcp_client import MCPClient


class DspyMcpTool(MCPClient):
    def __init__(self, mcp_config: dict):
        super().__init__(mcp_config)
        self.tools = []

    async def get_dspy_tools(self):
        if len(self.tools) != len(self.mcp_servers['mcpServers']): # type: ignore
            await self.connect_to_server()

        for connection in self.connections:
            for tool in connection.tools:
                self.tools.append(
                    dspy.Tool.from_mcp_tool(connection.session, tool=tool)
                )

        return self.tools