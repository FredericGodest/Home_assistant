import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from tools import STANDARD_TOOL_LIST
from langgraph.checkpoint.memory import InMemorySaver

def create_basic_agents(api_key: str):
    """Création d'un agent basique avec des tools basiques"""

    soul_path = os.path.join(os.path.dirname(__file__), "souls/basic_soul.md")
    with open(soul_path, encoding="utf-8") as f:
        system_prompt = f.read()

    llm = ChatOpenAI(
        model="gpt-5.4-nano",
        api_key=os.getenv("API_KEY_MAMMOUTH"),
        base_url="https://api.mammouth.ai/v1",
        temperature=0.2,
        timeout=30,
    )

    agent = create_agent(
        llm, 
        tools=STANDARD_TOOL_LIST,
        system_prompt=system_prompt,
        checkpointer=InMemorySaver(),
        name="agent basique")

    return agent