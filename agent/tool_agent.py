import dspy
from typing import Optional, List

#MCP
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool
from contextlib import AsyncExitStack

from agent.internal_gen import generate_agent_description
from utils import logger

class ToolAgent(dspy.Module):
    def __init__(self, mcp_config:dict, agent_name:str, lm:dspy.LM):
        self.lm = lm
        self.agent_name = ""
        self.agent_description = ""
        self.client = MCPClient()
        self.reAct: Optional[dspy.ReAct] = None
        self.mcp_config = mcp_config
    
    async def acall(self, *args):
        if self.reAct is None:
            raise ValueError("ReAct is not connected")
        if len(args) == 0:
            raise ValueError("No input provided")
        input = args[0]
        context = args[1] if len(args) > 1 else ""
        return await self.reAct.acall(input=input, context=context)
    
    async def connect(self):
        tool_information = await self.client.connect(self.mcp_config)
        self.agent_description = generate_agent_description(information=tool_information)

        dspy_tools = await self.client.convert_to_dspy()
        self.reAct = dspy.ReAct("input, context -> result", tools=dspy_tools)
        self.reAct.set_lm(self.lm)

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    def get_tools_information(self, tools:List[Tool]):
        tools_information = []
        for tool in tools:
            tools_information.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema,
                "annotations": tool.annotations
            })
        return str(tools_information)

    async def connect(self, mcp_config:dict):
        server_param = StdioServerParameters(
            command=mcp_config['command'],
            args=mcp_config['args'],
            env=None if 'env' not in mcp_config.keys() else mcp_config['env']
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_param))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()
        response = await self.session.list_tools()
        tools_information = self.get_tools_information(response.tools)
        return tools_information

    async def convert_to_dspy(self):
        dspy_tools = []
        if self.session is None:
            raise ValueError("Session is not connected")
        response = await self.session.list_tools()
        for tool in response.tools:
            dspy_tool = dspy.Tool.from_mcp_tool(self.session, tool)
            dspy_tools.append(dspy_tool)
        return dspy_tools

    async def disconnect(self):
        """Properly cleanup all async contexts"""
        try:
            await self.exit_stack.aclose()
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
        finally:
            self.session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
