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
        # Use intelligent routing workflow
        auditiq_crew = Auditiq()
        result = auditiq_crew.kickoff_intelligent_routing(inputs)
        
        # For cloud deployment, just return the result instead of writing to file
        print(f"\nQuery: {user_query}")
        print(f"Response:\n{result}")
        return result
        
    except Exception as e:
        error_msg = f"An error occurred while running the crew: {e}"
        print(error_msg)
        raise Exception(error_msg)

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
