"""
Tests for AuditIQ Document Translator Tool
"""

import os
import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from audit_iq_document_translator.tool import (
    AuditIqDocumentTranslator,
    CrossPlatformDocumentsHelper,
    SimpleTranslationHelper,
    DocumentTranslationInput
)


class TestDocumentTranslationInput:
    """Test the input schema validation."""
    
    def test_valid_input(self):
        """Test valid input creation."""
        input_data = DocumentTranslationInput(
            file_path="test.pdf",
            target_language="spanish"
        )
        assert input_data.file_path == "test.pdf"
        assert input_data.target_language == "spanish"
        assert input_data.source_language == "auto"
        assert input_data.output_file_path == ""
    
    def test_input_with_all_fields(self):
        """Test input with all fields specified."""
        input_data = DocumentTranslationInput(
            file_path="/path/to/document.pdf",
            target_language="fr",
            source_language="en",
            output_file_path="/output/document_fr.pdf"
        )
        assert input_data.file_path == "/path/to/document.pdf"
        assert input_data.target_language == "fr"
        assert input_data.source_language == "en"
        assert input_data.output_file_path == "/output/document_fr.pdf"


class TestCrossPlatformDocumentsHelper:
    """Test the cross-platform documents helper."""
    
    def test_supported_extensions(self):
        """Test that supported extensions are correctly defined."""
        helper = CrossPlatformDocumentsHelper()
        expected_extensions = {'.pdf', '.docx', '.doc'}
        assert helper.supported_extensions == expected_extensions
    
    @patch('platform.system')
    def test_system_detection(self, mock_system):
        """Test system detection."""
        mock_system.return_value = "Darwin"
        helper = CrossPlatformDocumentsHelper()
        assert helper.system == "darwin"
    
    @patch.dict(os.environ, {'DOCUMENTS_FOLDER_PATH': '/custom/docs'})
    def test_custom_documents_path(self):
        """Test custom documents folder path from environment."""
        helper = CrossPlatformDocumentsHelper()
        candidates = helper.get_documents_folders()
        assert Path('/custom/docs') in candidates
        assert candidates[0] == Path('/custom/docs')  # Should be first priority
    
    def test_validate_file_access_missing_file(self):
        """Test file validation with missing file."""
        helper = CrossPlatformDocumentsHelper()
        non_existent_path = Path("/non/existent/file.pdf")
        is_valid, error_msg = helper.validate_file_access(non_existent_path)
        assert not is_valid
        assert "not found" in error_msg.lower()
    
    def test_get_suggested_output_path(self):
        """Test output path generation."""
        helper = CrossPlatformDocumentsHelper()
        input_path = Path("/docs/report.pdf")
        output_path = helper.get_suggested_output_path(input_path, "es")
        assert output_path == Path("/docs/report_es.pdf")


class TestSimpleTranslationHelper:
    """Test the simple translation helper."""
    
    def test_normalize_language_code_valid_code(self):
        """Test normalization with valid language codes."""
        helper = SimpleTranslationHelper()
        assert helper.normalize_language_code("es") == "es"
        assert helper.normalize_language_code("fr") == "fr"
        assert helper.normalize_language_code("EN") == "en"
    
    def test_normalize_language_code_valid_name(self):
        """Test normalization with valid language names."""
        helper = SimpleTranslationHelper()
        assert helper.normalize_language_code("spanish") == "es"
        assert helper.normalize_language_code("french") == "fr"
        assert helper.normalize_language_code("GERMAN") == "de"
    
    def test_normalize_language_code_invalid(self):
        """Test normalization with invalid language."""
        helper = SimpleTranslationHelper()
        assert helper.normalize_language_code("invalid") is None
        assert helper.normalize_language_code("xyz") is None


class TestAuditIqDocumentTranslator:
    """Test the main document translator tool."""
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        tool = AuditIqDocumentTranslator()
        assert tool.name == "audit_iq_document_translator"
        assert "translate documents" in tool.description.lower()
        assert tool.args_schema == DocumentTranslationInput
    
    def test_get_content_type(self):
        """Test content type detection."""
        tool = AuditIqDocumentTranslator()
        assert tool._get_content_type("test.pdf") == "application/pdf"
        assert tool._get_content_type("test.docx") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert tool._get_content_type("test.doc") == "application/msword"
        assert tool._get_content_type("test.unknown") == "application/octet-stream"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_azure_credentials(self):
        """Test handling of missing Azure credentials."""
        tool = AuditIqDocumentTranslator()
        result = tool._perform_azure_translation(
            "test.pdf", "es", "auto", "output.pdf"
        )
        assert "azure document translation credentials not configured" in result.lower()
    
    @patch('os.path.exists')
    def test_file_not_found_full_path(self, mock_exists):
        """Test handling of non-existent file with full path."""
        mock_exists.return_value = False
        tool = AuditIqDocumentTranslator()
        result = tool._translate_by_full_path(
            "/non/existent/file.pdf", "es", "auto", ""
        )
        assert "not found" in result.lower()
    
    def test_unsupported_file_format(self):
        """Test handling of unsupported file format."""
        tool = AuditIqDocumentTranslator()
        with patch('os.path.exists', return_value=True):
            result = tool._translate_by_full_path(
                "/path/to/file.txt", "es", "auto", ""
            )
        assert "unsupported file format" in result.lower()
    
    def test_invalid_target_language(self):
        """Test handling of invalid target language."""
        tool = AuditIqDocumentTranslator()
        with patch('os.path.exists', return_value=True):
            result = tool._translate_by_full_path(
                "/path/to/file.pdf", "invalid_lang", "auto", ""
            )
        assert "invalid target language" in result.lower()
    
    @patch('audit_iq_document_translator.tool.CrossPlatformDocumentsHelper')
    def test_filename_only_translation_missing_docs_folder(self, mock_helper_class):
        """Test filename-only translation when Documents folder is missing."""
        mock_helper = Mock()
        mock_helper.find_documents_folder.return_value = None
        mock_helper_class.return_value = mock_helper
        
        tool = AuditIqDocumentTranslator()
        tool.docs_helper = mock_helper
        
        result = tool._translate_by_filename("test.pdf", "es", "auto", "")
        assert "cannot find documents folder" in result.lower()
    
    @patch('audit_iq_document_translator.tool.CrossPlatformDocumentsHelper')
    def test_filename_only_translation_file_not_found(self, mock_helper_class):
        """Test filename-only translation when file is not found."""
        mock_helper = Mock()
        mock_helper.find_documents_folder.return_value = Path("/docs")
        mock_helper.find_file.return_value = None
        mock_helper_class.return_value = mock_helper
        
        tool = AuditIqDocumentTranslator()
        tool.docs_helper = mock_helper
        
        result = tool._translate_by_filename("test.pdf", "es", "auto", "")
        assert "not found" in result.lower()
    
    def test_format_success(self):
        """Test success message formatting."""
        tool = AuditIqDocumentTranslator()
        result = tool._format_success(
            Path("/docs/input.pdf"),
            Path("/docs/output_es.pdf"),
            "es",
            "Translation completed successfully"
        )
        assert "✅" in result
        assert "Translation Successful" in result
        assert "input.pdf" in result
        assert "output_es.pdf" in result
        assert "es" in result
    
    def test_format_error(self):
        """Test error message formatting."""
        tool = AuditIqDocumentTranslator()
        result = tool._format_error("Test Error", "Detailed error message")
        assert "❌" in result
        assert "Test Error" in result
        assert "Detailed error message" in result


class TestIntegration:
    """Integration tests with mocked Azure services."""
    
    @patch.dict(os.environ, {
        'AZURE_DOCUMENT_TRANSLATION_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_DOCUMENT_TRANSLATION_KEY': 'test-key-12345'
    })
    @patch('audit_iq_document_translator.tool.SingleDocumentTranslationClient')
    @patch('builtins.open', new_callable=mock_open, read_data=b'mock pdf content')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_successful_translation(self, mock_getsize, mock_exists, mock_file, mock_client_class):
        """Test successful translation flow."""
        # Setup mocks
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        mock_client = Mock()
        mock_client.translate.return_value = b'translated content'
        mock_client_class.return_value = mock_client
        
        # Run translation
        tool = AuditIqDocumentTranslator()
        result = tool._perform_azure_translation(
            "/path/to/test.pdf", "es", "auto", "/output/test_es.pdf"
        )
        
        # Verify results
        assert "successfully translated" in result.lower()
        assert "1024 bytes" in result
        mock_client.translate.assert_called_once()
    
    @patch('audit_iq_document_translator.tool.CrossPlatformDocumentsHelper')
    @patch('audit_iq_document_translator.tool.SimpleTranslationHelper')
    def test_run_method_filename_path(self, mock_translation_helper_class, mock_docs_helper_class):
        """Test _run method with filename path."""
        # Setup mocks
        mock_docs_helper = Mock()
        mock_translation_helper = Mock()
        mock_docs_helper_class.return_value = mock_docs_helper
        mock_translation_helper_class.return_value = mock_translation_helper
        
        tool = AuditIqDocumentTranslator()
        
        with patch.object(tool, '_translate_by_filename', return_value="Success") as mock_translate:
            result = tool._run("test.pdf", "spanish")
            mock_translate.assert_called_once_with("test.pdf", "spanish", "auto", "")
            assert result == "Success"
    
    @patch('audit_iq_document_translator.tool.CrossPlatformDocumentsHelper')
    @patch('audit_iq_document_translator.tool.SimpleTranslationHelper')
    def test_run_method_full_path(self, mock_translation_helper_class, mock_docs_helper_class):
        """Test _run method with full path."""
        # Setup mocks
        mock_docs_helper = Mock()
        mock_translation_helper = Mock()
        mock_docs_helper_class.return_value = mock_docs_helper
        mock_translation_helper_class.return_value = mock_translation_helper
        
        tool = AuditIqDocumentTranslator()
        
        with patch.object(tool, '_translate_by_full_path', return_value="Success") as mock_translate:
            result = tool._run("/full/path/to/test.pdf", "es")
            mock_translate.assert_called_once_with("/full/path/to/test.pdf", "es", "auto", "")
            assert result == "Success"


if __name__ == "__main__":
    pytest.main([__file__])