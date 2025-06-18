import json
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, WebSocket
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from agent.agent_tool_manager import AgentToolManager
from agent.internal_gen import extract_memory_info
from utils import logger
from datetime import datetime, timezone
#from memory.conversation import add_new_conversation, Conversation, near_text_search
from memory import Memory
from fastapi.middleware.cors import CORSMiddleware
import dspy
from utils.chatsocket import ChatSocket, ConnectionManager

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
        "BRAVE_API_KEY=BSAFvyFnGBcWt8IImCnXR_7tgwymtdr",
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

connection_manager = ConnectionManager()
agent_manager = AgentToolManager(mcp_config)
memory = Memory()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - nothing needed since agent is lazy-loaded
    await agent_manager.load_agent()
    yield
    # Shutdown
    await agent_manager.close_agent()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.post("/query/{thread_id}")
@app.post("/query")
async def query_agent(input:dict, background_tasks: BackgroundTasks, thread_id: Optional[str] = None):
    try:
      mem_summary = ""
      if thread_id is not None:
          mem_summary = json.dumps(memory.memcache.get_summary(thread_id=thread_id))
      else:
          thread_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
      
      result = await agent_manager.acall(question=input['question'], context=mem_summary)
      background_tasks.add_task(memory.adding_new_memory, user_message=input['question'], assistant_response=result, thread_id=thread_id)
      return {
          "result": result,
          "thread_id": thread_id
      }
    except Exception as e:
      logger.error(f"Error in query_agent:{e}")
      logger.debug(f"""
                   
Error in query_agent:{dspy.inspect_history(1)}
""")
      raise HTTPException(status_code=500, detail=str(e))

@app.get("/fetch_thread_ids")
async def get_thread_ids(limit: int = 10, offset: int = 0):
    return memory.conversation.get_distinct_thread_ids(limit=limit, offset=offset)

@app.get("/fetch_conversation/{thread_id}")
async def get_conversation(thread_id: str, limit: int = 50, offset: int = 0):
    return memory.conversation.load_conversation_by_thread_id(thread_id=thread_id, limit=limit, offset=offset)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent_ready": agent_manager.is_agent_ready()}

# @app.websocket("/ws/chat")
# async def websocket_endpoint(websocket: WebSocket):
#     handler = ChatSocket()
#     await handler.handle(websocket)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await connection_manager.connect(websocket)
    await connection_manager.handler(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)