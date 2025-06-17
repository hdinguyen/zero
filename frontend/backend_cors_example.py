# FastAPI CORS Configuration Example

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Your existing endpoints
@app.post("/query")
async def new_query(request: dict):
    question = request.get("question")
    # Your logic here
    return {
        "result": "AI response here",
        "thread_id": "20250612_145429"
    }

@app.post("/query/{thread_id}")
async def continue_query(thread_id: str, request: dict):
    question = request.get("question")
    # Your logic here
    return {
        "result": "AI response here",
        "thread_id": thread_id
    } 