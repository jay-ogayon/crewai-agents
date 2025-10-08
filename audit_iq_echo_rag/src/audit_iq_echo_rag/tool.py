from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import time
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential


class EchoSearchInput(BaseModel):
    """Input schema for ECHO RAG search tool."""
    query: str = Field(..., description="Search query for GT Guidelines and Policy knowledge base")
    top: int = Field(default=5, description="Number of search results to return")


class AuditIqEchoRag(BaseTool):
    name: str = "audit_iq_echo_rag_search"
    description: str = (
        "Search GT Guidelines and Policy knowledge base using Azure Cognitive Search. "
        "Searches the echo index specifically for GT company guidelines, policies, procedures, "
        "and GT-specific requirements. Use this tool to find relevant GT internal documentation."
    )
    args_schema: Type[BaseModel] = EchoSearchInput

    def _run(self, query: str, top: int = 5) -> str:
        try:
            # Get Azure Search configuration from environment
            search_endpoint = os.getenv("AzureSearchEnpoint")
            search_key = os.getenv("AzureSearchAdminKey")
            
            if not search_endpoint or not search_key:
                return "Error: Azure Search credentials not configured. Please check AzureSearchEnpoint and AzureSearchAdminKey in environment variables."
            
            # Use echo index for GT Guidelines and Policy (hardcoded)
            index_name = "echo"
            
            # Initialize search client
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
            start_time = time.time()
            try:
                results = search_client.search(
                    search_text=query,
                    top=top,
                    include_total_count=True
                )
                
                results_list = list(results)
                elapsed_time = time.time() - start_time
                
                if elapsed_time > 30:
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
                title = result_dict.get('title', 'No title')
                content = result_dict.get('content', 'No content available')[:500]
                score = result_dict.get('@search.score', 'N/A')
                
                formatted_results.append(f"**Title:** {title}\n**Score:** {score}\n**Content:** {content}...\n")
            
            if formatted_results:
                header = f"Searched GT Guidelines and Policy index ({index_name}) and found {len(formatted_results)} results for query '{query}':\n\n"
                return header + "\n---\n".join(formatted_results)
            else:
                return f"No results found in GT Guidelines and Policy index ({index_name}) for query: '{query}'"
                
        except Exception as e:
            return f"Error searching GT Guidelines and Policy index: {str(e)}"