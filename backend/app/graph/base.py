from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
llm=ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)
search_tool=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

