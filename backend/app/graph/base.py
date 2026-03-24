from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
llm=ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    api_key=os.getenv("GEMINI_API_KEY")
)
search_tool=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
