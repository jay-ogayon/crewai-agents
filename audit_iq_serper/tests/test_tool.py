#!/usr/bin/env python3
"""
Tests for the AuditIQ SERPER tool.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from audit_iq_serper import AuditIqSerper


class TestAuditIqSerper(unittest.TestCase):
    """Test cases for the AuditIQ SERPER tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = AuditIqSerper()
    
    def test_tool_initialization(self):
        """Test that the tool initializes correctly."""
        self.assertEqual(self.tool.name, "audit_iq_serper_search")
        self.assertIn("SERPER API", self.tool.description)
        self.assertIsNotNone(self.tool.args_schema)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key(self):
        """Test behavior when SERPER API key is missing."""
        result = self.tool._run("test query")
        self.assertIn("SERPER API key not configured", result)
    
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    @patch('audit_iq_serper.tool.requests.post')
    def test_successful_search(self, mock_post):
        """Test successful search response."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "organic": [
                {
                    "title": "Test Audit Regulation",
                    "snippet": "Latest audit regulation details...",
                    "link": "https://example.com/audit-reg"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.tool._run("test audit query", 1)
        
        self.assertIn("Found 1 web results", result)
        self.assertIn("Test Audit Regulation", result)
        self.assertIn("https://example.com/audit-reg", result)
    
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    @patch('audit_iq_serper.tool.requests.post')
    def test_no_results(self, mock_post):
        """Test response when no results are found."""
        # Mock API response with no results
        mock_response = MagicMock()
        mock_response.json.return_value = {"organic": []}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.tool._run("test query")
        
        self.assertIn("No web results found", result)
    
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    @patch('audit_iq_serper.tool.requests.post')
    def test_timeout_error(self, mock_post):
        """Test handling of timeout errors."""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        
        result = self.tool._run("test query")
        
        self.assertIn("SERPER API request timed out", result)
    
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    @patch('audit_iq_serper.tool.requests.post')
    def test_connection_error(self, mock_post):
        """Test handling of connection errors."""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        result = self.tool._run("test query")
        
        self.assertIn("Unable to connect to SERPER API", result)
    
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_key"})
    @patch('audit_iq_serper.tool.requests.post')
    def test_http_error(self, mock_post):
        """Test handling of HTTP errors."""
        import requests
        mock_post.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        
        result = self.tool._run("test query")
        
        self.assertIn("SERPER API HTTP error", result)
        self.assertIn("check your SERPER_API_KEY", result)


if __name__ == "__main__":
    unittest.main()