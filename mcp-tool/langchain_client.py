# implement a LangChain multi-server client
# (1 server - 1 client) rule still holds
# but LangChain abstracts this so we don't need to write every client for each server
import asyncio

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

load_dotenv()


llm = ChatOpenAI()


async def main():
    client = MultiServerMCPClient( 
        {
            "math": {
                "command": "python",
                "args": ["C://Users//user//Desktop//learning_mcp//mcp-tool//servers//math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            },
        }
    )
    tools = await client.get_tools()
    agent = create_react_agent(llm, tools)
    # result = await agent.ainvoke({"messages": "What is 2 + 2?"})
    result = await agent.ainvoke({"messages": "What is the weather in New York?"})
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())