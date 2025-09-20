import re
from typing import Optional, Tuple, Dict
from pathlib import Path
from .documents_helper import CrossPlatformDocumentsHelper

class SimpleTranslationHelper:
    """
    Simplified interface for document translation that automatically finds files in Documents folder.
    Provides user-friendly functions that only require filename and target language.
    """
    
    def __init__(self):
        self.docs_helper = CrossPlatformDocumentsHelper()
        self.translation_tool = None  # Will be initialized when needed
        
        # Language code mapping for common language names
        self.language_codes = {
            # Common language names to ISO codes
            'spanish': 'es',
            'french': 'fr',
            'german': 'de',
            'italian': 'it',
            'portuguese': 'pt',
            'chinese': 'zh',
            'japanese': 'ja',
            'korean': 'ko',
            'russian': 'ru',
            'arabic': 'ar',
            'hindi': 'hi',
            'dutch': 'nl',
            'swedish': 'sv',
            'norwegian': 'no',
            'danish': 'da',
            'finnish': 'fi',
            'polish': 'pl',
            'czech': 'cs',
            'hungarian': 'hu',
            'greek': 'el',
            'turkish': 'tr',
            'hebrew': 'he',
            'thai': 'th',
            'vietnamese': 'vi',
            'indonesian': 'id',
            'malay': 'ms',
            'tagalog': 'tl',
            'ukrainian': 'uk',
            'bulgarian': 'bg',
            'romanian': 'ro',
            'croatian': 'hr',
            'serbian': 'sr',
            'slovak': 'sk',
            'slovenian': 'sl',
            'lithuanian': 'lt',
            'latvian': 'lv',
            'estonian': 'et'
        }
    
    def translate_document(self, filename: str, target_language: str, source_language: str = "auto") -> str:
        """
        Simplified document translation function.
        
        Args:
            filename: Name of the file in Documents folder (e.g., "report.pdf", "invoice.docx")
            target_language: Target language code or name (e.g., "es", "spanish", "fr", "french")
            source_language: Source language code or "auto" for automatic detection
        
        Returns:
            String result message indicating success or failure with details
        """
        try:
            # Step 1: Find Documents folder
            docs_folder = self.docs_helper.find_documents_folder()
            if not docs_folder:
                return self._format_error("Cannot find Documents folder", self._get_documents_search_info())
            
            # Step 2: Find the file
            file_path = self.docs_helper.find_file(filename, docs_folder)
            if not file_path:
                return self._format_file_not_found_error(filename, docs_folder)
            
            # Step 3: Validate file access
            is_valid, error_msg = self.docs_helper.validate_file_access(file_path)
            if not is_valid:
                return self._format_error("File validation failed", error_msg)
            
            # Step 4: Normalize target language
            target_lang_code = self._normalize_language_code(target_language)
            if not target_lang_code:
                return self._format_error("Invalid target language", 
                                        f"'{target_language}' is not recognized. Use language codes (es, fr, de) or names (spanish, french, german)")
            
            # Step 5: Generate output path
            output_path = self.docs_helper.get_suggested_output_path(file_path, target_lang_code)
            
            # Step 6: Perform translation using the existing tool
            if self.translation_tool is None:
                # Initialize translation tool when needed to avoid circular import
                from .custom_tool import DocumentTranslationTool
                self.translation_tool = DocumentTranslationTool()
            
            result = self.translation_tool._run(
                file_path=str(file_path),
                target_language=target_lang_code,
                source_language=source_language,
                output_file_path=str(output_path)
            )
            
            # Step 7: Format and return result
            if "successfully translated" in result.lower():
                return self._format_success(file_path, output_path, target_lang_code, result)
            else:
                return self._format_error("Translation failed", result)
            
        except Exception as e:
            return self._format_error("Unexpected error during translation", str(e))
    
    def parse_translation_request(self, user_query: str) -> Optional[Tuple[str, str, str]]:
        """
        Parse a natural language translation request.
        
        Args:
            user_query: Natural language request like "translate report.pdf to spanish"
        
        Returns:
            Tuple of (filename, target_language, source_language) or None if parsing fails
        """
        query_lower = user_query.lower().strip()
        
        # Pattern 1: "translate [filename] to [language]"
        pattern1 = r'translate\s+([^\s]+(?:\.[^\s]+)?)\s+to\s+([^\s]+)'
        match1 = re.search(pattern1, query_lower)
        if match1:
            filename = match1.group(1)
            target_lang = match1.group(2)
            return filename, target_lang, "auto"
        
        # Pattern 2: "translate [filename] from [source] to [target]"
        pattern2 = r'translate\s+([^\s]+(?:\.[^\s]+)?)\s+from\s+([^\s]+)\s+to\s+([^\s]+)'
        match2 = re.search(pattern2, query_lower)
        if match2:
            filename = match2.group(1)
            source_lang = match2.group(2)
            target_lang = match2.group(3)
            return filename, target_lang, source_lang
        
        # Pattern 3: "[filename] to [language]"
        pattern3 = r'([^\s]+(?:\.[^\s]+)?)\s+to\s+([^\s]+)'
        match3 = re.search(pattern3, query_lower)
        if match3:
            filename = match3.group(1)
            target_lang = match3.group(2)
            return filename, target_lang, "auto"
        
        return None
    
    def list_available_files(self) -> str:
        """
        List all translatable files in the Documents folder.
        
        Returns:
            Formatted string listing available files
        """
        docs_folder = self.docs_helper.find_documents_folder()
        if not docs_folder:
            return "Cannot find Documents folder. " + self._get_documents_search_info()
        
        files = self.docs_helper.list_supported_files(docs_folder)
        if not files:
            return f"No translatable files found in Documents folder: {docs_folder}"
        
        file_list = "\n".join([f"  • {name}" for name, _ in files])
        return f"Available files for translation in {docs_folder}:\n{file_list}"
    
    def get_language_help(self) -> str:
        """
        Get help information about supported languages.
        
        Returns:
            Formatted string with language code information
        """
        common_langs = [
            "spanish (es)", "french (fr)", "german (de)", "italian (it)",
            "portuguese (pt)", "chinese (zh)", "japanese (ja)", "korean (ko)",
            "russian (ru)", "arabic (ar)", "dutch (nl)", "polish (pl)"
        ]
        
        return (
            "Supported languages (use name or code):\n" +
            "\n".join([f"  • {lang}" for lang in common_langs]) +
            "\n\nExamples:\n" +
            "  • translate report.pdf to spanish\n" +
            "  • translate invoice.docx to fr\n" +
            "  • translate document.pdf from english to german"
        )
    
    def _normalize_language_code(self, language: str) -> Optional[str]:
        """Convert language name or code to standard ISO code."""
        lang_lower = language.lower().strip()
        
        # If it's already a valid language code (2-3 letters)
        if len(lang_lower) in [2, 3] and lang_lower.isalpha():
            return lang_lower
        
        # Look up in language names mapping
        return self.language_codes.get(lang_lower)
    
    def _format_success(self, input_path: Path, output_path: Path, target_lang: str, result: str) -> str:
        """Format successful translation result."""
        return (
            f"✅ **Translation Successful**\n\n"
            f"**Input:** {input_path.name}\n"
            f"**Output:** {output_path.name}\n"
            f"**Language:** {target_lang}\n"
            f"**Location:** {output_path.parent}\n\n"
            f"**Details:** {result}"
        )
    
    def _format_error(self, error_type: str, details: str) -> str:
        """Format error message."""
        return f"❌ **{error_type}**\n\n{details}"
    
    def _format_file_not_found_error(self, filename: str, docs_folder: Path) -> str:
        """Format file not found error with helpful suggestions."""
        available_files = self.docs_helper.list_supported_files(docs_folder)
        
        error_msg = f"File '{filename}' not found in Documents folder: {docs_folder}"
        
        if available_files:
            similar_files = [name for name, _ in available_files if filename.lower() in name.lower() or name.lower() in filename.lower()]
            
            if similar_files:
                suggestions = "\n".join([f"  • {name}" for name in similar_files[:3]])
                error_msg += f"\n\n**Did you mean:**\n{suggestions}"
            else:
                all_files = "\n".join([f"  • {name}" for name, _ in available_files[:5]])
                error_msg += f"\n\n**Available files:**\n{all_files}"
                if len(available_files) > 5:
                    error_msg += f"\n  ... and {len(available_files) - 5} more"
        else:
            error_msg += "\n\nNo translatable files found in Documents folder."
        
        return self._format_error("File Not Found", error_msg)
    
    def _get_documents_search_info(self) -> str:
        """Get information about Documents folder search for debugging."""
        candidates = self.docs_helper.get_documents_folders()
        search_info = "Searched paths:\n" + "\n".join([f"  • {path}" for path in candidates])
        
        system_info = self.docs_helper.get_system_info()
        search_info += f"\n\nSystem: {system_info['system']}"
        search_info += f"\nUser home: {system_info['user_home']}"
        
        return search_info


def translate_document(filename: str, target_language: str, source_language: str = "auto") -> str:
    """
    Convenience function for simple document translation.
    
    Args:
        filename: Name of file in Documents folder
        target_language: Target language code or name
        source_language: Source language code or "auto"
    
    Returns:
        Translation result message
    """
    helper = SimpleTranslationHelper()
    return helper.translate_document(filename, target_language, source_language)