import dspy

from agent.programming import ProgrammingModule
from conf import config


class GeneralAgent:
    def __init__(self, llm: dspy.LM, tools: list[dspy.Tool]):
        self.agent = None
        self.fallback_agent = None
        self.llm = llm
        self.tools = tools
    
    async def start(self):
        if self.agent is None:
            self.agent = dspy.ReAct("question, context -> answer", tools=self.tools)
            self.agent.set_lm(self.llm)
        if self.fallback_agent is None:
            self.fallback_agent = dspy.ReAct("question, context -> answer", tools=self.tools)
            self.fallback_agent.set_lm(
                dspy.LM(
                    model=config["fallback_model"]["model"],
                    api_key=config["fallback_model"]["api_key"]
                )
            )
    
    async def acall(self, message: str, context: list[str]):
        if self.agent is None:
            raise ValueError("Agent not initialized")
        try:
            r = await self.agent.acall(question=message, context=context)
            return r
        except Exception as e:
            # Ensure fallback agent is initialized
            if self.fallback_agent is None:
                await self.start()
                
            # If it's still None after initialization attempt, raise an error
            if self.fallback_agent is None:
                raise ValueError("Failed to initialize fallback agent")
                
            r = await self.fallback_agent.acall(question=message, context=context)
            return r