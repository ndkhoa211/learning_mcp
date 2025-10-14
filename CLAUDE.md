# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Research Assistant MCP (Model Context Protocol) server that provides semantic search and storage capabilities using ChromaDB and Ollama embeddings. The server exposes 5 tools through the FastMCP framework for managing research data across different topics.

## Architecture

### Core Components

**server.py** - Main MCP server implementation
- FastMCP server that exposes 5 research management tools
- Uses ChromaDB for vector storage with topic-based organization
- Integrates Ollama embeddings (nomic-embed-text model)
- Implements content deduplication using MD5 hashing
- Each topic creates a separate ChromaDB collection and directory

**Key Configuration**:
- ChromaDB storage: `research_chroma_dbs/` directory (auto-created)
- Ollama endpoint: `http://localhost:11434`
- Embedding model: `nomic-embed-text`
- Topics create isolated databases in `research_chroma_dbs/{topic}/`

### Data Storage Structure

```
research_chroma_dbs/
├── {topic_name}/
│   ├── content_hashes.json      # MD5 hashes for deduplication
│   └── [ChromaDB files]          # Vector database files
```

### Tool Functions

1. **save_research_data** - Saves content to vector DB with deduplication
2. **search_research_data** - Semantic similarity search within a topic
3. **list_research_topics** - Lists all topics with document counts
4. **delete_research_topic** - Removes topic and all its data
5. **get_topic_info** - Detailed topic information including paths and counts

## Development Setup

### Prerequisites
- Python 3.12+
- Ollama running locally with `nomic-embed-text` model available
- uv package manager

### Install Dependencies
```bash
uv sync
```

### Running the MCP Server
```bash
uv run server.py
```

The server runs with stdio transport for MCP communication.

### Testing with Claude Desktop

1. Configuration file location: `%APPDATA%\Claude\claude_desktop_config.json`
2. Use the provided `claude_desktop_conf.json` as reference
3. Restart Claude Desktop after config changes
4. Ensure Ollama is running before connecting

## Important Implementation Details

### Content Deduplication
- Uses MD5 hashing of content to prevent duplicate storage
- Hashes stored in `content_hashes.json` per topic
- New content checked against existing hashes before saving

### Vector Store Management
- Each topic gets its own ChromaDB collection: `research_on_{topic}`
- Collections persist in separate directories
- Documents include metadata: topic, content_hash, doc_index

### Error Handling
- All tools return string responses (success or error messages)
- Failed operations include descriptive error messages
- Missing topics handled gracefully with informative responses

## Working with This Codebase

### Adding New Tools
- Use `@mcp.tool()` decorator on functions
- Return string messages (MCP tools communicate via strings)
- Include comprehensive docstrings with Args descriptions
- Handle exceptions and return user-friendly error messages

### Modifying Storage
- ChromaDB path: `CHROMA_DB_ROOT` constant
- Embedding configuration: `embeddings` object (lines 36-39)
- Utility functions (lines 44-83) handle storage operations

### Dependencies
Key packages:
- `fastmcp` - MCP server framework
- `langchain-chroma` - ChromaDB integration
- `langchain-ollama` - Ollama embeddings
- `langchain-core` - Document abstractions
