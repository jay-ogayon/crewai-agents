#!/usr/bin/env python3
"""
Simple script to translate local documents and upload to blob storage.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def load_env():
    """Load environment variables."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

def main():
    """Translate documents and upload to blob storage."""
    print("🚀 Document Translation & Upload")
    print("=" * 35)
    
    load_env()
    
    # Check basic setup
    if not (os.getenv("AZURE_DOCUMENT_TRANSLATION_ENDPOINT") and 
            os.getenv("AZURE_DOCUMENT_TRANSLATION_KEY")):
        print("❌ Missing Azure Document Translation credentials")
        return
    
    try:
        from audit_iq_document_translator import AuditIqDocumentTranslator
        tool = AuditIqDocumentTranslator()
        print("✅ Tool initialized")
    except Exception as e:
        print(f"❌ Tool initialization failed: {e}")
        return
    
    # Files to translate
    docs_folder = Path(__file__).parent / "documents"
    target_languages = ["spanish", "french"]
    
    if not docs_folder.exists():
        print(f"❌ Documents folder not found: {docs_folder}")
        return
    
    # Find files
    supported_extensions = {'.pdf', '.docx', '.doc'}
    files = [f for f in docs_folder.iterdir() 
             if f.is_file() and f.suffix.lower() in supported_extensions]
    
    if not files:
        print("❌ No translatable files found")
        return
    
    print(f"📁 Found {len(files)} files to translate")
    
    # Process each file
    for file_path in files:
        print(f"\n📄 Processing: {file_path.name}")
        
        for target_lang in target_languages:
            print(f"   🔄 Translating to {target_lang}...")
            
            try:
                result = tool._run(
                    file_path=str(file_path),
                    target_language=target_lang
                )
                
                if "successfully translated" in result.lower():
                    print(f"   ✅ Translation to {target_lang} completed")
                    
                    # Extract output file and upload to blob storage
                    for line in result.split('\n'):
                        if "output saved to:" in line.lower():
                            output_file = line.split(":")[-1].strip().split()[0]
                            if os.path.exists(output_file):
                                try:
                                    # Upload to blob storage
                                    blob_filename = os.path.basename(output_file)
                                    blob_path = f"translated/{blob_filename}"
                                    
                                    blob_url = tool.blob_helper.upload_file_to_blob(
                                        output_file, blob_path, overwrite=True
                                    )
                                    print(f"   📤 Uploaded to: {blob_path}")
                                    
                                except Exception as e:
                                    print(f"   ⚠️  Upload failed: {e}")
                            break
                else:
                    print(f"   ❌ Translation to {target_lang} failed")
                    if "format parameter" in result:
                        print("      (PDF format issue - known limitation)")
            
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print(f"\n🎉 Processing completed!")
    print("Check your blob storage 'translated' container for results")

if __name__ == "__main__":
    main()