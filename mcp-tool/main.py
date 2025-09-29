import asyncio
from dotenv import load_dotenv

load_dotenv()


from mcp import (
    ClientSession, # provide the framework for a Python app to act as an MCP client
    StdioServerParameters, # a Pydantic class that specifies the parameters for the MCP server
    )
from mcp.client.stdio import stdio_client # spawn a new process, and communicate to the MCP server through stdio


from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools # load the MCP tools from the server and transform them into LangChain tools
from langgraph.prebuilt import create_react_agent


llm = ChatOpenAI()


# Pydantic object to specify the parameters for running the MCP server
stdio_server_params = StdioServerParameters(
    command="python",
    args=["C://Users//user//Desktop//learning_mcp//mcp-tool//servers//math_server.py"],
)


async def main():
    print("Hello from mcp-tool!")


if __name__ == "__main__":
    asyncio.run(main())
