#!/usr/bin/env python3
"""
Combined test script for both AuditIQ RAG tools
Tests both ECHO and AUDIT RAG functionality
"""

import os
import sys
from dotenv import load_dotenv

def setup_environment():
    """Setup environment and validate credentials."""
    print("🔧 Setting up test environment")
    print("=" * 50)
    
    # Load environment variables from audit rag .env file
    env_file = '/Users/ferdinanda/Desktop/AuditIQ/audit_iq_audit_rag/.env'
    load_dotenv(env_file)
    
    # Check environment variables
    endpoint = os.getenv("AzureSearchEndpoint")
    key = os.getenv("AzureSearchAdminKey")
    
    print(f"Environment file: {env_file}")
    print(f"Azure Search Endpoint: {endpoint}")
    print(f"Azure Search Key: {'*' * 20 if key else 'NOT SET'}")
    print()
    
    if not endpoint or not key:
        print("❌ Azure Search credentials not configured!")
        print("Please check your .env file has:")
        print("  - AzureSearchEndpoint=https://your-search-service.search.windows.net")
        print("  - AzureSearchAdminKey=your_admin_key")
        return False
    
    return True

def test_echo_tool():
    """Test ECHO RAG tool for GT Guidelines."""
    print("🔍 Testing ECHO RAG Tool (GT Guidelines)")
    print("=" * 50)
    
    try:
        # Add echo rag tool to path and import
        sys.path.insert(0, '/Users/ferdinanda/Desktop/AuditIQ/audit_iq_echo_rag/src')
        from audit_iq_echo_rag import AuditIqEchoRag
        
        echo_tool = AuditIqEchoRag()
        print("✅ ECHO RAG tool imported successfully")
        
        # Test a simple query
        test_query = "GT travel policy"
        print(f"📋 Testing query: '{test_query}'")
        
        result = echo_tool._run(query=test_query, top=1)
        
        if "Error:" in result:
            print(f"❌ ECHO Tool Error: {result}")
            return False
        elif "No results found" in result:
            print(f"⚠️  ECHO Tool: No results found (this might be expected)")
            print(f"Result: {result}")
            return True  # No results is still a successful connection
        else:
            print("✅ ECHO Tool: Search successful!")
            print(f"Result preview: {result[:150]}...")
            return True
            
    except Exception as e:
        print(f"❌ ECHO Tool Exception: {str(e)}")
        return False

def test_audit_tool():
    """Test AUDIT RAG tool for audit methodology."""
    print("🔍 Testing AUDIT RAG Tool (Audit Methodology)")
    print("=" * 50)
    
    try:
        # Add audit rag tool to path and import
        sys.path.insert(0, '/Users/ferdinanda/Desktop/AuditIQ/audit_iq_audit_rag/src')
        from audit_iq_audit_rag import AuditIqAuditRag
        
        audit_tool = AuditIqAuditRag()
        print("✅ AUDIT RAG tool imported successfully")
        
        # Test a simple query
        test_query = "internal controls"
        print(f"📋 Testing query: '{test_query}'")
        
        result = audit_tool._run(query=test_query, top=1)
        
        if "Error:" in result:
            print(f"❌ AUDIT Tool Error: {result}")
            return False
        elif "No results found" in result:
            print(f"⚠️  AUDIT Tool: No results found (this might be expected)")
            print(f"Result: {result}")
            return True  # No results is still a successful connection
        else:
            print("✅ AUDIT Tool: Search successful!")
            print(f"Result preview: {result[:150]}...")
            return True
            
    except Exception as e:
        print(f"❌ AUDIT Tool Exception: {str(e)}")
        return False

def main():
    """Main test function."""
    print("🚀 AuditIQ RAG Tools - Local Testing Suite")
    print("=" * 60)
    print()
    
    # Setup environment
    if not setup_environment():
        return False
    
    print()
    
    # Test ECHO tool
    echo_success = test_echo_tool()
    print()
    
    # Test AUDIT tool  
    audit_success = test_audit_tool()
    print()
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 30)
    print(f"ECHO RAG Tool:  {'✅ PASSED' if echo_success else '❌ FAILED'}")
    print(f"AUDIT RAG Tool: {'✅ PASSED' if audit_success else '❌ FAILED'}")
    print()
    
    if echo_success and audit_success:
        print("🎉 All tests passed! Both RAG tools are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)