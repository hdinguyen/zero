from fastapi import FastAPI, Depends, HTTPException
from typing import Dict, Any
from contextlib import asynccontextmanager
from agent.agent_tool_manager import AgentToolManager
from utils import logger

mcp_config = {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest"
      ]
    },
    "Brave search": {
      "command": "env",
      "args": [
        "BRAVE_API_KEY=BSAFvyFnGBcWt8IImCnXR_7tgwymtdr",
        "npx",
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ]
    },
}

agent_manager = AgentToolManager(mcp_config)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - nothing needed since agent is lazy-loaded
    await agent_manager.load_agent()
    yield
    # Shutdown
    await agent_manager.close_agent()

app = FastAPI(lifespan=lifespan)

@app.post("/query")
async def query_agent(input:dict):
    try:
        result = await agent_manager.acall(input['instruction'])
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/reload-config")
# async def reload_agent_config(new_config: Dict[str, Any]):
#     """Reload agent with new MCP configuration"""
#     try:
#         result = await agent_manager.reload_agent(new_config)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to reload agent: {str(e)}")

# @app.get("/current-config")
# async def get_current_config():
#     """Get current agent configuration"""
#     config = agent_manager.get_current_config()
#     return {"current_config": config}

@app.get("/health")
async def health_check():
    # try:
    #     config = agent_manager.get_current_config()
    #     is_ready = agent_manager.is_agent_ready()
    #     return {
    #         "status": "healthy" if is_ready else "initializing", 
    #         "agent_ready": is_ready,
    #         "current_config": config
    #     }
    # except Exception as e:
    #     return {
    #         "status": "unhealthy", 
    #         "agent_ready": False,
    #         "error": str(e)
    #     } 
    return {"status": "healthy"}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)