import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

import dspy
import uvicorn
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from agent import GeneralAgent
from conf import config
from external.getpantry import get_pantry_data_by_basket
from mcp_client.dspy_mcp import DspyMcpTool
from memory import Database, embed_text
from memory.conversation import Conversation
from memory.debug import Debug


async def init_agent():
    db = Database()

    mcp_config = get_pantry_data_by_basket(config["getpantry"]["token"],'mcp')
    dspy_mcp_tool = DspyMcpTool(mcp_config)
    dspy_tools = await dspy_mcp_tool.get_dspy_tools()

    llm = dspy.LM(
        model=config["llm"]["model"],
        api_key=config["llm"]["api_key"]
    )
    
    agent = GeneralAgent(llm, dspy_tools)
    await agent.start()
    return agent, dspy_mcp_tool, db
    

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application is starting up...")
    app.state.agent, app.state.dspy_mcp_tool, app.state.db = await init_agent()
    
    yield
    
    # Shutdown code
    print("Application is shutting down...")
    await app.state.dspy_mcp_tool.cleanup()
    app.state.db.close()

app = FastAPI(lifespan=lifespan)

@app.post("/ask")
async def ask(ask: dict):
    question = ask["question"]
    if question.strip() == "":
        return {"error": "Question is required"}
    
    embedding_question = embed_text(question)
    similar_conversations = app.state.db.retrieve_similar_conversations(embedding_question)
    
    response = await app.state.agent.acall(question, similar_conversations)
    embedding = embed_text(f"{question}\n{response.answer}")    

    conversation_id = app.state.db.add_row(Conversation(
        created_at=datetime.now(),
        question=question,
        answer=response.answer,
        embedding=embedding
    ))

    app.state.db.add_row(Debug(
        created_at=datetime.now(),
        conversation_id=conversation_id,
        reasoning=response.reasoning,
        trajectory=str(response.trajectory),
        human_feedback=""
    ))
    return {"answer": response.answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)