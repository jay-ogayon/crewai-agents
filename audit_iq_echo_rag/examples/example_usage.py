#!/usr/bin/env python3
"""
Example usage of the AuditIQ ECHO RAG tool.
This demonstrates how to use the tool both standalone and within a CrewAI agent.
"""

import os
from dotenv import load_dotenv
from audit_iq_echo_rag import AuditIqEchoRag

# Load environment variables
load_dotenv()

def standalone_example():
    """Example of using the ECHO RAG tool standalone."""
    print("=== Standalone Usage Example ===")
    
    # Initialize the tool
    echo_tool = AuditIqEchoRag()
    
    # Test search query for GT Guidelines
    query = "GT company travel policy expense requirements"
    
    print(f"Searching GT Guidelines for: {query}")
    print("-" * 50)
    
    # Perform the search
    result = echo_tool._run(query=query, top=3)
    
    print(result)
    print()

def crewai_agent_example():
    """Example of using the ECHO RAG tool within a CrewAI agent."""
    try:
        from crewai import Agent, Task, Crew
        
        print("=== CrewAI Agent Usage Example ===")
        
        # Create an agent with the ECHO RAG tool
        gt_specialist = Agent(
            role="GT Guidelines and Policy Specialist",
            goal="Search and retrieve relevant information from GT Guidelines and Policy documents",
            backstory=(
                "You are an expert at navigating GT company guidelines and policy documentation. "
                "You specialize in searching the echo index to find relevant GT policies, procedures, "
                "company guidelines, and internal compliance documentation."
            ),
            tools=[AuditIqEchoRag()],
            verbose=True
        )
        
        # Create a search task
        search_task = Task(
            description=(
                "Search for GT company policies related to employee expense management and travel. "
                "Focus on finding specific requirements and procedures that employees must follow. "
                "Provide detailed information with policy references."
            ),
            expected_output=(
                "A comprehensive summary of GT expense and travel policies including "
                "specific requirements, approval processes, and compliance guidelines."
            ),
            agent=gt_specialist
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[gt_specialist],
            tasks=[search_task],
            verbose=True
        )
        
        print("Starting GT Guidelines search...")
        result = crew.kickoff()
        
        print("\n=== Search Results ===")
        print(result)
        
    except ImportError:
        print("CrewAI not installed. Skipping CrewAI example.")
        print("To run this example, install CrewAI: pip install crewai")

if __name__ == "__main__":
    # Check if Azure Search credentials are configured
    if not os.getenv("AzureSearchEnpoint") or not os.getenv("AzureSearchAdminKey"):
        print("❌ Azure Search credentials not found in environment variables.")
        print("Please set your Azure Search credentials in the .env file.")
        print("Required: AzureSearchEnpoint and AzureSearchAdminKey")
        exit(1)
    
    print("🔍 AuditIQ ECHO RAG Tool Examples")
    print("=" * 40)
    
    # Run standalone example
    standalone_example()
    
    # Run CrewAI example (if CrewAI is available)
    crewai_agent_example()