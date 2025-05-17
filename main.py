import asyncio
from conf import config
from external.getpantry import get_pantry_data_by_basket
from mcp_client import MCPClient
from agent.programming import ProgrammingModule


async def main():
    mcp_config = get_pantry_data_by_basket(config["getpantry"]["token"],'mcp')
    
    mcp_client = MCPClient(mcp_config)
    await mcp_client.connect_to_server()
    
    try:
        programmingAgent = ProgrammingModule(mcp_client.connections, config["programming"])
        r = await programmingAgent.acall("Hello")
        print(r.answer)
    finally:
        await mcp_client.cleanup()

# Run everything in a single event loop
asyncio.run(main())