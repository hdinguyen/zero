from fastapi import FastAPI, Depends, HTTPException
from typing import Dict, Any
from contextlib import asynccontextmanager
from agent.agent_tool_manager import AgentToolManager
from utils import logger
from datetime import datetime, timezone
from memory.conversation import add_new_conversation, Conversation, near_text_search

mcp_config = {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--headless"
      ]
    },
    "brave-search": {
      "command": "env",
      "args": [
        "BRAVE_API_KEY=xxx",
        "npx",
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ]
    },
    "duckduckgo-search": {
      "command": "uvx",
      "args": ["duckduckgo-mcp-server"]
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
        response = near_text_search(input['question'])
        result = await agent_manager.acall(input['question'])
        add_new_conversation(Conversation(
            thread_id=input['thread_id'],
            timestamp=datetime.now(timezone.utc),
            user_message=input['question'],
            assistant_response=result,
            category="question",
            tags=["question"]
        ))
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent_ready": agent_manager.is_agent_ready()}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)