# AuditIQ 🔍 - Intelligent Multi-Agent Audit System

Welcome to **AuditIQ**, an advanced multi-agent AI audit system powered by [crewAI](https://crewai.com). This intelligent platform combines internal knowledge base search, live web research, and document translation capabilities to provide comprehensive audit intelligence.

## 🌟 Features

- **🤖 Intelligent Query Routing**: Automatically routes queries to the most appropriate specialized agent
- **📚 Dual-Index RAG Search**: Intelligent search across specialized indexes - audit policies vs. methodologies - using Azure Cognitive Search
- **🌐 Live Web Research**: Real-time research on current audit regulations and industry trends
- **📄 PDF Translation**: Translate audit documents between languages while preserving formatting
- **⚡ Multi-Agent Collaboration**: Specialized agents working together for comprehensive audit intelligence

## 🏗️ Architecture

### Three Specialized Agents:

1. **🔍 RAG Agent**: Searches internal audit knowledge base using dual Azure Search indexes (policies vs. methodologies)
2. **🌐 Audit Researcher**: Conducts web research using SERPER API for current information
3. **📄 PDF Translator**: Translates documents between languages using Azure Document Translation

### Intelligent Workflow:
```
User Query → Query Router → Appropriate Agent → Specialized Response
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

# Azure Search Configuration (RAG Agent - Dual Index System)
AzureSearchEnpoint=https://your-search-service.search.windows.net
AzureSearchAdminKey=your_search_key
AzureSearchIndexName=audit-iq  # For audit policies, regulations, compliance
AzureSearchIndexName2=echo     # For audit methodologies, procedures, techniques

# SERPER API Configuration (Research Agent)
SERPER_API_KEY=your_serper_api_key

# Azure Document Translation Configuration (PDF Translator Agent)
AZURE_DOCUMENT_TRANSLATION_ENDPOINT=https://your-translator.cognitiveservices.azure.com/
AZURE_DOCUMENT_TRANSLATION_KEY=your_translation_key
```

## 🎯 Usage

### Quick Start
```bash
crewai run
```

### Alternative Commands
```bash
uv run auditiq
```

## 🧪 Testing Different Agents

### 🔍 RAG Agent (Q&A) - Internal Knowledge Base with Dual Index System
The system automatically selects between two specialized indexes based on query content:

#### 📋 Policy Index (audit-iq) - Audit Policies & Compliance
Test with questions about audit policies, regulations, and compliance:

```bash
# Test Policy Index (AzureSearchIndexName = audit-iq)
echo "What are the audit policies for financial reporting?" | crewai run
echo "What are compliance requirements for SOX?" | crewai run
echo "What are the regulatory requirements for auditing?" | crewai run
echo "What governance standards apply to audit committees?" | crewai run
```

#### 🔧 Methodology Index (echo) - Audit Procedures & Techniques
Test with questions about audit methodologies, procedures, and techniques:

```bash
# Test Methodology Index (AzureSearchIndexName2 = echo)
echo "What methods should I follow for testing internal controls?" | crewai run
echo "How to implement audit sampling methodology?" | crewai run
echo "What procedures should I follow for risk assessment?" | crewai run
echo "What are the standard procedures for audit evidence collection?" | crewai run
```

**Expected Output**: Look for confirmation messages like:
- `"Searched audit policy index (audit-iq) and found X results"` for policy queries
- `"Searched methodology index (echo) and found X results"` for methodology queries

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

## 🎯 Dual Index System

The RAG Agent intelligently routes queries to specialized indexes based on content analysis:

### 📋 **Policy Queries → audit-iq Index**
Keywords: `policy`, `regulation`, `compliance`, `requirement`, `governance`, `standard`, `mandate`

Examples:
- "What are the audit policies for financial reporting?"
- "What are compliance requirements for SOX?"
- "What governance standards apply to audit committees?"
- "What are the regulatory requirements for auditing?"

### 🔧 **Methodology Queries → echo Index** 
Keywords: `methodology`, `procedure`, `technique`, `how to`, `steps`, `methods for`, `standard procedures`

Examples:
- "What methods should I follow for testing internal controls?"
- "How to implement audit sampling methodology?"
- "What procedures should I follow for risk assessment?"
- "What are the standard procedures for audit evidence collection?"

## 📝 Sample Questions by Agent Type

### 📚 **Q&A Questions (Routes to RAG Agent with Smart Index Selection)**
- "What are our company's audit policies for financial reporting?" *(→ Policy Index)*
- "Explain our risk assessment procedures" *(→ Methodology Index)*
- "What documentation is required for expense audits?" *(→ Policy Index)*
- "Find information about our internal control frameworks" *(→ Policy Index)*
- "What are the audit findings from last quarter's review?" *(→ Policy Index)*

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
- **`src/auditiq/config/agents.yaml`** - Define agent roles, goals, and capabilities
- **`src/auditiq/config/tasks.yaml`** - Configure task workflows and expectations
- **`src/auditiq/crew.py`** - Add custom logic, tools, and agent coordination
- **`src/auditiq/tools/custom_tool.py`** - Implement specialized tools and integrations

### Adding New Agents
1. Define agent configuration in `agents.yaml`
2. Create corresponding task in `tasks.yaml`
3. Add agent method in `crew.py`
4. Update query routing logic for new agent type

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