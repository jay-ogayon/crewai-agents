#!/usr/bin/env python3
"""
Tests for the AuditIQ AUDIT RAG tool.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from audit_iq_audit_rag import AuditIqAuditRag


class TestAuditIqAuditRag(unittest.TestCase):
    """Test cases for the AuditIQ AUDIT RAG tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = AuditIqAuditRag()
    
    def test_tool_initialization(self):
        """Test that the tool initializes correctly."""
        self.assertEqual(self.tool.name, "audit_iq_audit_rag_search")
        self.assertIn("audit methodology knowledge base", self.tool.description)
        self.assertIn("audit-iq index", self.tool.description)
        self.assertIsNotNone(self.tool.args_schema)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_credentials(self):
        """Test behavior when Azure Search credentials are missing."""
        result = self.tool._run("test query")
        self.assertIn("Azure Search credentials not configured", result)
    
    @patch.dict(os.environ, {"AzureSearchEnpoint": "https://test.search.windows.net", "AzureSearchAdminKey": ""})
    def test_missing_key(self):
        """Test behavior when Azure Search key is missing."""
        result = self.tool._run("test query")
        self.assertIn("Azure Search credentials not configured", result)
    
    @patch.dict(os.environ, {"AzureSearchEnpoint": "https://test.search.windows.net", "AzureSearchAdminKey": "test_key"})
    @patch('audit_iq_audit_rag.tool.SearchClient')
    def test_successful_search(self, mock_search_client):
        """Test successful search response."""
        # Mock search client and results
        mock_client_instance = MagicMock()
        mock_search_client.return_value = mock_client_instance
        
        mock_result = {
            "title": "Internal Controls Testing",
            "content": "Audit methodology for testing internal controls...",
            "@search.score": 0.89
        }
        mock_client_instance.search.return_value = [mock_result]
        
        result = self.tool._run("internal controls testing", 1)
        
        self.assertIn("Searched audit methodology index (audit-iq)", result)
        self.assertIn("Internal Controls Testing", result)
        self.assertIn("0.89", result)
    
    @patch.dict(os.environ, {"AzureSearchEnpoint": "https://test.search.windows.net", "AzureSearchAdminKey": "test_key"})
    @patch('audit_iq_audit_rag.tool.SearchClient')
    def test_no_results(self, mock_search_client):
        """Test response when no results are found."""
        # Mock search client with no results
        mock_client_instance = MagicMock()
        mock_search_client.return_value = mock_client_instance
        mock_client_instance.search.return_value = []
        
        result = self.tool._run("nonexistent methodology")
        
        self.assertIn("No results found in audit methodology index (audit-iq)", result)
    
    @patch.dict(os.environ, {"AzureSearchEnpoint": "https://test.search.windows.net", "AzureSearchAdminKey": "test_key"})
    @patch('audit_iq_audit_rag.tool.SearchClient')
    def test_client_initialization_error(self, mock_search_client):
        """Test handling of client initialization errors."""
        mock_search_client.side_effect = Exception("Connection failed")
        
        result = self.tool._run("test query")
        
        self.assertIn("Error initializing Azure Search client", result)
    
    @patch.dict(os.environ, {"AzureSearchEnpoint": "https://test.search.windows.net", "AzureSearchAdminKey": "test_key"})
    @patch('audit_iq_audit_rag.tool.SearchClient')
    def test_search_error(self, mock_search_client):
        """Test handling of search errors."""
        mock_client_instance = MagicMock()
        mock_search_client.return_value = mock_client_instance
        mock_client_instance.search.side_effect = Exception("Search failed")
        
        result = self.tool._run("test query")
        
        self.assertIn("Error searching audit methodology index", result)


if __name__ == "__main__":
    unittest.main()