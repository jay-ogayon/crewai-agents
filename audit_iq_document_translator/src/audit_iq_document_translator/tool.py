from crewai.tools import BaseTool
from typing import Type, Optional, List, Tuple
from pydantic import BaseModel, Field
import os
import platform
import tempfile
import urllib.parse
from pathlib import Path
from azure.ai.translation.document import SingleDocumentTranslationClient
from azure.ai.translation.document.models import DocumentTranslateContent
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError, AzureError


class DocumentTranslationInput(BaseModel):
    """Input schema for Document Translation tool."""
    file_path: str = Field(..., description="Path to document file: local path, filename (searches Documents folder), blob URL (https://account.blob.core.windows.net/container/file.pdf), or blob path (container/file.pdf)")
    target_language: str = Field(..., description="Target language code (e.g., 'es' for Spanish, 'fr' for French) or language name (e.g., 'spanish', 'french')")
    source_language: str = Field(default="auto", description="Source language code or 'auto' for automatic detection")
    output_file_path: str = Field(default="", description="Output path for translated document: local path, blob URL, or blob path (optional, defaults to input location with language suffix)")
    use_blob_storage: bool = Field(default=True, description="Force use of Azure Blob Storage for file operations (always enabled)")


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


class AzureBlobStorageHelper:
    """
    Azure Blob Storage helper for document file operations.
    Handles blob upload, download, listing, and path resolution.
    """
    
    def __init__(self):
        self.blob_service_client = None
        self.supported_extensions = {'.pdf', '.docx', '.doc'}
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Azure Blob Storage client from environment variables."""
        try:
            # Try connection string first
            connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            if connection_string:
                self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                return
            
            # Try account name and key
            account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
            account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
            if account_name and account_key:
                account_url = f"https://{account_name}.blob.core.windows.net"
                self.blob_service_client = BlobServiceClient(account_url=account_url, credential=account_key)
                return
                
            # Could add managed identity support here in the future
                
        except Exception as e:
            # Client will remain None, operations will handle gracefully
            pass
    
    def is_blob_path(self, path: str) -> bool:
        """Check if a path is a blob storage path or URL."""
        if not path:
            return False
        
        # Check for blob URL
        if path.startswith('https://') and '.blob.core.windows.net' in path:
            return True
        
        # Check for blob path format (container/folder/file.ext)
        if '/' in path and not os.path.isabs(path) and not path.startswith('./'):
            # Simple heuristic: if it contains '/' but isn't an absolute local path
            return True
            
        return False
    
    def parse_blob_url(self, blob_url: str) -> Tuple[str, str, str]:
        """Parse blob URL into account, container, and blob name."""
        try:
            parsed = urllib.parse.urlparse(blob_url)
            account_name = parsed.hostname.split('.')[0]
            path_parts = parsed.path.lstrip('/').split('/')
            container_name = path_parts[0]
            blob_name = '/'.join(path_parts[1:])
            return account_name, container_name, blob_name
        except Exception:
            raise ValueError(f"Invalid blob URL format: {blob_url}")
    
    def parse_blob_path(self, blob_path: str) -> Tuple[str, str]:
        """Parse blob path into container and blob name."""
        if '/' not in blob_path:
            raise ValueError(f"Blob path must include container: {blob_path}")
        
        parts = blob_path.split('/', 1)
        return parts[0], parts[1]
    
    def download_blob_to_temp(self, blob_path: str) -> Tuple[str, str]:
        """Download blob to temporary file and return temp path and original filename."""
        if not self.blob_service_client:
            raise RuntimeError("Azure Blob Storage client not initialized. Check connection string or credentials.")
        
        try:
            # Parse path
            if blob_path.startswith('https://') and '.blob.core.windows.net' in blob_path:
                account_name, container_name, blob_name = self.parse_blob_url(blob_path)
            else:
                container_name, blob_name = self.parse_blob_path(blob_path)
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, 
                blob=blob_name
            )
            
            # Check if blob exists
            if not blob_client.exists():
                raise FileNotFoundError(f"Blob not found: {blob_path}")
            
            # Get file extension for temp file
            original_filename = os.path.basename(blob_name)
            file_ext = os.path.splitext(original_filename)[1]
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                temp_path = temp_file.name
                
                # Download blob content
                download_stream = blob_client.download_blob()
                temp_file.write(download_stream.readall())
            
            return temp_path, original_filename
            
        except ResourceNotFoundError:
            raise FileNotFoundError(f"Blob not found: {blob_path}")
        except AzureError as e:
            raise RuntimeError(f"Azure Blob Storage error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error downloading blob: {str(e)}")
    
    def upload_file_to_blob(self, local_file_path: str, blob_path: str, overwrite: bool = True) -> str:
        """Upload local file to blob storage and return blob URL."""
        if not self.blob_service_client:
            raise RuntimeError("Azure Blob Storage client not initialized. Check connection string or credentials.")
        
        try:
            # Parse destination path
            if blob_path.startswith('https://') and '.blob.core.windows.net' in blob_path:
                account_name, container_name, blob_name = self.parse_blob_url(blob_path)
            else:
                container_name, blob_name = self.parse_blob_path(blob_path)
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            # Upload file
            with open(local_file_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=overwrite)
            
            # Return blob URL
            return blob_client.url
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Local file not found: {local_file_path}")
        except AzureError as e:
            raise RuntimeError(f"Azure Blob Storage error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error uploading to blob: {str(e)}")
    
    def find_blob_by_filename(self, filename: str, container_name: str = None) -> Optional[str]:
        """Find blob by filename, searching in specified container or all containers."""
        if not self.blob_service_client:
            return None
        
        try:
            search_filename = filename.lower()
            containers_to_search = []
            
            if container_name:
                containers_to_search = [container_name]
            else:
                # Search in common containers
                common_containers = ['documents', 'files', 'source', 'input']
                try:
                    all_containers = [c.name for c in self.blob_service_client.list_containers()]
                    containers_to_search = [c for c in common_containers if c in all_containers]
                    if not containers_to_search:
                        containers_to_search = all_containers[:5]  # Limit search scope
                except:
                    containers_to_search = common_containers
            
            for container in containers_to_search:
                try:
                    container_client = self.blob_service_client.get_container_client(container)
                    for blob in container_client.list_blobs():
                        blob_filename = os.path.basename(blob.name).lower()
                        
                        # Exact match
                        if blob_filename == search_filename:
                            return f"{container}/{blob.name}"
                        
                        # Match with extension variants
                        if self._matches_with_extension(search_filename, blob_filename):
                            return f"{container}/{blob.name}"
                except:
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _matches_with_extension(self, search_name: str, blob_name: str) -> bool:
        """Check if search name matches blob name considering extensions."""
        if '.' not in search_name:
            for ext in self.supported_extensions:
                if blob_name == search_name + ext:
                    return True
        
        if '.' in search_name:
            search_base = search_name.rsplit('.', 1)[0]
            blob_base = blob_name.rsplit('.', 1)[0] if '.' in blob_name else blob_name
            blob_ext = '.' + blob_name.rsplit('.', 1)[1] if '.' in blob_name else ''
            
            return (search_base == blob_base and blob_ext in self.supported_extensions)
        
        return False
    
    def get_suggested_output_blob_path(self, input_blob_path: str, target_language: str) -> str:
        """Generate suggested output blob path for translated document."""
        if input_blob_path.startswith('https://') and '.blob.core.windows.net' in input_blob_path:
            account_name, container_name, blob_name = self.parse_blob_url(input_blob_path)
        else:
            container_name, blob_name = self.parse_blob_path(input_blob_path)
        
        # Parse filename
        directory = os.path.dirname(blob_name)
        filename = os.path.basename(blob_name)
        name_without_ext, extension = os.path.splitext(filename)
        
        # Create output filename with language suffix
        output_filename = f"{name_without_ext}_{target_language}{extension}"
        
        # Combine paths
        if directory:
            output_blob_name = f"{directory}/{output_filename}"
        else:
            output_blob_name = output_filename
        
        return f"{container_name}/{output_blob_name}"


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
        "using Azure Document Translation service. Supports local files, Azure Blob Storage, and automatic "
        "file discovery. Input can be local paths, filenames (searches Documents folder), blob URLs, or "
        "blob paths (container/file.pdf). Supports various languages and maintains document structure, "
        "images, tables, and layout. Outputs to same storage type as input unless specified otherwise."
    )
    args_schema: Type[BaseModel] = DocumentTranslationInput

    def __init__(self):
        super().__init__()
        # Initialize helpers after super().__init__() to avoid Pydantic field validation
        object.__setattr__(self, 'docs_helper', CrossPlatformDocumentsHelper())
        object.__setattr__(self, 'blob_helper', AzureBlobStorageHelper())
        object.__setattr__(self, 'translation_helper', SimpleTranslationHelper())

    def _get_content_type(self, file_path: str) -> str:
        """Determine the appropriate MIME type based on file extension."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Azure Document Translation supported content types
        content_type_mapping = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
            ".html": "text/html",
            ".htm": "text/html",
            ".txt": "text/plain"
        }
        
        content_type = content_type_mapping.get(file_extension, "application/octet-stream")
        
        # For debugging: ensure we're using supported content types
        if content_type == "application/octet-stream":
            supported_exts = list(content_type_mapping.keys())
            raise ValueError(f"Unsupported file extension '{file_extension}'. Supported: {supported_exts}")
        
        return content_type

    def _run(self, file_path: str, target_language: str, source_language: str = "auto", output_file_path: str = "", use_blob_storage: bool = True) -> str:
        try:
            # Determine if we should use blob storage
            use_blob = use_blob_storage or self.blob_helper.is_blob_path(file_path)
            
            if use_blob:
                return self._translate_blob_storage(file_path, target_language, source_language, output_file_path)
            elif not os.path.isabs(file_path) and '/' not in file_path and '\\' not in file_path:
                # Use simplified logic for filename-only requests (local files)
                return self._translate_by_filename(file_path, target_language, source_language, output_file_path)
            else:
                # Use full path logic (local files)
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

    def _translate_blob_storage(self, blob_path: str, target_language: str, source_language: str, output_file_path: str) -> str:
        """Handle translation for Azure Blob Storage files."""
        temp_input_path = None
        temp_output_path = None
        
        try:
            # Step 1: Handle input blob path resolution
            if self.blob_helper.is_blob_path(blob_path):
                input_blob_path = blob_path
            else:
                # Try to find blob by filename
                found_blob_path = self.blob_helper.find_blob_by_filename(blob_path)
                if not found_blob_path:
                    return self._format_error("Blob Not Found", 
                                            f"Could not find blob with filename '{blob_path}' in any container. "
                                            f"Use full blob path like 'container/file.pdf' or blob URL.")
                input_blob_path = found_blob_path
            
            # Step 2: Normalize target language
            target_lang_code = self.translation_helper.normalize_language_code(target_language)
            if not target_lang_code:
                return self._format_error("Invalid target language", 
                                        f"'{target_language}' is not recognized. Use language codes (es, fr, de) or names (spanish, french, german)")
            
            # Step 3: Download blob to temporary file
            try:
                temp_input_path, original_filename = self.blob_helper.download_blob_to_temp(input_blob_path)
            except FileNotFoundError as e:
                return self._format_error("Blob Not Found", str(e))
            except RuntimeError as e:
                return self._format_error("Blob Storage Error", str(e))
            
            # Step 4: Validate file format
            file_extension = os.path.splitext(original_filename)[1].lower()
            if file_extension not in self.blob_helper.supported_extensions:
                return self._format_error("Unsupported File Format", 
                                        f"File '{original_filename}' has unsupported format '{file_extension}'. "
                                        f"Supported formats: {', '.join(self.blob_helper.supported_extensions)}")
            
            # Step 5: Create temporary output file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_output:
                temp_output_path = temp_output.name
            
            # Step 6: Perform translation
            translation_result = self._perform_azure_translation(
                temp_input_path, target_lang_code, source_language, temp_output_path
            )
            
            if "successfully translated" not in translation_result.lower():
                return self._format_error("Translation Failed", translation_result)
            
            # Step 7: Determine output blob path
            if output_file_path:
                if self.blob_helper.is_blob_path(output_file_path):
                    output_blob_path = output_file_path
                else:
                    # Treat as local path, don't upload to blob
                    import shutil
                    shutil.copy2(temp_output_path, output_file_path)
                    return self._format_success_mixed(input_blob_path, output_file_path, target_lang_code, "local")
            else:
                output_blob_path = self.blob_helper.get_suggested_output_blob_path(input_blob_path, target_lang_code)
            
            # Step 8: Upload translated file to blob storage
            try:
                blob_url = self.blob_helper.upload_file_to_blob(temp_output_path, output_blob_path, overwrite=True)
                return self._format_success_blob(input_blob_path, output_blob_path, blob_url, target_lang_code, translation_result)
            except RuntimeError as e:
                return self._format_error("Upload Failed", f"Translation completed but failed to upload result: {str(e)}")
            
        except Exception as e:
            return self._format_error("Unexpected Error", f"Error during blob translation: {str(e)}")
        
        finally:
            # Clean up temporary files
            for temp_file in [temp_input_path, temp_output_path]:
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.unlink(temp_file)
                    except:
                        pass

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
            # Let Azure auto-detect content type by only providing filename and content
            document_translate_content = DocumentTranslateContent(
                document=(file_name, file_contents)
            )
            
            # Perform translation using Azure Document Translation API
            # The correct format requires target_language as keyword-only argument
            if source_language != "auto":
                response = client.translate(
                    document_translate_content,
                    target_language=target_language,
                    source_language=source_language
                )
            else:
                response = client.translate(
                    document_translate_content,
                    target_language=target_language
                )
            
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
    
    def _format_success_blob(self, input_blob_path: str, output_blob_path: str, blob_url: str, target_lang: str, result: str) -> str:
        """Format successful blob storage translation result."""
        input_filename = os.path.basename(input_blob_path.split('/')[-1])
        output_filename = os.path.basename(output_blob_path.split('/')[-1])
        
        return (
            f"✅ **Translation Successful (Blob Storage)**\n\n"
            f"**Input:** {input_filename} ({input_blob_path})\n"
            f"**Output:** {output_filename} ({output_blob_path})\n"
            f"**Language:** {target_lang}\n"
            f"**Blob URL:** {blob_url}\n\n"
            f"**Details:** {result}"
        )
    
    def _format_success_mixed(self, input_path: str, output_path: str, target_lang: str, output_type: str) -> str:
        """Format successful translation result with mixed storage types."""
        input_filename = os.path.basename(input_path.split('/')[-1])
        output_filename = os.path.basename(output_path)
        
        return (
            f"✅ **Translation Successful (Mixed Storage)**\n\n"
            f"**Input:** {input_filename} (blob storage)\n"
            f"**Output:** {output_filename} ({output_type} file)\n"
            f"**Language:** {target_lang}\n"
            f"**Location:** {output_path}\n\n"
            f"**Note:** Translated file saved locally from blob storage source."
        )
    
    def _get_documents_search_info(self) -> str:
        """Get information about Documents folder search for debugging."""
        candidates = self.docs_helper.get_documents_folders()
        search_info = "Searched paths:\n" + "\n".join([f"  • {path}" for path in candidates])
        
        search_info += f"\n\nSystem: {platform.system()}"
        search_info += f"\nUser home: {Path.home()}"
        
        return search_info