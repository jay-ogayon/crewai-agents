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
            
            # Initialize search client
            credential = AzureKeyCredential(search_key)
            search_client = SearchClient(
                endpoint=search_endpoint,
                index_name=index_name,
                credential=credential
            )
            
            # Perform search
            results = search_client.search(
                search_text=query,
                top=top,
                include_total_count=True
            )
            
            # Format results
            formatted_results = []
            for result in results:
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
            
            # Make API request
            response = requests.post(url, headers=headers, json=payload)
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


# Export tools for easy import
azure_search_tool = AzureSearchTool()
serper_search_tool = SerperSearchTool()
document_translation_tool = DocumentTranslationTool()

# Keep backward compatibility
pdf_translation_tool = document_translation_tool
