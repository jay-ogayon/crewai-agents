# AuditIQ 🔍 - Intelligent Multi-Agent Audit System

Welcome to **AuditIQ**, an advanced multi-agent AI audit system powered by [crewAI](https://crewai.com). This intelligent platform combines internal knowledge base search, live web research, and document translation capabilities to provide comprehensive audit intelligence.

## 🌟 Features

- **🤖 Intelligent Query Routing**: Automatically routes queries to the most appropriate specialized agent
- **📚 Specialized RAG Search**: LLM-powered routing to specialized agents for GT Guidelines (echo index) vs. Audit Methodology (audit-iq index)
- **🌐 Live Web Research**: Real-time research on current audit regulations and industry trends
- **📄 PDF Translation**: Translate audit documents between languages while preserving formatting
- **⚡ Multi-Agent Collaboration**: Specialized agents working together for comprehensive audit intelligence

## 🏗️ Architecture

### Four Specialized Agents:

1. **🔍 Echo RAG Agent**: Searches GT Guidelines and Policy using the echo index for GT-specific content
2. **🔍 Audit RAG Agent**: Searches audit methodology using the audit-iq index for audit techniques and procedures
3. **🌐 Audit Researcher**: Conducts web research using SERPER API for current information
4. **📄 PDF Translator**: Translates documents between languages using Azure Document Translation

### Intelligent LLM-Based Workflow:
```
User Query → LLM Query Router → Specialized Agent Selection → Targeted Index Search → Expert Response
```

## 📋 Prerequisites

- Python >=3.10 <3.14
- [UV](https://docs.astral.sh/uv/) for dependency management
- Azure OpenAI account
- Azure Search service
- Azure Document Translation service
- SERPER API key

## 🚀 Installation

### 1. Install UV (if not already installed)
```bash
pip install uv
```

### 2. Install Dependencies
```bash
crewai install
# or
uv sync
```

### 3. Environment Setup
Create a `.env` file with the following variables:

```env
# Azure OpenAI Configuration
MODEL=azure/gpt-4o
AZURE_API_KEY=your_azure_openai_key
AZURE_API_BASE=https://your-openai-resource.openai.azure.com/
AZURE_API_VERSION=2025-01-01-preview

# Azure Search Configuration (Specialized RAG Agents)
AzureSearchEnpoint=https://your-search-service.search.windows.net
AzureSearchAdminKey=your_search_key
AzureSearchIndexName=audit-iq  # Audit RAG Agent - audit methodologies, procedures, techniques
AzureSearchIndexName2=echo     # Echo RAG Agent - GT Guidelines, policies, GT-specific requirements

# SERPER API Configuration (Research Agent)
SERPER_API_KEY=your_serper_api_key

# Azure Document Translation Configuration (PDF Translator Agent)
AZURE_DOCUMENT_TRANSLATION_ENDPOINT=https://your-translator.cognitiveservices.azure.com/
AZURE_DOCUMENT_TRANSLATION_KEY=your_translation_key
```

## 🎯 Usage

### Interactive Mode (Local Development)
When running locally, AuditIQ provides an interactive CLI with helpful prompts:

```bash
# Main interactive mode with intelligent routing
crewai run
# or
uv run auditiq

# Force Q&A mode (internal knowledge base only)
python3 src/auditiq/main.py qa

# Force research mode (web search only)  
python3 src/auditiq/main.py research
```

**Interactive Features:**
- 🔍 **Smart LLM Query Classification**: Automatically routes queries to appropriate specialized agents
- 📚 **Specialized Agent Routing**: Shows which agent (Echo/Audit/Research/Translate) will handle the query
- ⚡ **Agent-Specific Responses**: Tailored responses from GT Guidelines, Audit Methodology, Research, or Translation specialists
- 🌐 **Environment Detection**: Automatically adapts to cloud vs local deployment

### Command Line Usage
```bash
# Direct query execution
crewai run "What are the audit policies for financial reporting?"
uv run auditiq "How to perform risk assessment procedures?"

# Specific mode execution
python3 -c "from src.auditiq.main import run_qa; run_qa()" "SOX compliance requirements"
python3 -c "from src.auditiq.main import run_research; run_research()" "Latest 2024 audit trends"
```

## 🧪 Testing Different Agents

### 🏢 Echo RAG Agent - GT Guidelines & Policy (echo index)
Test with questions about GT company guidelines, policies, and GT-specific requirements:

```bash
# Test Echo RAG Agent (GT Guidelines & Policy)
echo "What are GT's expense approval policies?" | crewai run
echo "Show me GT company guidelines for remote work" | crewai run
echo "What are GT's compliance requirements for vendors?" | crewai run
echo "What GT procedures must I follow for procurement?" | crewai run
```

### 🔍 Audit RAG Agent - Audit Methodology (audit-iq index)  
Test with questions about audit methodologies, techniques, and procedures:

```bash
# Test Audit RAG Agent (Audit Methodologies)
echo "What audit methodology should I use for risk assessment?" | crewai run
echo "How do I perform substantive testing procedures?" | crewai run
echo "What are the best practices for audit sampling?" | crewai run
echo "What procedures should I follow for internal control testing?" | crewai run
```

**Expected Output**: Look for confirmation messages like:
- `"Searched GT Guidelines and Policy index (echo) and found X results"` for GT queries
- `"Searched audit methodology index (audit-iq) and found X results"` for audit queries

### 🌐 Audit Researcher Agent (RESEARCH) - Web Search
Test with questions requiring current external information:

```bash
# Test Research Agent
echo "What are 2025 cybersecurity audit trends?" | uv run auditiq
echo "What are the latest changes to SOX compliance requirements?" | uv run auditiq
echo "Research current ESG audit best practices" | uv run auditiq
```

### 📄 PDF Translator Agent (TRANSLATE) - Document Translation
Test with PDF translation requests:

```bash
# Test Translation Agent
echo "Translate Documents/AB8782.pdf from Greek to English" | uv run auditiq
echo "Translate my Docx file /Users/ferdinanda/Desktop/AuditIQ/auditiq/Documents/document-translation-sample.docx to German" | uv run auditiq
echo "Convert Documents/AB8782.pdf to French while preserving formatting" | uv run auditiq
```

## 🎯 LLM-Based Agent Routing System

The Query Router uses Azure OpenAI LLM to intelligently analyze queries and route them to the most appropriate specialized agent:

### 🏢 **GT Queries → Echo RAG Agent (echo index)**
GT company-specific questions about guidelines, policies, and internal procedures:

Examples:
- "What are GT's expense approval policies?"
- "Show me GT company guidelines for remote work"
- "What are GT's compliance requirements for vendors?"
- "What GT procedures must I follow for procurement?"

### 🔍 **Audit Methodology Queries → Audit RAG Agent (audit-iq index)** 
Questions about audit techniques, methodologies, and professional practices:

Examples:
- "What audit methodology should I use for risk assessment?"
- "How do I perform substantive testing procedures?"
- "What are the best practices for audit sampling?"
- "What procedures should I follow for internal control testing?"

## 📝 Sample Questions by Agent Type

### 🏢 **GT Guidelines Questions (Routes to Echo RAG Agent)**
- "What are GT's expense approval policies?"
- "Show me GT company guidelines for remote work"
- "What are GT's compliance requirements for vendors?"
- "What GT procedures must I follow for procurement?"
- "Find GT internal documentation about employee onboarding"

### 🔍 **Audit Methodology Questions (Routes to Audit RAG Agent)**
- "What audit methodology should I use for risk assessment?"
- "How do I perform substantive testing procedures?" 
- "What are the best practices for audit sampling?"
- "What procedures should I follow for internal control testing?"
- "Explain audit evidence collection techniques"

### 🔬 **Research Questions (Routes to Audit Researcher)**
- "What are the latest PCAOB audit standards for 2024?"
- "Research new SEC reporting requirements this year"
- "Find recent regulatory updates for financial institutions"
- "What are current penalties for GDPR non-compliance?"
- "Research best practices for remote audit procedures"

### 🌍 **Translation Questions (Routes to PDF Translator)**
- "Translate Documents/AB8782.pdf from Greek to English"
- "Convert the audit guidelines document to Spanish"
- "Translate the compliance report to French"
- "Change Documents/AB8782.pdf from Greek to German"

## ⚙️ Customization

### Configuration Files
- **`src/auditiq/config/agents.yaml`** - Define specialized agent roles (Echo RAG, Audit RAG, Research, Translation)
- **`src/auditiq/config/tasks.yaml`** - Configure task workflows and LLM routing expectations
- **`src/auditiq/crew.py`** - Manage agent coordination and dynamic crew creation
- **`src/auditiq/tools/custom_tool.py`** - Implement specialized search tools (EchoSearchTool, AuditSearchTool)

### Adding New Specialized Agents
1. Define new agent configuration in `agents.yaml`
2. Create corresponding specialized task in `tasks.yaml`
3. Add agent method and routing logic in `crew.py`
4. Update LLM query routing prompt to include new agent type
5. Create specialized search tool if needed

## 🔧 Development Commands

```bash
# Run the crew
crewai run
uv run auditiq

# Install dependencies
crewai install
uv sync

# Format code
uv format

# Train the crew
uv run train <iterations> <filename>

# Test crew execution
uv run test <iterations> <eval_llm>

# Replay specific task
uv run replay <task_id>
```

## 🛠️ Troubleshooting

### Common Issues

1. **Azure Search Issues**: Verify endpoint URL and API key
2. **Translation Errors**: Ensure Document Translation feature is enabled in Azure
3. **SERPER API Limits**: Check your API usage and quotas
4. **File Path Errors**: Use absolute paths for PDF translation

### Debug Mode
Enable verbose logging by setting `verbose: true` in agent configurations.

## 📊 Output

The system generates different outputs based on query type:
- **Q&A**: Comprehensive answers with document citations
- **Research**: Detailed reports with current information and sources
- **Translation**: Translated documents with preservation confirmation

Results are saved to `audit_response.md` for review.

## 🔐 Security

- Never commit API keys to version control
- Use environment variables for all sensitive configuration
- Regularly rotate API keys and access tokens
- Follow Azure security best practices for service configurations

## 📈 Performance Tips

- **Azure Search**: Optimize index for faster queries
- **SERPER API**: Use specific queries to reduce API calls
- **Document Translation**: Consider file size limits and processing time
- **Caching**: Leverage crew caching for repeated queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with provided sample queries
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, questions, or feedback:
- 📖 [CrewAI Documentation](https://docs.crewai.com)
- 🐛 [GitHub Issues](https://github.com/joaomdmoura/crewai)
- 💬 [Join Discord Community](https://discord.com/invite/X4JWnZnxPb)
- 🔗 [Chat with Docs](https://chatg.pt/DWjSBZn)

---

**Let's revolutionize audit intelligence with the power of AI! 🚀**