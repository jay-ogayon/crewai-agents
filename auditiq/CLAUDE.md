# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses [UV](https://docs.astral.sh/uv/) for dependency management and crewAI for multi-agent AI workflows.

### Core Commands
- `crewai run` - Run the crew and execute tasks (generates report.md)
- `crewai install` - Install dependencies using UV
- `uv sync` - Sync project dependencies
- `uv run auditiq` - Run the project directly via UV
- `uv format` - Format Python code

### Available Scripts (via pyproject.toml)
- `uv run auditiq` - Main entry point
- `uv run run_crew` - Alternative run command
- `uv run train <iterations> <filename>` - Train the crew
- `uv run replay <task_id>` - Replay crew execution from specific task
- `uv run test <iterations> <eval_llm>` - Test crew execution

### Environment Setup
Required environment variables in `.env`:
- `MODEL=azure/gpt-4o` - Azure OpenAI model configuration
- `AZURE_API_KEY` - Azure OpenAI API key
- `AZURE_API_BASE` - Azure OpenAI endpoint base URL
- `AZURE_API_VERSION` - Azure OpenAI API version
- `AzureSearchEnpoint` - Azure Search service endpoint (for RAG Agent)
- `AzureSearchAdminKey` - Azure Search API key (for RAG Agent)
- `AzureSearchIndexName` - Azure Search index name for audit policies (defaults to 'audit-iq')
- `AzureSearchIndexName2` - Azure Search index name for methodologies (defaults to 'echo')
- `SERPER_API_KEY` - SERPER API key for web search (for Audit Researcher Agent)
- `AZURE_DOCUMENT_TRANSLATION_ENDPOINT` - Azure Document Translation service endpoint (for PDF Translator Agent)
- `AZURE_DOCUMENT_TRANSLATION_KEY` - Azure Document Translation API key (for PDF Translator Agent)
- `DOCUMENTS_FOLDER_PATH` - Custom Documents folder path (optional, auto-detects ~/Documents if not set)
- Ensure Python >=3.10,<3.14 is installed
- Run `crewai install` or `uv sync` to install dependencies


## Architecture

### Core Structure
- **Multi-Agent Audit System**: Specialized agents for comprehensive audit intelligence
- **RAG + Web Search**: Combines internal knowledge base with live web research
- **Configuration-Driven**: YAML configs define agent roles and task workflows
- **Azure Integration**: Leverages Azure OpenAI and Azure Search services

### Agent Architecture

#### 1. Echo RAG Agent
- **Purpose**: Search GT Guidelines and Policy content using Azure Cognitive Search
- **Data Source**: `echo` search index in Azure Search (configurable via `AzureSearchIndexName2`)
- **Capabilities**: 
  - Semantic search across GT company guidelines and policies
  - Contextual information retrieval for GT-specific requirements
  - Knowledge base querying for GT internal documentation
- **Configuration**: Uses Azure Search credentials from `.env`

#### 2. Audit RAG Agent
- **Purpose**: Search audit methodology content using Azure Cognitive Search
- **Data Source**: `audit-iq` search index in Azure Search (configurable via `AzureSearchIndexName`)
- **Capabilities**: 
  - Semantic search across audit methodology documents
  - Contextual information retrieval for audit techniques and procedures
  - Knowledge base querying for audit best practices and methodologies
- **Configuration**: Uses Azure Search credentials from `.env`

#### 3. Audit Researcher Agent  
- **Purpose**: Web-based research using SERPER API for current information
- **Data Source**: Live web search via SERPER API
- **Capabilities**:
  - Real-time web search for audit-related information
  - Current compliance requirements research
  - Industry trends and regulatory updates
  - Supplemental research beyond internal knowledge base
- **Configuration**: Uses SERPER API key from `.env`

#### 4. PDF Translator Agent
- **Purpose**: Translate PDF documents between languages while preserving formatting
- **Data Source**: Local PDF files and Azure Document Translation API
- **Capabilities**:
  - Multi-language document translation with format preservation
  - Automatic language detection or manual source language specification
  - Maintains document structure, images, tables, and layout
  - Professional-quality translation for audit and compliance documents
- **Configuration**: Uses Azure Document Translation credentials from `.env`

### Key Components

#### Main Entry Points
- `src/auditiq/main.py:16` - Main run() function that kicks off crew
- `src/auditiq/crew.py:10` - Auditiq crew class with @CrewBase decorator

#### Agent Configuration
- `src/auditiq/config/agents.yaml` - Defines RAG Agent and Audit Researcher Agent configurations
- `src/auditiq/config/tasks.yaml` - Defines search tasks and research workflows
- Multi-agent coordination for comprehensive audit intelligence

#### Workflow
The system uses intelligent LLM-based query routing to determine the appropriate workflow:

1. **Query Routing**: Query Router Agent analyzes user input and classifies it as:
   - **ECHO**: GT Guidelines and Policy queries → Routes to Echo RAG Agent
   - **AUDIT**: Audit methodology queries → Routes to Audit RAG Agent
   - **RESEARCH**: Current information needs → Routes to Audit Researcher Agent  
   - **TRANSLATE**: PDF translation requests → Routes to PDF Translator Agent

2. **ECHO Workflow**: Echo RAG Agent queries GT-specific echo index for relevant GT guidelines and policies
3. **AUDIT Workflow**: Audit RAG Agent queries audit-iq index for relevant audit methodologies and procedures
4. **Research Workflow**: Audit Researcher Agent performs live web search for current information
5. **Translation Workflow**: PDF Translator Agent converts documents between languages while preserving formatting
6. **Analysis & Reporting**: Contextual insights based on the selected workflow
7. **Output**: Specialized response based on query type (GT knowledge retrieval, audit methodology, research report, or translation confirmation)

#### Customization Points
- `src/auditiq/config/agents.yaml` - Modify agent roles, search parameters, and translation settings
- `src/auditiq/config/tasks.yaml` - Adjust search queries, research scope, and translation workflows
- `src/auditiq/crew.py` - Add custom tools for Azure Search, SERPER, and Document Translation integration
- `src/auditiq/tools/custom_tool.py` - Custom tools for specialized audit searches and PDF translation
- `knowledge/user_preference.txt` - User context for personalized audit focus

### Integration Details

#### Azure Search Integration (Echo & Audit RAG Agents)
- **Dual Index System**: Specialized agents for targeted search capabilities
  - **Echo Index**: Configurable via `AzureSearchIndexName2` (defaults to `echo`) - GT Guidelines and Policy documents accessed by Echo RAG Agent
  - **Audit Index**: Configurable via `AzureSearchIndexName` (defaults to `audit-iq`) - Audit methodology documents accessed by Audit RAG Agent
- **Query Classification**: Intelligent LLM-based routing determines which specialized agent to use
- **Search Type**: Semantic search with AI-powered relevance for each specific domain
- **Content**: 
  - Echo Agent: GT company guidelines, policies, procedures, GT-specific requirements
  - Audit Agent: Audit methodologies, techniques, procedures, best practices
- **Authentication**: Azure Search key-based authentication via `AzureSearchAdminKey`
- **Endpoint**: Configured via `AzureSearchEnpoint`

#### SERPER API Integration (Audit Researcher Agent)
- **Service**: Real-time web search API
- **Scope**: Current audit regulations, compliance updates, industry news
- **Rate Limits**: Managed through SERPER API quotas
- **Authentication**: API key-based authentication

#### Azure Document Translation Integration (PDF Translator Agent)
- **Service**: Azure AI Document Translation API for format-preserving translation
- **Supported Formats**: PDF documents with complex layouts, images, and tables
- **Languages**: 90+ language pairs with automatic detection capabilities
- **Format Preservation**: Maintains original document structure, fonts, images, and layout
- **Authentication**: Azure key-based authentication via `AZURE_DOCUMENT_TRANSLATION_KEY`
- **Endpoint**: Configurable via `AZURE_DOCUMENT_TRANSLATION_ENDPOINT`

### Input System
Enhanced inputs for audit intelligence:
- `audit_topic`: Specific audit area or compliance requirement
- `search_scope`: Internal only, external only, or combined search
- `current_year`: Current year for compliance context
- `jurisdiction`: Geographic or regulatory jurisdiction for focused research
- `user_query`: Primary input that gets intelligently routed to appropriate agent workflow

For document translation, you can use either:

**Simple format (recommended):**
- `"translate filename.pdf to spanish"` - The system will automatically find the file in Documents folder
- Supports both language codes (`es`) and names (`spanish`, `french`, etc.)
- Files are searched in this order:
  1. Custom path from `DOCUMENTS_FOLDER_PATH` environment variable
  2. `./Documents` (project Documents folder)
  3. `../Documents` (parent directory Documents folder) 
  4. `~/Documents` (user's Documents folder)
  5. Platform-specific locations (OneDrive, iCloud, etc.)

**Full path format (legacy):**
- `pdf_file_path`: Full absolute path to the PDF document
- `target_language`: Target language code (e.g., 'es', 'fr', 'de', 'zh')
- `source_language`: Source language (optional, uses auto-detection if not specified)
- `output_file_path`: Custom output path (optional, auto-generated if not provided)

### Testing & Debugging
- Use `uv run test <iterations> <eval_llm>` for multi-agent crew testing
- Training available via `uv run train <iterations> <filename>`
- Replay functionality for debugging specific search, research, and translation tasks
- Monitor Azure Search, SERPER API, and Azure Document Translation usage through respective dashboards
- Test PDF translation with sample documents to verify format preservation and language accuracy