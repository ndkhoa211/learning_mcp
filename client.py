# client.py - Research Assistant with Firecrawl and LangGraph


# ----- IMPORTS -----
import os
import json
import asyncio # for async connection between clients and servers
from typing import List, Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv


# ----- LANGCHAIN/LANGGRAPH IMPORTS -----
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages # for state management of our graph
from langgraph.checkpoint.memory import MemorySaver # for in-memory checkpoint
from langchain_mcp_adapters.client import MultiServerMCPClient


# ----- LOAD API KEYS -----
load_dotenv()
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")


current_dir = os.path.dirname(os.path.abspath(__file__))
# ----- MULTI-SERVER MCP CLIENT CONFIGURATION
mcp_config_path = os.path.join(current_dir, "mcp.json")
mcp_json = json.load(open(mcp_config_path, 'r'))
mcp_json["firecrawl_server"]["env"] = {
    "FIRECRAWL_API_KEY": FIRECRAWL_API_KEY
}


# ----- MULTI-SERVER MCP CLIENT INITIALIZATION
client = MultiServerMCPClient(mcp_json)




async def create_research_agent():
    """Create a LangGraph agent with research and web crawling capabilities."""

    # Initialize LLM
    llm = ChatOllama(model="qwen3:1.7b", base_url="http://localhost:11434/")

    # Get tools from all MCP servers
    tools = await client.get_tools()
    llm_with_tools = llm.bind_tools(tools)

    # System prompt for research assistant
    system_message = """You are an advanced research assistant with access to web crawling and knowledge storage capabilities.

                        Your abilities:
                        1. **Web Research**: Use Firecrawl tools to scrape and analyze web content
                        2. **Knowledge Storage**: Save important research findings to vector databases organized by topic
                        3. **Information Retrieval**: Search through previously saved research using semantic similarity
                        4. **Research Management**: Organize and manage research topics

                        When conducting research:
                        - Always save important findings to the appropriate topic database
                        - Search existing knowledge first before crawling new content
                        - Provide comprehensive, well-structured responses
                        - Cite sources when possible

                        Available commands:
                        - Regular conversation for research questions
                        - The system will automatically use the best tools for your requests"""
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder("messages")
    ])

    chat_llm = prompt_template | llm_with_tools

    # Define state
    class State(TypedDict):
        messages: Annotated[List[AnyMessage], add_messages]

    # Chat node
    def chat_node(state: State) -> State:
        response = chat_llm.invoke({"messages": state["messages"]})
        return {"messages": [response]}

    # Build graph
    graph_builder = StateGraph(State)
    graph_builder.add_node("chat_node", chat_node)
    graph_builder.add_node("tool_node", ToolNode(tools=tools))

    graph_builder.add_edges(START, "chat_node")
    graph_builder.add_conditional_edges(
        "chat_node",
        tools_condition, # decide whether to use tool (return "tools") in ToolNode or not (return "__end__")
        {"tools": "tool_node", "__end__": END}
    )
    graph_builder.add_edge("tool_node", "chat_node")

    return graph_builder.compile(checkpointer=MemorySaver()), tools