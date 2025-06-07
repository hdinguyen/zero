from dspy import LM, ChainOfThought, InputField, OutputField, Signature
import os
from utils import logger


class InternalGenerator(Signature):
    information: str = InputField(description="Information about the agent capabilities can do with the tools supported")
    # instruction: str = InputField(description="Summary of the agent capabilities can do with the tools supported")
    output: str = OutputField(description="Summary of the agent capabilities can do with the tools supported, must short but not missing any important information")

lm = LM(
    model="openrouter/meta-llama/llama-3.3-8b-instruct:free",
    api_key=os.getenv("OR_KEY")
)
internal_generator = ChainOfThought(InternalGenerator)
internal_generator.set_lm(lm)

def generate_agent_description(information: str) -> str:
    try:
        return internal_generator(information=information).output
    except Exception as e:
        logger.error(f"Error generating agent description: {e}")
        return information
