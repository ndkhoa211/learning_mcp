# ----- IMPORTS -----
import streamlit as st
import asyncio


from langchain_ollama import ChatOllama


# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools


# for langchain & langgraph v0.3
from langgraph.prebuilt import create_react_agent as create_agent
# for langchain v1
# from langchain.agents import create_agent


# ----- STDIO SERVER PARAMETERS INITIALIZATION -----
server_params = StdioServerParameters(
    command="uv",
    args=[
        "--directory",
        "C:\\Users\\user\\Desktop\\learning_mcp",
        "run",
        "server.py"
        ]
)




# ----- STREAMLIT UI IMPLEMENTATION -----
st.title(":brain: Streamlit Application for MCP RAG with Ollama's LLM")
st.write("Github Repository: https://github.com/ndkhoa211/learning_mcp/tree/8_rag_langchain")

model = ChatOllama(model="qwen3:1.7b", base_url="http://localhost:11434/")

# INITIALIZE CHAT HISTORY
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

with st.form("llm-chat-form"):
    text = st.text_area("Enter your query here.")
    submit = st.form_submit_button("Submit")
    new_chat = st.form_submit_button("New Chat")
    debug_info = st.checkbox("Show Debug Info")


async def generate_response_async(user_message, show_debug=False):
    """Async function to generate response using MCP tools"""
    try:
        # create connection over stdio to the MCP server
        # `await stdio_client(...)` returns 2 async streams: (read, write)
        async with stdio_client(server_params) as (read, write):
            # ClientSession wraps those raw streams in a structured message protocol (JSON-RPC over MCP)
            # it handles: encode/decode messages, send requests & receive response, keep track of active method calls
            # turns (read, write) into a fully functional session object we can interact with
            async with ClientSession(read, write) as session:
                # Initialize the connection: verify protocol version compability, announce available capabilities, prepare for subsequent tool loading
                await session.initialize()

                # fetch 4 tools from MCP server
                tools = await load_mcp_tools(session)

                # Create and run the agent
                agent = create_agent(model, tools)
                agent_response = await agent.ainvoke({
                    "messages": [{"role": "user", "content": user_message}]
                })

                if show_debug:
                    st.write("### Debug - Agent Response")
                    st.write(agent_response)

                response = agent_response.get("messages")[-1].content
                return response
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        st.error(f"Error in async function: {str(e)}")
        if show_debug:
            st.code(error_details)
        raise

# This function bridges async and sync worlds because Streanlit is synchronous but MCP requires async operations
def generate_response(user_message, show_debug=False):
    """Synchronous wrapper for the async function"""
    # Create a new event loop for this execution
    loop = asyncio.new_event_loop()
    # Set it as the current event loop for the current thread (optional, but often needed)
    asyncio.set_event_loop(loop)
    try:
        # `run_until_complete()` runs the async function until finishes
        # execute the entire async operation within the new loop
        return loop.run_until_complete(generate_response_async(user_message, show_debug))
    finally:
        # Clean up the loop
        try:
            # Cancel all pending tasks
            pending = asyncio.all_tasks(loop) # get all currently running tasks in the loop
            for task in pending:
                task.cancel()
            # Run the loop once more to process cancellations
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception:
            pass
        finally:
            # close the loop when done
            loop.close()

# Handle form submission
if submit and text:
    with st.spinner("Generating response..."):
        try:
            response = generate_response(text, debug_info)
            st.session_state["chat_history"].append(
                {"user": text, "assistant": response}
                )
            st.success("Response generated successfully!")
        except Exception as e:
            import traceback
            st.error(f"Error generating response: {str(e)}")
            if debug_info:
                st.code(traceback.format_exc())

# Handle new chat button
if new_chat:
    st.session_state["chat_history"] = []
    st.success("Chat history cleared!")

# Display chat history
if st.session_state["chat_history"]:
    st.write("## Chat History")
    for chat in reversed(st.session_state["chat_history"]):
        st.write(f"**:adult: User**: {chat["user"]}")
        st.write(f"**:brain: Assistant**: {chat["assistant"]}")
        st.write("---")



# Flow Diagram
# User submits query in Streamlit
#          ↓
# generate_response() (sync)
#          ↓
# [Creates new event loop]
#          ↓
# generate_response_async() (async)
#          ↓
# [Connects to MCP server via stdio]
#          ↓
# [Loads tools from server.py]
#          ↓
# [Creates ReAct agent with LLM + tools]
#          ↓
# [Agent processes query, may call tools]
#          ↓
# [Returns response]
#          ↓
# [Cleanup event loop]
#          ↓
# Display response in Streamlit