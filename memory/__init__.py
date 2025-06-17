import dspy
from memory.conversation import ConversationManager, Conversation
from memory.memcache import MemCache
from typing import Optional
from conf import config
from datetime import datetime, timezone

class MemorySignature(dspy.Signature):
    """Extract memory information from the conversation with purpose of context for continue conversation"""
    user_message: str = dspy.InputField(description="The input/question from user")
    assistant_response: str = dspy.InputField(description="The assistant response to the user message")
    memory: str = dspy.InputField(description="The memory of the conversation above this question and answer")
    summary: str = dspy.OutputField(description="The information finally extracted combined with the memory that consistenct with the whole conversation")

class Memory:
    def __init__(self):
        self.memcache = MemCache()
        self.conversation = ConversationManager()
        lm = dspy.LM(
            model=config.get("memory", "model"),
            api_key=config.get("memory", "api_key")
        )
        self.cot = dspy.ChainOfThought(MemorySignature)
        self.cot.set_lm(lm)

    def get_summary(self, thread_id: str) -> Optional[dict]:
        return self.memcache.get_summary(thread_id)
    
    def adding_new_memory(self, user_message: str, assistant_response: str, thread_id: str):
        current_mem = self.memcache.get_summary(thread_id=thread_id)
        if current_mem is None:
            current_mem = {
                "memory": "",
                "message_count": 0
            }
        mem_summary = current_mem.get("memory", "") if current_mem else ""
        summary = self.cot(user_message=user_message, assistant_response=assistant_response, memory=mem_summary)
        current_time = datetime.now(timezone.utc)
        self.memcache.set_summary(thread_id=thread_id, summary=summary.summary, last_updated=int(current_time.timestamp()), last_conversation={
            "user_message": user_message,
            "assistant_response": assistant_response
        }, message_count=int(current_mem.get("message_count", 0)) + 1)
        self.conversation.add_new_conversation(Conversation(
            thread_id=thread_id,
            timestamp=current_time,
            user_message=user_message,
            assistant_response=assistant_response,
            category="",
            tags=[],
            rate=None
        ))