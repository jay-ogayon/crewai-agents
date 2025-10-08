#!/usr/bin/env python3
"""
Example usage of the AuditIQ AUDIT RAG tool.
This demonstrates how to use the tool both standalone and within a CrewAI agent.
"""

import os
from dotenv import load_dotenv
from audit_iq_audit_rag import AuditIqAuditRag

# Load environment variables
load_dotenv()

def standalone_example():
    """Example of using the AUDIT RAG tool standalone."""
    print("=== Standalone Usage Example ===")
    
    # Initialize the tool
    audit_tool = AuditIqAuditRag()
    
    # Test search query for audit methodologies
    query = "internal controls testing procedures for financial reporting"
    
    print(f"Searching audit methodologies for: {query}")
    print("-" * 50)
    
    # Perform the search
    result = audit_tool._run(query=query, top=3)
    
    print(result)
    print()

def crewai_agent_example():
    """Example of using the AUDIT RAG tool within a CrewAI agent."""
    try:
        from crewai import Agent, Task, Crew
        
        print("=== CrewAI Agent Usage Example ===")
        
        # Create an agent with the AUDIT RAG tool
        audit_specialist = Agent(
            role="Audit Methodology Specialist",
            goal="Search and retrieve relevant information from audit methodology documents",
            backstory=(
                "You are an expert at navigating audit methodology knowledge bases and retrieving precise information "
                "about audit techniques, procedures, and best practices. You specialize in searching the audit-iq index "
                "to find relevant audit methodologies, procedures, historical audit findings, and compliance documentation."
            ),
            tools=[AuditIqAuditRag()],
            verbose=True
        )
        
        # Create a search task
        search_task = Task(
            description=(
                "Search for audit methodologies related to risk assessment and internal controls testing. "
                "Focus on finding specific procedures and best practices for conducting effective audits. "
                "Provide detailed information with methodology references."
            ),
            expected_output=(
                "A comprehensive summary of audit methodologies including "
                "risk assessment procedures, testing techniques, and compliance best practices."
            ),
            agent=audit_specialist
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[audit_specialist],
            tasks=[search_task],
            verbose=True
        )
        
        print("Starting audit methodology search...")
        result = crew.kickoff()
        
        print("\n=== Search Results ===")
        print(result)
        
    except ImportError:
        print("CrewAI not installed. Skipping CrewAI example.")
        print("To run this example, install CrewAI: pip install crewai")

if __name__ == "__main__":
    # Check if Azure Search credentials are configured
    if not os.getenv("AzureSearchEndpoint") or not os.getenv("AzureSearchAdminKey"):
        print("❌ Azure Search credentials not found in environment variables.")
        print("Please set your Azure Search credentials in the .env file.")
        print("Required: AzureSearchEndpoint and AzureSearchAdminKey")
        exit(1)
    
    print("🔍 AuditIQ AUDIT RAG Tool Examples")
    print("=" * 40)
    
    # Run standalone example
    standalone_example()
    
    # Run CrewAI example (if CrewAI is available)
    crewai_agent_example()