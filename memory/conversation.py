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
from datetime import datetime, timezone
from typing import Optional

from conf import config

import weaviate
from weaviate.classes.aggregate import GroupByAggregate
from weaviate.classes.query import Filter
from weaviate.classes.init import Auth, AdditionalConfig, Timeout


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

class ConversationManager:
    def __init__(self):
        self.client = weaviate.connect_to_custom(
          http_host=config.get("weaviate","http_url"),
          http_port=int(config.get("weaviate","http_port")),
          http_secure=bool(config.get("weaviate","http_ssl")),
          grpc_host=config.get("weaviate","grpc_url"),
          grpc_port=int(config.get("weaviate","grpc_port")),
          grpc_secure=bool(config.get("weaviate","grpc_ssl")),
          auth_credentials=Auth.api_key(config.get("weaviate","api_key")),
          additional_config=AdditionalConfig(timeout=Timeout(init=5))
        )
        self.conversation_schema = self.client.collections.get("Conversation")

    def add_new_conversation(self, conversation: Conversation):
        self.conversation_schema.data.insert({
          "threadId": conversation.thread_id,
          "timestamp": conversation.timestamp.isoformat(),
          "userMessage": conversation.user_message,
          "assistantResponse": conversation.assistant_response,
          "category": conversation.category,
          "tags": conversation.tags,
          "rate": conversation.rate
        })
    
    def near_text_search(self, query: str, limit: int = 5):
        return self.conversation_schema.query.near_text(
            query=query,
            limit=limit
        ).objects
    
    def get_distinct_thread_ids(self, limit: int = 10, offset: int = 0):
        response = self.conversation_schema.aggregate.over_all(
            group_by=GroupByAggregate(prop="threadId")
        )

        return [{"thread_id": group.grouped_by.value} for group in response.groups]
    
    def load_conversation_by_thread_id(self, thread_id: str, limit: int = 50, offset: int = 0):
        response = self.conversation_schema.query.fetch_objects(
            filters=Filter.by_property("threadId").equal(thread_id),
            limit=limit,
            offset=offset
        )

        if response and response.objects:
            convs = response.objects
            return [{"timestamp": obj.properties.get("timestamp") if isinstance(obj.properties.get("timestamp"), str) else obj.properties.get("timestamp").isoformat(),
              "user_message": obj.properties.get("userMessage"),
              "assistant_response": obj.properties.get("assistantResponse"),
              "category": obj.properties.get("category"),
              "tags": obj.properties.get("tags", []),
              "rate": obj.properties.get("rate")}
             for obj in convs]
        return []

    # def set_summary(self, conversation_id: str, summary: str, message_count: int = 0) -> bool:
    #         """Store conversation summary in Redis"""
    #         try:
    #             key = f"conv:{conversation_id}"
    #             data = {
    #                 'summary': summary,
    #                 'last_updated': int(datetime.now().timestamp()),
    #                 'message_count': message_count
    #             }
    #             self.redis_client.hset(key, mapping=data)
    #             self.redis_client.expire(key, 604800) # 7 days
    #             return True
    #         except Exception as e:
    #             print(f"Error storing summary: {e}")
    #             return False
        
    # def get_summary(self, conversation_id: str) -> Optional[dict]:
    #     """Retrieve conversation summary from Redis"""
    #     try:
    #         key = f"conv:{conversation_id}"
    #         data = self.redis_client.hgetall(key)
    #         if not data:
    #             return None
            
    #         return {
    #             'summary': data.get('summary', ''),
    #             'last_updated': int(data.get('last_updated', 0)),
    #             'message_count': int(data.get('message_count', 0))
    #         }
    #     except Exception as e:
    #         print(f"Error retrieving summary: {e}")
    #         return None

    # def update_summary(self, conversation_id: str, new_summary: str, message_count: int) -> bool:
    #     """Update existing conversation summary"""
    #     return self.set_summary(conversation_id, new_summary, message_count)

    # def delete_summary(self, conversation_id: str) -> bool:
    #     """Delete conversation summary"""
    #     try:
    #         key = f"conv:{conversation_id}"
    #         return bool(self.redis_client.delete(key))
    #     except Exception as e:
    #         print(f"Error deleting summary: {e}")
    #         return False