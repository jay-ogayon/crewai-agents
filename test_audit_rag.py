#!/usr/bin/env python3
"""
Test script for AuditIQ AUDIT RAG tool
Tests audit methodology search functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add the audit rag tool to Python path
sys.path.insert(0, '/Users/ferdinanda/Desktop/AuditIQ/audit_iq_audit_rag/src')

def test_audit_rag():
    """Test the AUDIT RAG tool with various queries."""
    
    print("🔍 Testing AuditIQ AUDIT RAG Tool")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv('/Users/ferdinanda/Desktop/AuditIQ/audit_iq_audit_rag/.env')
    
    # Check environment variables
    endpoint = os.getenv("AzureSearchEndpoint")
    key = os.getenv("AzureSearchAdminKey")
    
    print(f"Azure Search Endpoint: {endpoint}")
    print(f"Azure Search Key: {'*' * 20 if key else 'NOT SET'}")
    print()
    
    if not endpoint or not key:
        print("❌ Azure Search credentials not configured!")
        print("Please check your .env file.")
        return False
    
    try:
        # Import and initialize the tool
        from audit_iq_audit_rag import AuditIqAuditRag
        audit_tool = AuditIqAuditRag()
        
        print("✅ AUDIT RAG tool imported successfully")
        print()
        
        # Test queries for audit methodology
        test_queries = [
            "internal controls testing procedures",
            "risk assessment methodology",
            "audit sampling techniques", 
            "financial statement audit procedures",
            "compliance testing procedures"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"📋 Test {i}: {query}")
            print("-" * 30)
            
            try:
                result = audit_tool._run(query=query, top=2)
                
                if "Error:" in result:
                    print(f"❌ Error: {result}")
                    return False
                elif "No results found" in result:
                    print(f"⚠️  No results found for: {query}")
                else:
                    print("✅ Search successful!")
                    # Print first 200 characters of result
                    preview = result[:200] + "..." if len(result) > 200 else result
                    print(f"Preview: {preview}")
                
                print()
                
            except Exception as e:
                print(f"❌ Exception during search: {str(e)}")
                return False
        
        print("🎉 All AUDIT RAG tests completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import AUDIT RAG tool: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_audit_rag()
    sys.exit(0 if success else 1)