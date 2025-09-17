from crewai.tools import BaseTool
from typing import Type, Optional, List, Dict, Any
from pydantic import BaseModel, Field
import os
import requests
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import SingleDocumentTranslationClient
from azure.ai.translation.document.models import DocumentTranslateContent
import json

def is_cloud_environment() -> bool:
    """
    Detect if running in CrewAI cloud environment vs local development.
    """
    # Check for common cloud environment indicators
    cloud_indicators = [
        'CREWAI_CLOUD',  # CrewAI specific
        'KUBERNETES_SERVICE_HOST',  # Kubernetes
        'AWS_LAMBDA_FUNCTION_NAME',  # AWS Lambda
        'VERCEL',  # Vercel
        'HEROKU',  # Heroku
        'RAILWAY_ENVIRONMENT'  # Railway
    ]
    
    # If any cloud indicator is present, assume cloud environment
    if any(os.getenv(indicator) for indicator in cloud_indicators):
        return True
    
    # Additional heuristics for cloud detection
    if os.getenv('HOME') == '/home/runner':  # Common in cloud environments
        return True
    
    if not os.path.exists('/usr/bin') or not os.access('/tmp', os.W_OK):  # Limited file system
        return True
        
    return False


class AzureSearchInput(BaseModel):
    """Input schema for Azure Search tool."""
    query: str = Field(..., description="Search query for the audit knowledge base")
    top: int = Field(default=5, description="Number of search results to return")

class AzureSearchTool(BaseTool):
    name: str = "azure_search_tool"
    description: str = (
        "Search the internal audit knowledge base using Azure Cognitive Search. "
        "Automatically selects the appropriate index based on query content: "
        "- Audit policy queries use the main audit-iq index "
        "- Methodology queries use the methodology-specific index "
        "Use this tool to find relevant audit documents, policies, procedures, "
        "historical findings, and compliance documentation."
    )
    args_schema: Type[BaseModel] = AzureSearchInput

    def _classify_query(self, query: str) -> str:
        """
        Classify the query to determine which index to use.
        Returns 'policy' for audit policy queries, 'methodology' for methodology queries.
        """
        query_lower = query.lower()
        
        # Keywords that indicate methodology queries
        methodology_keywords = [
            'methodology', 'method', 'approach', 'technique', 'procedure', 'process',
            'how to', 'steps', 'workflow', 'framework', 'best practice', 'guideline',
            'implementation', 'execution', 'practice', 'standard operating', 'sop',
            'performing', 'conducting', 'execute', 'carry out', 'technique for',
            'standard procedures', 'procedures for', 'methods for'
        ]
        
        # Keywords that indicate policy queries
        policy_keywords = [
            'policy', 'policies', 'regulation', 'rule', 'requirement', 'compliance',
            'standard', 'mandate', 'directive', 'governance', 'audit rule',
            'regulatory', 'legal', 'obligation', 'requirements for'
        ]
        
        # Count matches for each category
        methodology_score = sum(1 for keyword in methodology_keywords if keyword in query_lower)
        policy_score = sum(1 for keyword in policy_keywords if keyword in query_lower)
        
        # Return the category with higher score, default to policy if tied
        if methodology_score > policy_score:
            return 'methodology'
        else:
            return 'policy'

    def _run(self, query: str, top: int = 5) -> str:
        try:
            # Get Azure Search configuration from environment using correct variable names
            search_endpoint = os.getenv("AzureSearchEnpoint")  # Note: keeping original spelling from user
            search_key = os.getenv("AzureSearchAdminKey")
            
            if not search_endpoint or not search_key:
                return "Error: Azure Search credentials not configured. Please check AzureSearchEnpoint and AzureSearchAdminKey in environment variables."
            
            # Classify the query to determine which index to use
            query_type = self._classify_query(query)
            
            # Select appropriate index based on query classification
            if query_type == 'methodology':
                index_name = os.getenv("AzureSearchIndexName2", "echo")  # Methodology index
                index_description = "methodology"
            else:
                index_name = os.getenv("AzureSearchIndexName", "audit-iq")  # Policy index
                index_description = "audit policy"
            
            # Initialize search client with timeout and error handling
            try:
                credential = AzureKeyCredential(search_key)
                search_client = SearchClient(
                    endpoint=search_endpoint,
                    index_name=index_name,
                    credential=credential
                )
            except Exception as init_error:
                return f"Error initializing Azure Search client: {str(init_error)}. Please check your Azure Search credentials and endpoint configuration."
            
            # Perform search with timeout (30 seconds)
            import time
            start_time = time.time()
            try:
                results = search_client.search(
                    search_text=query,
                    top=top,
                    include_total_count=True
                )
                
                # Convert results to list to avoid timeout during iteration
                results_list = list(results)
                elapsed_time = time.time() - start_time
                
                if elapsed_time > 30:  # 30 second timeout
                    return f"Search timeout after {elapsed_time:.1f} seconds. Please try a simpler query."
                    
            except Exception as search_error:
                elapsed_time = time.time() - start_time
                if elapsed_time > 30:
                    return f"Search timeout after {elapsed_time:.1f} seconds: {str(search_error)}"
                raise search_error
            
            # Format results
            formatted_results = []
            for result in results_list:
                result_dict = dict(result)
                # Extract key fields (adjust based on your index schema)
                title = result_dict.get('title', 'No title')
                content = result_dict.get('content', 'No content available')[:500]  # Limit content length
                score = result_dict.get('@search.score', 'N/A')
                
                formatted_results.append(f"**Title:** {title}\n**Score:** {score}\n**Content:** {content}...\n")
            
            if formatted_results:
                header = f"Searched {index_description} index ({index_name}) and found {len(formatted_results)} results for query '{query}':\n\n"
                return header + "\n---\n".join(formatted_results)
            else:
                return f"No results found in {index_description} index ({index_name}) for query: '{query}'"
                
        except Exception as e:
            return f"Error searching Azure index: {str(e)}"


class SerperSearchInput(BaseModel):
    """Input schema for SERPER search tool."""
    query: str = Field(..., description="Web search query for current audit and compliance information")
    num_results: int = Field(default=5, description="Number of search results to return")

class SerperSearchTool(BaseTool):
    name: str = "serper_search_tool"
    description: str = (
        "Search the web for current audit regulations, compliance requirements, "
        "industry trends, and regulatory updates using SERPER API. Use this tool "
        "to find up-to-date information not available in internal documents."
    )
    args_schema: Type[BaseModel] = SerperSearchInput

    def _run(self, query: str, num_results: int = 5) -> str:
        try:
            # Get SERPER API key from environment
            api_key = os.getenv("SERPER_API_KEY")
            
            if not api_key:
                return "Error: SERPER API key not configured in environment variables."
            
            # SERPER API endpoint
            url = "https://google.serper.dev/search"
            
            # Prepare request payload
            payload = {
                "q": query,
                "num": num_results
            }
            
            headers = {
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }
            
            # Make API request with 15 second timeout
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Format results
            formatted_results = []
            
            # Process organic results
            organic_results = data.get('organic', [])
            for result in organic_results:
                title = result.get('title', 'No title')
                snippet = result.get('snippet', 'No description available')
                link = result.get('link', 'No link')
                
                formatted_results.append(f"**Title:** {title}\n**URL:** {link}\n**Description:** {snippet}\n")
            
            if formatted_results:
                return f"Found {len(formatted_results)} web results for query '{query}':\n\n" + "\n---\n".join(formatted_results)
            else:
                return f"No web results found for query: '{query}'"
                
        except requests.exceptions.Timeout:
            return "Error: SERPER API request timed out after 15 seconds. Please try again with a simpler query."
        except requests.exceptions.ConnectionError:
            return "Error: Unable to connect to SERPER API. Please check your internet connection."
        except requests.exceptions.HTTPError as e:
            return f"Error: SERPER API HTTP error: {str(e)}. Please check your SERPER_API_KEY."
        except requests.RequestException as e:
            return f"Error making SERPER API request: {str(e)}"
        except Exception as e:
            return f"Error with web search: {str(e)}"


class DocumentTranslationInput(BaseModel):
    """Input schema for Document Translation tool."""
    file_path: str = Field(..., description="Full path to the document file to translate (PDF or DOCX)")
    target_language: str = Field(..., description="Target language code (e.g., 'es' for Spanish, 'fr' for French)")
    source_language: str = Field(default="auto", description="Source language code or 'auto' for automatic detection")
    output_file_path: str = Field(default="", description="Output path for translated document (optional, defaults to input path with language suffix)")

class DocumentTranslationTool(BaseTool):
    name: str = "document_translation_tool"
    description: str = (
        "Translate documents (PDF or DOCX) from one language to another while preserving formatting "
        "using Azure Document Translation service. Supports various languages and maintains "
        "document structure, images, tables, and layout. Auto-detects file format."
    )
    args_schema: Type[BaseModel] = DocumentTranslationInput

    def _get_content_type(self, file_path: str) -> str:
        """Determine the appropriate MIME type based on file extension."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Use the exact content types from the Azure documentation
        content_type_mapping = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword"
        }
        
        return content_type_mapping.get(file_extension, "application/octet-stream")
    
    def _run(self, file_path: str, target_language: str, source_language: str = "auto", output_file_path: str = "") -> str:
        # Check if running in cloud environment
        if is_cloud_environment():
            return (
                "Document translation is not available in cloud deployment due to file system restrictions. "
                "This feature is only available in local development environments where file access is permitted. "
                "For cloud-based document translation, please use the local deployment or consider using "
                "Azure Document Translation service directly via API."
            )
        
        try:
            # Get Azure Document Translation configuration from environment
            endpoint = os.getenv("AZURE_DOCUMENT_TRANSLATION_ENDPOINT")
            key = os.getenv("AZURE_DOCUMENT_TRANSLATION_KEY")
            
            if not endpoint or not key:
                return "Error: Azure Document Translation credentials not configured. Please check AZURE_DOCUMENT_TRANSLATION_ENDPOINT and AZURE_DOCUMENT_TRANSLATION_KEY in environment variables."
            
            # Handle relative paths by making them absolute
            if not os.path.isabs(file_path):
                # If relative path, assume it's relative to current working directory
                file_path = os.path.abspath(file_path)
            
            # Check if input file exists
            if not os.path.exists(file_path):
                return f"Error: Document file not found at path: {file_path}"
            
            # Validate file format
            file_extension = os.path.splitext(file_path)[1].lower()
            supported_formats = [".pdf", ".docx", ".doc"]
            
            if file_extension not in supported_formats:
                return f"Error: Unsupported file format '{file_extension}'. Supported formats: {', '.join(supported_formats)}"
            
            # Determine output file path if not provided
            if not output_file_path:
                base_name, ext = os.path.splitext(file_path)
                output_file_path = f"{base_name}_{target_language}{ext}"
            
            # Initialize the translation client
            client = SingleDocumentTranslationClient(endpoint, AzureKeyCredential(key))
            
            # Read the document file
            with open(file_path, 'rb') as file:
                file_contents = file.read()
                file_name = os.path.basename(file_path)
            
            print(f"File size: {len(file_contents)} bytes")
            print(f"File name: {file_name}")
            
            # Get the appropriate content type for the file
            content_type = self._get_content_type(file_path)
            
            # Create document translate content
            document_translate_content = DocumentTranslateContent(
                document=(file_name, file_contents, content_type)
            )
            
            # Perform translation
            print(f"Translating {file_name} from {source_language} to {target_language}...")
            
            # Call translate method with proper parameters
            # Don't include source_language if it's 'auto' for PDFs as it may cause issues
            translate_params = {
                "body": document_translate_content,
                "target_language": target_language
            }
            
            # Only add source language if it's not 'auto' and not PDF
            if source_language != "auto":
                translate_params["source_language"] = source_language
            
            response = client.translate(**translate_params)
            
            # Save translated document
            with open(output_file_path, 'wb') as output_file:
                output_file.write(response)
            
            file_size = os.path.getsize(output_file_path)
            file_type = "PDF" if file_extension == ".pdf" else "DOCX document"
            return f"Successfully translated {file_type} from {source_language} to {target_language}. Output saved to: {output_file_path} ({file_size} bytes)"
            
        except FileNotFoundError:
            return f"Error: Could not find document file at {file_path}"
        except PermissionError:
            return f"Error: Permission denied when accessing file {file_path} or writing to {output_file_path}"
        except Exception as e:
            return f"Error translating document: {str(e)}"


# Export tool classes for lazy instantiation
# This prevents import-time errors if environment variables are missing

# For backward compatibility, provide lazy-loaded instances
def get_azure_search_tool():
    """Get Azure Search tool instance with lazy loading."""
    return AzureSearchTool()

def get_serper_search_tool():
    """Get SERPER search tool instance with lazy loading."""
    return SerperSearchTool()

def get_document_translation_tool():
    """Get document translation tool instance with lazy loading."""
    return DocumentTranslationTool()

# Keep legacy global instances for backward compatibility
# These will be instantiated on first access, not at import time
azure_search_tool = None
serper_search_tool = None
document_translation_tool = None
pdf_translation_tool = None

def validate_environment_variables():
    """Validate that required environment variables are properly formatted."""
    issues = []
    
    # Check Azure OpenAI variables
    azure_api_key = os.getenv("AZURE_API_KEY")
    if azure_api_key and len(azure_api_key) < 10:
        issues.append("AZURE_API_KEY seems too short")
    
    # Check Azure Search variables
    search_endpoint = os.getenv("AzureSearchEnpoint")
    if search_endpoint and not search_endpoint.startswith("https://"):
        issues.append("AzureSearchEnpoint should start with https://")
    
    search_key = os.getenv("AzureSearchAdminKey")
    if search_key and len(search_key) < 10:
        issues.append("AzureSearchAdminKey seems too short")
    
    # Check Azure Document Translation variables
    doc_endpoint = os.getenv("AZURE_DOCUMENT_TRANSLATION_ENDPOINT")
    if doc_endpoint and not doc_endpoint.startswith("https://"):
        issues.append("AZURE_DOCUMENT_TRANSLATION_ENDPOINT should start with https://")
    
    doc_key = os.getenv("AZURE_DOCUMENT_TRANSLATION_KEY")
    if doc_key and len(doc_key) < 20:
        issues.append("AZURE_DOCUMENT_TRANSLATION_KEY seems too short")
    
    return issues

def _ensure_tools_loaded():
    """Ensure tool instances are loaded with proper error handling."""
    global azure_search_tool, serper_search_tool, document_translation_tool, pdf_translation_tool
    
    try:
        # Validate environment variables first
        env_issues = validate_environment_variables()
        if env_issues and not is_cloud_environment():
            print(f"Environment validation warnings: {', '.join(env_issues)}")
        
        if azure_search_tool is None:
            azure_search_tool = AzureSearchTool()
        if serper_search_tool is None:
            serper_search_tool = SerperSearchTool()
        if document_translation_tool is None:
            document_translation_tool = DocumentTranslationTool()
        if pdf_translation_tool is None:
            pdf_translation_tool = document_translation_tool
            
    except Exception as e:
        print(f"Warning: Tool initialization error: {e}")
        # Don't fail completely, just log the error
        if azure_search_tool is None:
            azure_search_tool = AzureSearchTool()
        if serper_search_tool is None:
            serper_search_tool = SerperSearchTool()
        if document_translation_tool is None:
            document_translation_tool = DocumentTranslationTool()
        if pdf_translation_tool is None:
            pdf_translation_tool = document_translation_tool

# Auto-load tools when module is accessed (with error handling)
try:
    _ensure_tools_loaded()
except Exception as startup_error:
    print(f"Startup warning: {startup_error}")
    # Continue anyway - tools will be loaded on demand
