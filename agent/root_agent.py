import dspy
from conf import config
from pydantic import BaseModel, Field
import asyncio

class OutputSignature(dspy.Signature):
    original_question: str = dspy.InputField(description="The original question or input from user")
    data_collection: list[dict] = dspy.InputField(description="List of data response from each agent")
    output_format: str = dspy.InputField(description="The output format of the answer to user, what is the layout, sessions, should it contained table, markdown, or text, tree, ... This ")
    final_answer: str = dspy.OutputField(description="The conclusion of the agent tool manager, must short but not missing any important information")

class AgentOutputAdvisor(dspy.Signature):
    """Decision which format output is the best for the user's question, this output will be LLM instruction for the agent to generate the output"""
    question: str = dspy.InputField(description="The question from user")
    context: str = dspy.InputField(description="The context of the conversation")
    output: str = dspy.OutputField(description="The output format of the answer to user, what is the layout, sessions, should it contained table, markdown, or text, tree, ... This ")

class AgentToolManagerConclusion(dspy.Signature):
    original_question: str = dspy.InputField(description="The original question or input from user")
    data_collection: list[dict] = dspy.InputField(description="List of data response from each agent")
    output_format: str = dspy.InputField(description="The output format of the answer to user, what is the layout, sessions, should it contained table, markdown, or text, tree, ... This ")
    final_answer: str = dspy.OutputField(description="The conclusion of the agent tool manager, must short but not missing any important information")

class RootAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.output_advisor = dspy.ChainOfThought(AgentOutputAdvisor)
        self.output_conclusion = dspy.ChainOfThought(AgentToolManagerConclusion)

        self.free_lm = dspy.LM(
            model=config.get("root_agent.free","model"),
            api_key=config.get("root_agent.free","api_key")
        )
        self.paid_lm = dspy.LM(
            model=config.get("root_agent.paid","model"),
            api_key=config.get("root_agent.paid","api_key")
        )
        self.change_mode(mode="free")
    
    def change_mode(self, mode: str="free"):
        if mode == "free":
            self.output_advisor.set_lm(self.free_lm)
            self.output_conclusion.set_lm(self.free_lm)
        else:
            self.output_advisor.set_lm(self.paid_lm)
            self.output_conclusion.set_lm(self.paid_lm)
    
    async def create_plan(self, question: str, agents:str, context: str = ""):
        tasks = [
            self.output_advisor.acall(question=question, context=context),
            self.output_conclusion.acall(question=question, context=context)
        ]
        output_format, plan = await asyncio.gather(*tasks)
        return output_format.output, plan.execution_plan