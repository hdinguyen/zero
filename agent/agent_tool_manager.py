import os
from typing import Optional, Dict, Any
import dspy.primitives
from pydantic import BaseModel, Field
import asyncio
from agent.tool_agent import ToolAgent
import dspy
from utils import logger

class PlanModel(BaseModel):
    plan_id: int = Field(description="The sequence number indicating the order of execution for this agent in the plan")
    agent_name: str = Field(description="The unique identifier/name of the agent that will execute this step, agent name must be one of the following: brave-search, duckduckgo-search")
    agent_input: str = Field(description="The input to the agent that leads agent to return the result as target")
    agent_context: str = Field(description="The context of the agent that leads agent to return the result as target")
    agent_target: str = Field(description="The specific target of the agent to execute the task")

class AgentToolManagerSignature(dspy.Signature):
    question: str = dspy.InputField(description="High level question or input from user")
    agent_description: str = dspy.InputField(description="Description of the agent")
    execution_plan: list[PlanModel] = dspy.OutputField(description="List of objects containing agent name and input for each agent to execute the task at agent task level")

class AgentToolManagerConclusion(dspy.Signature):
    original_question: str = dspy.InputField(description="The original question or input from user")
    data_collection: list[dict] = dspy.InputField(description="List of data response from each agent")
    final_answer: str = dspy.OutputField(description="The conclusion of the agent tool manager, must short but not missing any important information")

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
        self._conclusion = dspy.ChainOfThought(AgentToolManagerConclusion)
        self._conclusion.set_lm(self.lm)
    
    async def load_agent(self):
        """Create agent for each MCP tool collection"""
        if self._current_config is None:
            raise ValueError("MCP config is not set")
        logger.info("Closing all agents if any")
        await self.close_agent()

        logger.info("Loading new agent")
        
        async with self._lock:
            for k,v in self._current_config.items():
                try:
                    self._agents[k] = ToolAgent(mcp_config=v, agent_name=k, lm=self.lm)
                    await asyncio.wait_for(self._agents[k].connect(), timeout=5)
                    self.description += f"""
<agent>
<name>{k}</name>
<capabilities>{self._agents[k].agent_description}</capabilities>
</agent>"""
                except asyncio.TimeoutError:
                    logger.error(f"Timeout during setup MCP: {k}")
                    if k in self._agents:
                        await self._agents[k].__aexit__(None, None, None)
                        del self._agents[k]
                    continue
                except Exception as e:
                    logger.error(f"Error during setup MCP: {k} {e}")
                    if k in self._agents:
                        await self._agents[k].__aexit__(None, None, None)
                        del self._agents[k]
                    continue
    
    async def close_agent(self):
        """Close the current agent and cleanup resources"""
        async with self._lock:
            for key, agent in self._agents.items():
                logger.info(f"Closing agent {key}")
                await agent.__aexit__(None, None, None)
            self._agents = {}
            self.description = ""
    
    def is_agent_ready(self) -> list[str]:
        """Check if agent is ready"""
        return list(self._agents.keys())
    
    async def acall(self, question:str):
        logger.debug(f"agent network: {self.description}")
        plan = await self._coodinator.acall(question=question, agent_description=self.description)
        data_collection = await self.execute_plans_parallel(plan.execution_plan)
        conclusion = await self._conclusion.acall(original_question=question, data_collection=data_collection)
        return conclusion.final_answer

    async def execute_plans_parallel(self, execution_plan:list[PlanModel]):
        # Create all tasks
        tasks = []
        for plan in execution_plan:
            agent = self._agents[plan.agent_name]
            task = agent.acall(plan.agent_input, plan.agent_target, plan.agent_context)
            tasks.append(task)
        
        # Execute all tasks concurrently and get results in order
        data_collection = await asyncio.gather(*tasks, return_exceptions=True)

        data_collection = [
            {
                "agent_name": plan.agent_name,
                "result": response.result if isinstance(response, dspy.primitives.prediction.Prediction) else str(response)
            }
            for plan, response in zip(execution_plan, data_collection)
        ]
        return data_collection