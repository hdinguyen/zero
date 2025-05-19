import asyncio
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool

from conf import config


class MCPConnection:
    def __init__(self, session: ClientSession, tools: List[Tool]):
        self.session = session
        self.tools = tools

class MCPClient:
    def __init__(self, mcp_config: dict):
        # Initialize session and client objects
        self.connections: List[MCPConnection] = []
        self.exit_stack = AsyncExitStack()
        self.mcp_servers = mcp_config

    async def connect_to_server(self):
        """Connect to an MCP server

        Args:
            mcp_server: List of MCP servers configuration
        """

        
        self.connections = []

        for k,v in self.mcp_servers['mcpServers'].items(): # type: ignore
            command = v['command']
            args = v['args']
            env = None if v['env'] is None else v['env']

            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env
            )

            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_transport
            session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

            await session.initialize()
            tools = await session.list_tools()
            self.connections.append(MCPConnection(session, tools.tools))

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
        self.connections = []
