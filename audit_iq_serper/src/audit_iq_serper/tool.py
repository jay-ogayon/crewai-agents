from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import requests


class SerperSearchInput(BaseModel):
    """Input schema for SERPER search tool."""
    query: str = Field(..., description="Web search query for current audit and compliance information")
    num_results: int = Field(default=5, description="Number of search results to return")


class AuditIqSerper(BaseTool):
    name: str = "audit_iq_serper_search"
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
