#!/usr/bin/env python3
"""
Example usage of the AuditIQ SERPER tool.
This demonstrates how to use the tool both standalone and within a CrewAI agent.
"""

import os
from dotenv import load_dotenv
from audit_iq_serper import AuditIqSerper

# Load environment variables
load_dotenv()

def standalone_example():
    """Example of using the SERPER tool standalone."""
    print("=== Standalone Usage Example ===")
    
    # Initialize the tool
    serper_tool = AuditIqSerper()
    
    # Test search query
    query = "latest audit regulations 2024 compliance requirements"
    
    print(f"Searching for: {query}")
    print("-" * 50)
    
    # Perform the search
    result = serper_tool._run(query=query, num_results=3)
    
    print(result)
    print()

def crewai_agent_example():
    """Example of using the SERPER tool within a CrewAI agent."""
    try:
        from crewai import Agent, Task, Crew
        
        print("=== CrewAI Agent Usage Example ===")
        
        # Create an agent with the SERPER tool
        researcher = Agent(
            role="Audit Research Specialist",
            goal="Conduct comprehensive web research on current audit regulations and compliance requirements",
            backstory=(
                "You are a skilled research analyst specializing in audit and compliance topics. "
                "You use web search capabilities to find the most current regulatory updates, "
                "industry best practices, and emerging compliance requirements."
            ),
            tools=[AuditIqSerper()],
            verbose=True
        )
        
        # Create a research task
        research_task = Task(
            description=(
                "Research the latest developments in audit regulations for 2024. "
                "Focus on new compliance requirements and industry best practices. "
                "Provide a summary of key findings with source citations."
            ),
            expected_output=(
                "A detailed research report including current regulatory updates, "
                "compliance requirements, and practical implications for audit practices."
            ),
            agent=researcher
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            verbose=True
        )
        
        print("Starting research...")
        result = crew.kickoff()
        
        print("\n=== Research Results ===")
        print(result)
        
    except ImportError:
        print("CrewAI not installed. Skipping CrewAI example.")
        print("To run this example, install CrewAI: pip install crewai")

if __name__ == "__main__":
    # Check if SERPER API key is configured
    if not os.getenv("SERPER_API_KEY"):
        print("❌ SERPER_API_KEY not found in environment variables.")
        print("Please set your SERPER API key in the .env file.")
        print("Get your key from: https://serper.dev/")
        exit(1)
    
    print("🔍 AuditIQ SERPER Tool Examples")
    print("=" * 40)
    
    # Run standalone example
    standalone_example()
    
    # Run CrewAI example (if CrewAI is available)
    crewai_agent_example()