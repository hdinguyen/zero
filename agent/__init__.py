import dspy
from mcp.types import Tool
from mcp.client.session import ClientSession

from agent.programming import ProgrammingModule

# dspy_tools = []

# async def convert_mcp_tools_to_dspy_tools(session: ClientSession) -> List[dspy.Tool]:
#     if len(dspy_tools) > 0:
#         return dspy_tools
    
#     response = await session.list_tools()
#     tools = response.tools
    
#     for tool in tools:
#         dspy_tools.append(dspy.Tool.from_mcp_tool(session, tool))
#     return dspy_tools


