# AuditIQ AUDIT RAG Tool

A CrewAI tool that provides access to audit methodology knowledge base using Azure Cognitive Search. This tool is based on the `AuditSearchTool` implementation from the AuditIQ project's `audit_rag_agent`.

## Features

- **Audit Methodology Search**: Search audit methodologies, techniques, procedures, and best practices
- **Azure Cognitive Search Integration**: Uses Azure Search with the hardcoded "audit-iq" index
- **Semantic Search**: AI-powered relevance scoring for audit-specific content
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
AzureSearchEnpoint=https://your-search-service.search.windows.net
AzureSearchAdminKey=your_azure_search_admin_key_here
```

**Note**: This tool is hardcoded to use the "audit-iq" index for audit methodology content.

## Usage

### In a CrewAI Project

```python
from audit_iq_audit_rag import AuditIqAuditRag

# Create an agent with the AUDIT RAG search tool
agent = Agent(
    role="Audit Methodology Specialist",
    goal="Search and retrieve audit methodology and best practices information",
    backstory="You are an expert at navigating audit methodology knowledge bases.",
    tools=[AuditIqAuditRag()],
    verbose=True
)
```

### Standalone Usage

```python
from audit_iq_audit_rag import AuditIqAuditRag

# Initialize the tool
audit_tool = AuditIqAuditRag()

# Perform a search
result = audit_tool._run(
    query="internal controls testing procedures",
    top=3
)

print(result)
```

## Tool Parameters

- `query` (required): Search query for audit methodology knowledge base
- `top` (optional): Number of search results to return (default: 5)

## Error Handling

The tool includes comprehensive error handling for:
- Missing Azure Search credentials
- Network connection issues
- Search timeout (30 seconds)
- Azure Search service errors
- Invalid search queries

## Based on AuditIQ Implementation

This tool is based on the `AuditSearchTool` implementation from the AuditIQ project, specifically used by the `audit_rag_agent`. It maintains the same functionality and error handling patterns for consistency.

Key features from the original implementation:
- Hardcoded "audit-iq" index usage
- 30-second timeout protection  
- Comprehensive error handling
- Formatted result output with titles, scores, and content previews

## Publishing

To publish this tool for others to use:

```bash
crewai tool publish audit_iq_audit_rag
```

Others can install your tool with:

```bash
crewai tool install audit_iq_audit_rag
```

## Support

For support, questions, or feedback:

- Visit the [CrewAI documentation](https://docs.crewai.com)
- Check the [CrewAI GitHub repository](https://github.com/joaomdmoura/crewai)
- Join the [CrewAI Discord](https://discord.com/invite/X4JWnZnxPb)