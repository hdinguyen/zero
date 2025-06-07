import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import asyncio
from agent.tool_agent import ToolAgent
import dspy
from utils import logger

class PlanModel(BaseModel):
    plan_id: int = Field(description="The sequence number indicating the order of execution for this agent in the plan")
    plan_dependency: list[int] = Field(description="The sequence number of the plan that this plan depends on, if the plan not depends on any other plan, the value is an empty list")
    agent_name: str = Field(description="The unique identifier/name of the agent that will execute this step")
    agent_instruction: str = Field(description="The specific instruction or task that this agent needs to perform, this instruction is used to execute the task")

class AgentToolManagerSignature(dspy.Signature):
    question: str = dspy.InputField(description="Question to the agent")
    agent_description: str = dspy.InputField(description="Description of the agent")
    execution_plan: list[PlanModel] = dspy.OutputField(description="List of objects containing agent name and input for each agent to execute the task at agent task level")

class AgentToolManager(dspy.Module):
    def __init__(self, mcp_config:Optional[Dict[str, Any]] = None):
        self.lm = dspy.LM(
            model="openrouter/deepseek/deepseek-chat-v3-0324:free",
            api_key=os.getenv("OR_KEY")
        )
        self._agents: Dict[str, ToolAgent] = {}
        self._lock = asyncio.Lock()
        self._current_config: Optional[Dict[str, Any]] = mcp_config
        self.description = ""
        self._coodinator = dspy.ChainOfThought(AgentToolManagerSignature)
        self._coodinator.set_lm(self.lm)
    
    async def load_agent(self):
        """Create agent for each MCP tool collection"""
        if self._current_config is None:
            raise ValueError("MCP config is not set")
        logger.info("Closing all agents if any")
        await self.close_agent()

        logger.info("Loading new agent")
        
        async with self._lock:
            for k,v in self._current_config.items():
                self._agents[k] = ToolAgent(mcp_config=v, agent_name=k, lm=self.lm)
                await self._agents[k].connect()
                self.description += f"Agent {k} is loaded with description:\n===\n{self._agents[k].agent_description}\n\n"
    
    async def close_agent(self):
        """Close the current agent and cleanup resources"""
        async with self._lock:
            for key, agent in self._agents.items():
                logger.info(f"Closing agent {key}")
                await agent.__aexit__(None, None, None)
            self._agents = {}
            self.description = ""
    
    def is_agent_ready(self) -> bool:
        """Check if agent is ready"""
        return self.description != ""
    
    async def acall(self, question:str):
        logger.debug(f"agent network: {self.description}")
        execution_plan = await self._coodinator.acall(question=question, agent_description=self.description)
        

        return execution_plan