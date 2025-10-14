# simple_test.py - Simple test to check MCP client basics
import asyncio
import json
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient

current_dir = Path.cwd()

# Simplified config - only test research-assistant server
mcp_config = {
    "research-assistant": {
        "command": "uv",
        "args": [
            "--directory",
            str(current_dir),
            "run",
            "server.py"
        ],
        "transport": "stdio",
        "env": {
            "OLLAMA_BASE_URL": "http://localhost:11434",
            "EMBED_MODEL": "nomic-embed-text"
        }
    }
}

async def simple_test():
    print("Creating MultiServerMCPClient...")
    client = MultiServerMCPClient(mcp_config)

    print("Calling get_tools() - this may take a moment...")
    try:
        tools = await client.get_tools()
        print(f"\n[SUCCESS] Loaded {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_test())
