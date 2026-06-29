from langchain_community.tools.tavily_search import TavilySearchResults
import os

search_tool = TavilySearchResults(
    max_results=5,
    api_key=os.getenv("TAVILY_API_KEY")
)