# AuditIQ ECHO RAG Tool

A CrewAI tool that provides access to GT Guidelines and Policy knowledge base using Azure Cognitive Search. This tool is based on the `EchoSearchTool` implementation from the AuditIQ project's `echo_rag_agent`.

## Features

- **GT Guidelines Search**: Search GT company guidelines, policies, and procedures
- **Azure Cognitive Search Integration**: Uses Azure Search with the hardcoded "echo" index
- **Semantic Search**: AI-powered relevance scoring for GT-specific content
- **Timeout Protection**: 30-second timeout with robust error handling
- **Configurable Results**: Adjustable number of search results (default: 5)

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management.

First, if you haven't already, install `uv`:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

```bash
crewai install
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Configure your Azure Search credentials in the `.env` file:
```
AzureSearchEndpoint=https://your-search-service.search.windows.net
AzureSearchAdminKey=your_azure_search_admin_key_here
```

**Note**: This tool is hardcoded to use the "echo" index for GT Guidelines and Policy content.

## Usage

### In a CrewAI Project

```python
from audit_iq_echo_rag import AuditIqEchoRag

# Create an agent with the ECHO RAG search tool
agent = Agent(
    role="GT Guidelines Specialist",
    goal="Search and retrieve GT company guidelines and policy information",
    backstory="You are an expert at navigating GT company documentation.",
    tools=[AuditIqEchoRag()],
    verbose=True
)
```

### Standalone Usage

```python
from audit_iq_echo_rag import AuditIqEchoRag

# Initialize the tool
echo_tool = AuditIqEchoRag()

# Perform a search
result = echo_tool._run(
    query="GT company travel policy requirements",
    top=3
)

print(result)
```

## Tool Parameters

- `query` (required): Search query for GT Guidelines and Policy knowledge base
- `top` (optional): Number of search results to return (default: 5)

## Error Handling

The tool includes comprehensive error handling for:
- Missing Azure Search credentials
- Network connection issues
- Search timeout (30 seconds)
- Azure Search service errors
- Invalid search queries

## Based on AuditIQ Implementation

This tool is based on the `EchoSearchTool` implementation from the AuditIQ project, specifically used by the `echo_rag_agent`. It maintains the same functionality and error handling patterns for consistency.

Key features from the original implementation:
- Hardcoded "echo" index usage
- 30-second timeout protection  
- Comprehensive error handling
- Formatted result output with titles, scores, and content previews

## Publishing

To publish this tool for others to use:

```bash
crewai tool publish audit_iq_echo_rag
```

Others can install your tool with:

```bash
crewai tool install audit_iq_echo_rag
```

## Support

For support, questions, or feedback:

- Visit the [CrewAI documentation](https://docs.crewai.com)
- Check the [CrewAI GitHub repository](https://github.com/joaomdmoura/crewai)
- Join the [CrewAI Discord](https://discord.com/invite/X4JWnZnxPb)