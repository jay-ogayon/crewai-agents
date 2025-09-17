#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from auditiq.crew import Auditiq

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew with user query input.
    """
    # Check if user provided a query as command line argument
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        # Interactive mode - prompt user for query
        user_query = input("Enter your audit query: ")
    
    if not user_query.strip():
        print("Error: No query provided.")
        return
    
    inputs = {
        'user_query': user_query,
        'current_year': str(datetime.now().year)
    }
    
    try:
        # Use intelligent routing workflow
        auditiq_crew = Auditiq()
        result = auditiq_crew.kickoff_intelligent_routing(inputs)
        
        # Write result to file for consistency with original behavior
        with open('audit_response.md', 'w') as f:
            f.write(f"# Audit Intelligence Response\n\n")
            f.write(f"**Query:** {user_query}\n\n")
            f.write(f"**Response:**\n{result}\n")
            f.write(f"\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        print(f"\nResponse saved to audit_response.md")
        print(f"\nResponse:\n{result}")
        
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def run_qa():
    """
    Force Q&A mode - search internal knowledge base only.
    """
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = input("Enter your audit query (Q&A mode): ")
    
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
        
        with open('audit_qa_response.md', 'w') as f:
            f.write(f"# Q&A Response (Internal Knowledge Base)\n\n")
            f.write(f"**Query:** {user_query}\n\n")
            f.write(f"**Response:**\n{result}\n")
            f.write(f"\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        print(f"\nQ&A response saved to audit_qa_response.md")
        print(f"\nResponse:\n{result}")
        
    except Exception as e:
        raise Exception(f"An error occurred while running Q&A mode: {e}")

def run_research():
    """
    Force research mode - web search only.
    """
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = input("Enter your audit query (Research mode): ")
    
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
        
        with open('audit_research_response.md', 'w') as f:
            f.write(f"# Research Response (Web Search)\n\n")
            f.write(f"**Query:** {user_query}\n\n")
            f.write(f"**Response:**\n{result}\n")
            f.write(f"\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        print(f"\nResearch response saved to audit_research_response.md")
        print(f"\nResponse:\n{result}")
        
    except Exception as e:
        raise Exception(f"An error occurred while running research mode: {e}")

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
