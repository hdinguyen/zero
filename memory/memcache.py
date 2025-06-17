import redis
from typing import Optional
import json

class MemCache:
    def __init__(self):
        self.redis_client = redis.Redis(host="localhost", port=9379, decode_responses=True)

    def get_summary(self, thread_id: str) -> Optional[dict]:
        try:
            data = self.redis_client.hgetall(f"{thread_id}")
            if not data:
                return None
            return {
                'summary': data.get('summary', ''),
                'last_updated': data.get('last_updated', ''),
                'message_count': data.get('message_count', '0'),
                'last_conversation': data.get('last_conversation', '')
            }
        except Exception as e:
            print(f"Error retrieving summary: {e}")
            return None
    
    def set_summary(self, thread_id: str, summary: str, last_updated: int, last_conversation: dict, message_count: int):
        try:
            self.redis_client.hset(f"{thread_id}", mapping={
                'summary': summary,
                'last_updated': last_updated,
                'message_count': message_count,
                'last_conversation': json.dumps(last_conversation)
            })
        except Exception as e:
            print(f"Error setting summary: {e}")