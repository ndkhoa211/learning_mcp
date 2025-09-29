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
    print("Starting multi-server client...")


if __name__ == "__main__":
    asyncio.run(main())