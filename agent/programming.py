from typing import Any, Dict, List

import dspy

from mcp_client import MCPConnection


class ProgrammingSignature(dspy.Signature):
    """
    Answer technical programming questions with code examples and clear explanations.
    """
    question: str = dspy.InputField(description="This is the question may included code examples and clear explanations.")
    context: str = dspy.InputField(optional=True, description="This is the context of the question or summary from previous conversation.")
    answer: str = dspy.OutputField(description="This is the answer to the question may included code examples and clear explanations.")
    
class ProgrammingModule(dspy.Module):
    def __init__(self, mcp_connections: List[MCPConnection], llm: Dict[str, Any]):

        self.llm = dspy.LM(
            model=llm["model"],
            api_key=llm["api_key"],
        )

        self.tools = []

        for connection in mcp_connections:
            for tool in connection.tools:
                self.tools.append(
                    dspy.Tool.from_mcp_tool(connection.session, tool=tool)
                )

        self.agent = dspy.ReAct(
            signature=ProgrammingSignature,
            tools=self.tools
        )
        self.agent.set_lm(self.llm)

    async def aforward(self, question: str):
        return await self.agent.acall(question=question)
        