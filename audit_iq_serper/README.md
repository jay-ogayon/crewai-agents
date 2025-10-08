# AuditIQ SERPER Tool

A CrewAI tool that provides web search capabilities using the SERPER API. This tool is based on the SERPER search implementation from the AuditIQ project's `audit_researcher` agent.

## Features

- **Web Search**: Search the web for current audit regulations, compliance requirements, and industry trends
- **SERPER API Integration**: Uses the powerful SERPER API for high-quality search results
- **Audit-Focused**: Designed specifically for audit and compliance research
- **Error Handling**: Robust error handling with timeout protection
- **Configurable Results**: Adjustable number of search results (default: 5)

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling.

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

2. Get your SERPER API key from [serper.dev](https://serper.dev/)

3. Add your API key to the `.env` file:
```
SERPER_API_KEY=your_serper_api_key_here
```

## Usage

### In a CrewAI Project

```python
from audit_iq_serper import AuditIqSerper

# Create an agent with the SERPER search tool
agent = Agent(
    role="Audit Researcher",
    goal="Conduct comprehensive web research on audit regulations",
    backstory="You are a skilled research analyst specializing in audit topics.",
    tools=[AuditIqSerper()],
    verbose=True
)
```

### Standalone Usage

```python
from audit_iq_serper import AuditIqSerper

# Initialize the tool
serper_tool = AuditIqSerper()

# Perform a search
result = serper_tool._run(
    query="latest audit regulations 2024",
    num_results=5
)

print(result)
```

## Tool Parameters

- `query` (required): Web search query for current audit and compliance information
- `num_results` (optional): Number of search results to return (default: 5)

## Error Handling

The tool includes comprehensive error handling for:
- Missing API key configuration
- Network connection issues
- API timeout (15 seconds)
- HTTP errors
- Rate limiting

## Based on AuditIQ Implementation

This tool is based on the `SerperSearchTool` implementation from the AuditIQ project, specifically used by the `audit_researcher` agent. It maintains the same functionality and error handling patterns for consistency.

## Publishing

To publish this tool for others to use:

```bash
crewai tool publish audit_iq_serper
```

Others can install your tool with:

```bash
crewai tool install audit_iq_serper
```

## Support

For support, questions, or feedback:

- Visit the [CrewAI documentation](https://docs.crewai.com)
- Check the [CrewAI GitHub repository](https://github.com/joaomdmoura/crewai)
- Join the [CrewAI Discord](https://discord.com/invite/X4JWnZnxPb)
