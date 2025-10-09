from crewai.tools import BaseTool
from typing import Type, Optional, List, Tuple
from pydantic import BaseModel, Field
import os
import platform
from pathlib import Path
from azure.ai.translation.document import SingleDocumentTranslationClient
from azure.ai.translation.document.models import DocumentTranslateContent
from azure.core.credentials import AzureKeyCredential


class DocumentTranslationInput(BaseModel):
    """Input schema for Document Translation tool."""
    file_path: str = Field(..., description="Full path to the document file to translate (PDF or DOCX). Can also be just a filename to search in Documents folder")
    target_language: str = Field(..., description="Target language code (e.g., 'es' for Spanish, 'fr' for French) or language name (e.g., 'spanish', 'french')")
    source_language: str = Field(default="auto", description="Source language code or 'auto' for automatic detection")
    output_file_path: str = Field(default="", description="Output path for translated document (optional, defaults to input path with language suffix)")


class CrossPlatformDocumentsHelper:
    """
    Cross-platform helper for finding and managing documents in the Documents folder.
    Works seamlessly on Mac, Windows, and Linux systems.
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.supported_extensions = {'.pdf', '.docx', '.doc'}
    
    def get_documents_folders(self) -> List[Path]:
        """Get potential Documents folder locations in priority order."""
        candidates = []
        
        # 1. Environment variable override (highest priority)
        env_path = os.getenv("DOCUMENTS_FOLDER_PATH")
        if env_path:
            candidates.append(Path(env_path))
        
        # 2. Project-local Documents folder (current working directory)
        try:
            cwd = Path.cwd()
            project_docs = cwd / "Documents"
            candidates.append(project_docs)
        except Exception:
            pass
        
        # 3. Parent directory Documents folder (in case we're in a subdirectory)
        try:
            cwd = Path.cwd()
            parent_docs = cwd.parent / "Documents"
            candidates.append(parent_docs)
        except Exception:
            pass
        
        # 4. Standard user Documents folder (cross-platform)
        try:
            user_home = Path.home()
            standard_docs = user_home / "Documents"
            candidates.append(standard_docs)
        except Exception:
            pass
        
        # 5. Platform-specific additional locations
        if self.system == "windows":
            try:
                # OneDrive Documents (common on Windows)
                user_home = Path.home()
                onedrive_docs = user_home / "OneDrive" / "Documents"
                candidates.append(onedrive_docs)
                
                # Legacy Windows path structure
                username = os.getenv("USERNAME")
                if username:
                    legacy_path = Path(f"C:/Users/{username}/Documents")
                    candidates.append(legacy_path)
            except Exception:
                pass
                
        elif self.system == "darwin":  # macOS
            try:
                user_home = Path.home()
                # iCloud Documents (if synced)
                icloud_docs = user_home / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "Documents"
                candidates.append(icloud_docs)
                
                # Legacy macOS path
                username = os.getenv("USER")
                if username:
                    legacy_path = Path(f"/Users/{username}/Documents")
                    candidates.append(legacy_path)
            except Exception:
                pass
        
        elif self.system == "linux":
            try:
                # XDG user directories
                xdg_docs = Path.home() / "Documents"
                candidates.append(xdg_docs)
                
                username = os.getenv("USER")
                if username:
                    legacy_path = Path(f"/home/{username}/Documents")
                    candidates.append(legacy_path)
            except Exception:
                pass
        
        # Remove duplicates while preserving order
        unique_candidates = []
        seen = set()
        for path in candidates:
            if path not in seen:
                unique_candidates.append(path)
                seen.add(path)
        
        return unique_candidates
    
    def find_documents_folder(self) -> Optional[Path]:
        """Find the first existing and accessible Documents folder."""
        candidates = self.get_documents_folders()
        
        for folder in candidates:
            if self._is_valid_documents_folder(folder):
                return folder
        
        return None
    
    def _is_valid_documents_folder(self, path: Path) -> bool:
        """Check if a path is a valid, accessible Documents folder."""
        try:
            return (
                path.exists() and 
                path.is_dir() and 
                os.access(path, os.R_OK)
            )
        except (OSError, PermissionError):
            return False
    
    def find_file(self, filename: str, documents_folder: Optional[Path] = None) -> Optional[Path]:
        """Find a file in the Documents folder using case-insensitive search."""
        if documents_folder is None:
            documents_folder = self.find_documents_folder()
        
        if not documents_folder:
            return None
        
        return self._search_file_in_directory(filename, documents_folder)
    
    def _search_file_in_directory(self, filename: str, directory: Path) -> Optional[Path]:
        """Search for a file in the given directory with case-insensitive matching."""
        if not directory.exists() or not directory.is_dir():
            return None
        
        search_name = filename.lower()
        
        try:
            # Get all files in the directory
            for file_path in directory.iterdir():
                if not file_path.is_file():
                    continue
                
                file_name = file_path.name.lower()
                
                # Exact match (case-insensitive)
                if file_name == search_name:
                    return file_path
                
                # Match with automatic extension detection
                if self._matches_with_extension(search_name, file_name):
                    return file_path
            
            # If no exact match, try partial matching
            return self._find_partial_match(search_name, directory)
            
        except (PermissionError, OSError):
            return None
    
    def _matches_with_extension(self, search_name: str, file_name: str) -> bool:
        """Check if search name matches file name when considering extensions."""
        # If search name has no extension, try adding supported extensions
        if '.' not in search_name:
            for ext in self.supported_extensions:
                if file_name == search_name + ext:
                    return True
        
        # If search name has extension, check if file has supported extension
        if '.' in search_name:
            search_base = search_name.rsplit('.', 1)[0]
            file_base = file_name.rsplit('.', 1)[0] if '.' in file_name else file_name
            file_ext = '.' + file_name.rsplit('.', 1)[1] if '.' in file_name else ''
            
            return (search_base == file_base and 
                   file_ext in self.supported_extensions)
        
        return False
    
    def _find_partial_match(self, search_name: str, directory: Path) -> Optional[Path]:
        """Find partial matches if exact match fails."""
        try:
            # Remove extension from search name for partial matching
            search_base = search_name.rsplit('.', 1)[0] if '.' in search_name else search_name
            
            best_match = None
            best_score = 0
            
            for file_path in directory.iterdir():
                if not file_path.is_file():
                    continue
                
                file_name = file_path.name.lower()
                file_ext = '.' + file_name.rsplit('.', 1)[1] if '.' in file_name else ''
                
                # Only consider supported file types
                if file_ext not in self.supported_extensions:
                    continue
                
                file_base = file_name.rsplit('.', 1)[0] if '.' in file_name else file_name
                
                # Calculate similarity score
                if search_base in file_base or file_base in search_base:
                    # Simple scoring: longer common substring gets higher score
                    score = len(self._longest_common_substring(search_base, file_base))
                    if score > best_score:
                        best_score = score
                        best_match = file_path
            
            # Only return match if it's reasonably good (at least 3 characters match)
            return best_match if best_score >= 3 else None
            
        except (PermissionError, OSError):
            return None
    
    def _longest_common_substring(self, str1: str, str2: str) -> str:
        """Find the longest common substring between two strings."""
        longest = ""
        for i in range(len(str1)):
            for j in range(i + 1, len(str1) + 1):
                substr = str1[i:j]
                if substr in str2 and len(substr) > len(longest):
                    longest = substr
        return longest
    
    def validate_file_access(self, file_path: Path) -> Tuple[bool, str]:
        """Validate that a file exists and is accessible."""
        if not file_path.exists():
            return False, f"File not found: {file_path}"
        
        if not file_path.is_file():
            return False, f"Path is not a file: {file_path}"
        
        if file_path.suffix.lower() not in self.supported_extensions:
            return False, f"Unsupported file type: {file_path.suffix}. Supported: {', '.join(self.supported_extensions)}"
        
        try:
            if not os.access(file_path, os.R_OK):
                return False, f"No read permission for file: {file_path}"
        except OSError as e:
            return False, f"Cannot access file: {e}"
        
        return True, ""
    
    def get_suggested_output_path(self, input_path: Path, target_language: str) -> Path:
        """Generate a suggested output path for the translated document."""
        directory = input_path.parent
        name_without_ext = input_path.stem
        extension = input_path.suffix
        
        # Create output filename with language suffix
        output_name = f"{name_without_ext}_{target_language}{extension}"
        return directory / output_name


class SimpleTranslationHelper:
    """Simplified interface for document translation that automatically finds files in Documents folder."""
    
    def __init__(self):
        self.docs_helper = CrossPlatformDocumentsHelper()
        
        # Language code mapping for common language names
        self.language_codes = {
            'spanish': 'es', 'french': 'fr', 'german': 'de', 'italian': 'it',
            'portuguese': 'pt', 'chinese': 'zh', 'japanese': 'ja', 'korean': 'ko',
            'russian': 'ru', 'arabic': 'ar', 'hindi': 'hi', 'dutch': 'nl',
            'swedish': 'sv', 'norwegian': 'no', 'danish': 'da', 'finnish': 'fi',
            'polish': 'pl', 'czech': 'cs', 'hungarian': 'hu', 'greek': 'el',
            'turkish': 'tr', 'hebrew': 'he', 'thai': 'th', 'vietnamese': 'vi',
            'indonesian': 'id', 'malay': 'ms', 'tagalog': 'tl', 'ukrainian': 'uk',
            'bulgarian': 'bg', 'romanian': 'ro', 'croatian': 'hr', 'serbian': 'sr',
            'slovak': 'sk', 'slovenian': 'sl', 'lithuanian': 'lt', 'latvian': 'lv',
            'estonian': 'et'
        }
    
    def normalize_language_code(self, language: str) -> Optional[str]:
        """Convert language name or code to standard ISO code."""
        lang_lower = language.lower().strip()
        
        # If it's already a valid language code (2-3 letters)
        if len(lang_lower) in [2, 3] and lang_lower.isalpha():
            return lang_lower
        
        # Look up in language names mapping
        return self.language_codes.get(lang_lower)


class AuditIqDocumentTranslator(BaseTool):
    name: str = "audit_iq_document_translator"
    description: str = (
        "Translate documents (PDF or DOCX) from one language to another while preserving formatting "
        "using Azure Document Translation service. Supports various languages and maintains "
        "document structure, images, tables, and layout. Can accept either full file paths or just "
        "filenames (will search Documents folder automatically). Supports language codes (es, fr) or "
        "language names (spanish, french). Auto-detects file format."
    )
    args_schema: Type[BaseModel] = DocumentTranslationInput

    def __init__(self):
        super().__init__()
        self.docs_helper = CrossPlatformDocumentsHelper()
        self.translation_helper = SimpleTranslationHelper()

    def _get_content_type(self, file_path: str) -> str:
        """Determine the appropriate MIME type based on file extension."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        content_type_mapping = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword"
        }
        
        return content_type_mapping.get(file_extension, "application/octet-stream")

    def _run(self, file_path: str, target_language: str, source_language: str = "auto", output_file_path: str = "") -> str:
        try:
            # Check if this looks like a simple filename (not a full path)
            if not os.path.isabs(file_path) and '/' not in file_path and '\\' not in file_path:
                # Use simplified logic for filename-only requests
                return self._translate_by_filename(file_path, target_language, source_language, output_file_path)
            else:
                # Use full path logic
                return self._translate_by_full_path(file_path, target_language, source_language, output_file_path)
                
        except Exception as e:
            return f"Error during translation: {str(e)}"

    def _translate_by_filename(self, filename: str, target_language: str, source_language: str, output_file_path: str) -> str:
        """Handle translation when only filename is provided."""
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
            target_lang_code = self.translation_helper.normalize_language_code(target_language)
            if not target_lang_code:
                return self._format_error("Invalid target language", 
                                        f"'{target_language}' is not recognized. Use language codes (es, fr, de) or names (spanish, french, german)")
            
            # Step 5: Generate output path if not provided
            if not output_file_path:
                output_path = self.docs_helper.get_suggested_output_path(file_path, target_lang_code)
            else:
                output_path = Path(output_file_path)
            
            # Step 6: Perform translation
            result = self._perform_azure_translation(str(file_path), target_lang_code, source_language, str(output_path))
            
            # Step 7: Format and return result
            if "successfully translated" in result.lower():
                return self._format_success(file_path, output_path, target_lang_code, result)
            else:
                return self._format_error("Translation failed", result)
            
        except Exception as e:
            return self._format_error("Unexpected error during translation", str(e))

    def _translate_by_full_path(self, file_path: str, target_language: str, source_language: str, output_file_path: str) -> str:
        """Handle translation when full file path is provided."""
        try:
            # Handle relative paths by making them absolute
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)
            
            # Check if input file exists
            if not os.path.exists(file_path):
                return f"Error: Document file not found at path: {file_path}"
            
            # Validate file format
            file_extension = os.path.splitext(file_path)[1].lower()
            supported_formats = [".pdf", ".docx", ".doc"]
            
            if file_extension not in supported_formats:
                return f"Error: Unsupported file format '{file_extension}'. Supported formats: {', '.join(supported_formats)}"
            
            # Normalize target language
            target_lang_code = self.translation_helper.normalize_language_code(target_language)
            if not target_lang_code:
                return f"Error: Invalid target language '{target_language}'. Use language codes (es, fr, de) or names (spanish, french, german)"
            
            # Determine output file path if not provided
            if not output_file_path:
                base_name, ext = os.path.splitext(file_path)
                output_file_path = f"{base_name}_{target_lang_code}{ext}"
            
            # Perform translation
            return self._perform_azure_translation(file_path, target_lang_code, source_language, output_file_path)
            
        except Exception as e:
            return f"Error translating document: {str(e)}"

    def _perform_azure_translation(self, file_path: str, target_language: str, source_language: str, output_file_path: str) -> str:
        """Perform the actual Azure translation."""
        try:
            # Get Azure Document Translation configuration from environment
            endpoint = os.getenv("AZURE_DOCUMENT_TRANSLATION_ENDPOINT")
            key = os.getenv("AZURE_DOCUMENT_TRANSLATION_KEY")
            
            if not endpoint or not key:
                return "Error: Azure Document Translation credentials not configured. Please check AZURE_DOCUMENT_TRANSLATION_ENDPOINT and AZURE_DOCUMENT_TRANSLATION_KEY in environment variables."
            
            # Initialize the translation client
            client = SingleDocumentTranslationClient(endpoint, AzureKeyCredential(key))
            
            # Read the document file
            with open(file_path, 'rb') as file:
                file_contents = file.read()
                file_name = os.path.basename(file_path)
            
            # Get the appropriate content type for the file
            content_type = self._get_content_type(file_path)
            
            # Create document translate content
            document_translate_content = DocumentTranslateContent(
                document=(file_name, file_contents, content_type)
            )
            
            # Perform translation
            translate_params = {
                "body": document_translate_content,
                "target_language": target_language
            }
            
            # Only add source language if it's not 'auto'
            if source_language != "auto":
                translate_params["source_language"] = source_language
            
            response = client.translate(**translate_params)
            
            # Save translated document
            with open(output_file_path, 'wb') as output_file:
                output_file.write(response)
            
            file_size = os.path.getsize(output_file_path)
            file_extension = os.path.splitext(file_path)[1].lower()
            file_type = "PDF" if file_extension == ".pdf" else "DOCX document"
            
            return f"Successfully translated {file_type} from {source_language} to {target_language}. Output saved to: {output_file_path} ({file_size} bytes)"
            
        except FileNotFoundError:
            return f"Error: Could not find document file at {file_path}"
        except PermissionError:
            return f"Error: Permission denied when accessing file {file_path} or writing to {output_file_path}"
        except Exception as e:
            return f"Error translating document: {str(e)}"

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
        try:
            # Try to list files in directory for suggestions
            available_files = []
            for file_path in docs_folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.docs_helper.supported_extensions:
                    available_files.append(file_path.name)
        except:
            available_files = []
        
        error_msg = f"File '{filename}' not found in Documents folder: {docs_folder}"
        
        if available_files:
            similar_files = [name for name in available_files if filename.lower() in name.lower() or name.lower() in filename.lower()]
            
            if similar_files:
                suggestions = "\n".join([f"  • {name}" for name in similar_files[:3]])
                error_msg += f"\n\n**Did you mean:**\n{suggestions}"
            else:
                all_files = "\n".join([f"  • {name}" for name in available_files[:5]])
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
        
        search_info += f"\n\nSystem: {platform.system()}"
        search_info += f"\nUser home: {Path.home()}"
        
        return search_info