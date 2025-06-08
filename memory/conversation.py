'''
{
    "class": "Conversation",
    "description": "Personal assistant conversation history with threading",
    "properties": [
      {
        "name": "threadId",
        "dataType": ["text"],
        "description": "Unique identifier to group related conversations"
      },
      {
        "name": "timestamp",
        "dataType": ["date"],
        "description": "When the conversation occurred"
      },
      {
        "name": "userMessage",
        "dataType": ["text"],
        "description": "User input message"
      },
      {
        "name": "assistantResponse",
        "dataType": ["text"],
        "description": "Assistant response"
      },
      {
        "name": "category",
        "dataType": ["text"],
        "description": "Conversation category (e.g., scheduling, reminder, query)"
      },
      {
        "name": "tags",
        "dataType": ["text[]"],
        "description": "Tags for categorization"
      },
      {
        "name": "rate",
        "dataType": ["boolean"],
        "description": "user satify with the response or not"
      }
    ]
  }
'''

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from memory import client

class Conversation(BaseModel):
    thread_id: str = Field(description="Unique identifier to group related conversations")
    timestamp: datetime = Field(description="When the conversation occurred")
    user_message: str = Field(description="User input message")
    assistant_response: str = Field(description="Assistant response")
    category: str = Field(description="Conversation category (e.g., scheduling, reminder, query)")
    tags: list[str] = Field(description="Tags for categorization")
    rate: Optional[bool] = Field(default=None, description="user satify with the response or not")  # Made optional

class ConversationModel(BaseModel):
    conversation: list[Conversation] = Field(description="List of conversations")

conversation_schema = client.collections.get("Conversation")

def add_new_conversation(conversation: Conversation):
    conversation_schema.data.insert({
        "thread_id": conversation.thread_id,
        "timestamp": conversation.timestamp,
        "user_message": conversation.user_message,
        "assistant_response": conversation.assistant_response,
        "category": conversation.category,
        "tags": conversation.tags,
        "rate": conversation.rate
    })

def near_text_search(query: str, limit: int = 5):
    return conversation_schema.generate.near_text(
        query=query,
        limit=limit
    )

# def get_conversation_by_thread_id(thread_id: str):
#     return client.query.get(
#         class_name="Conversation",
#         properties=["thread_id", "timestamp", "user_message", "assistant_response", "category", "tags", "rate"]
#     ).with_near_text(
#         query=thread_id
#     ).with_limit(1).do()