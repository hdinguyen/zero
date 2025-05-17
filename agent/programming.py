import dspy
from mcp_client import MCPConnection
from typing import List, Dict, Any

class ProgrammingSignature(dspy.Signature):
    question: str = dspy.InputField(description="The question to answer")
    answer: str = dspy.OutputField(description="The answer to the question")
    
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
        