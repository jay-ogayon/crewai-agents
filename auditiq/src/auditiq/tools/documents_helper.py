import os
import platform
from pathlib import Path
from typing import Optional, List, Tuple
import re

class CrossPlatformDocumentsHelper:
    """
    Cross-platform helper for finding and managing documents in the Documents folder.
    Works seamlessly on Mac, Windows, and Linux systems.
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.supported_extensions = {'.pdf', '.docx', '.doc'}
    
    def get_documents_folders(self) -> List[Path]:
        """
        Get potential Documents folder locations in priority order.
        Returns list of Path objects to check.
        """
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
            # Windows specific paths
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
            # macOS specific paths
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
        
        # 6. Linux/Unix fallbacks
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
        """
        Find the first existing and accessible Documents folder.
        Returns None if no valid Documents folder is found.
        """
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
        """
        Find a file in the Documents folder using case-insensitive search.
        
        Args:
            filename: Name of the file to find (with or without extension)
            documents_folder: Specific Documents folder to search (auto-detected if None)
        
        Returns:
            Path to the found file, or None if not found
        """
        if documents_folder is None:
            documents_folder = self.find_documents_folder()
        
        if not documents_folder:
            return None
        
        return self._search_file_in_directory(filename, documents_folder)
    
    def _search_file_in_directory(self, filename: str, directory: Path) -> Optional[Path]:
        """
        Search for a file in the given directory with case-insensitive matching.
        Supports partial matches and automatic extension detection.
        """
        if not directory.exists() or not directory.is_dir():
            return None
        
        # Normalize the search filename
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
    
    def list_supported_files(self, documents_folder: Optional[Path] = None) -> List[Tuple[str, Path]]:
        """
        List all supported files in the Documents folder.
        
        Returns:
            List of tuples: (filename, full_path)
        """
        if documents_folder is None:
            documents_folder = self.find_documents_folder()
        
        if not documents_folder or not documents_folder.exists():
            return []
        
        supported_files = []
        
        try:
            for file_path in documents_folder.iterdir():
                if (file_path.is_file() and 
                    file_path.suffix.lower() in self.supported_extensions):
                    supported_files.append((file_path.name, file_path))
        except (PermissionError, OSError):
            pass
        
        return sorted(supported_files, key=lambda x: x[0].lower())
    
    def validate_file_access(self, file_path: Path) -> Tuple[bool, str]:
        """
        Validate that a file exists and is accessible.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
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
        """
        Generate a suggested output path for the translated document.
        Places the translated file in the same directory with language suffix.
        """
        directory = input_path.parent
        name_without_ext = input_path.stem
        extension = input_path.suffix
        
        # Create output filename with language suffix
        output_name = f"{name_without_ext}_{target_language}{extension}"
        return directory / output_name
    
    def get_system_info(self) -> dict:
        """Get system information for debugging."""
        docs_folder = self.find_documents_folder()
        candidates = self.get_documents_folders()
        
        return {
            "system": platform.system(),
            "platform": platform.platform(),
            "documents_folder": str(docs_folder) if docs_folder else None,
            "documents_folder_exists": docs_folder.exists() if docs_folder else False,
            "searched_paths": [str(p) for p in candidates],
            "user_home": str(Path.home()),
            "supported_extensions": list(self.supported_extensions)
        }