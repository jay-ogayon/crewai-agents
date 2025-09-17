#!/usr/bin/env python
import sys
import warnings
import os

from datetime import datetime

from auditiq.crew import Auditiq

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def startup_health_check():
    """Perform startup health checks to identify potential deployment issues."""
    print("🔍 Performing startup health check...")
    
    issues = []
    
    # Check critical environment variables
    required_env_vars = [
        "AZURE_API_KEY",
        "AZURE_API_BASE", 
        "AzureSearchEnpoint",
        "AzureSearchAdminKey"
    ]
    
    for var in required_env_vars:
        if not os.getenv(var):
            issues.append(f"Missing required environment variable: {var}")
    
    # Check environment variable formats
    search_endpoint = os.getenv("AzureSearchEnpoint")
    if search_endpoint and not search_endpoint.startswith("https://"):
        issues.append("AzureSearchEnpoint should start with https://")
    
    azure_base = os.getenv("AZURE_API_BASE")
    if azure_base and not azure_base.startswith("https://"):
        issues.append("AZURE_API_BASE should start with https://")
    
    if issues:
        print(f"⚠️  Found {len(issues)} startup issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("⚠️  Continuing with deployment, but these may cause runtime issues.")
    else:
        print("✅ Startup health check passed!")
    
    return len(issues) == 0

def run():
    """
    Run the crew with user query input.
    """
    # Perform startup health check
    startup_health_check()
    
    # Check if user provided a query as command line argument
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        # For cloud deployment, use a default query if none provided
        user_query = "What are the audit policies for financial reporting?"
    
    if not user_query.strip():
        print("Error: No query provided.")
        return
    
    inputs = {
        'user_query': user_query,
        'current_year': str(datetime.now().year)
    }
    
    try:
        print(f"🚀 Initializing AuditIQ crew...")
        # Use intelligent routing workflow
        auditiq_crew = Auditiq()
        print(f"✅ Crew initialized successfully")
        
        print(f"🔍 Processing query: {user_query}")
        result = auditiq_crew.kickoff_intelligent_routing(inputs)
        
        # For cloud deployment, just return the result instead of writing to file
        print(f"✅ Query processed successfully")
        print(f"\nQuery: {user_query}")
        print(f"Response:\n{result}")
        return result
        
    except Exception as e:
        error_msg = f"An error occurred while running the crew: {e}"
        print(f"❌ Error: {error_msg}")
        # Don't raise in cloud environment to prevent deployment failure
        return f"Error: {error_msg}"

def run_qa():
    """
    Force Q&A mode - search internal knowledge base only.
    """
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = "What are the audit policies for financial reporting?"
    
    if not user_query.strip():
        print("Error: No query provided.")
        return
    
    inputs = {
        'user_query': user_query,
        'current_year': str(datetime.now().year)
    }
    
    try:
        auditiq_crew = Auditiq()
        qa_crew = auditiq_crew.create_dynamic_crew("QA")
        result = qa_crew.kickoff(inputs=inputs)
        
        print(f"\nQ&A Mode - Query: {user_query}")
        print(f"Response:\n{result}")
        return result
        
    except Exception as e:
        error_msg = f"An error occurred while running Q&A mode: {e}"
        print(error_msg)
        raise Exception(error_msg)

def run_research():
    """
    Force research mode - web search only.
    """
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = "What are the latest audit regulations for 2024?"
    
    if not user_query.strip():
        print("Error: No query provided.")
        return
    
    inputs = {
        'user_query': user_query,
        'current_year': str(datetime.now().year)
    }
    
    try:
        auditiq_crew = Auditiq()
        research_crew = auditiq_crew.create_dynamic_crew("RESEARCH")
        result = research_crew.kickoff(inputs=inputs)
        
        print(f"\nResearch Mode - Query: {user_query}")
        print(f"Response:\n{result}")
        return result
        
    except Exception as e:
        error_msg = f"An error occurred while running research mode: {e}"
        print(error_msg)
        raise Exception(error_msg)

def train():
    """
    Train the crew for a given number of iterations.
    """
    # Use a sample query for training
    inputs = {
        "user_query": "What are the current SOX compliance requirements?",
        'current_year': str(datetime.now().year)
    }
    try:
        auditiq_crew = Auditiq()
        auditiq_crew.crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        auditiq_crew = Auditiq()
        auditiq_crew.crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "user_query": "What are the key audit controls for financial reporting?",
        "current_year": str(datetime.now().year)
    }
    
    try:
        auditiq_crew = Auditiq()
        auditiq_crew.crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    run()
