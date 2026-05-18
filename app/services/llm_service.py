# from openai import AsyncOpenAI # Removed
from langchain_openai import ChatOpenAI # Added
from app.config.settings import settings

llm = ChatOpenAI( # Added
    model="gpt-4o-mini", # Added
    temperature=0.2 # Added
) # Added

async def ask_llm(prompt: str, config: dict = None) -> str: # Modified
    response = await llm.ainvoke(prompt, config=config) # Modified
    return response.content # Modified