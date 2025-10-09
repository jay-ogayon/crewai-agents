#!/usr/bin/env python3
"""
Test the complete blob storage workflow:
1. Search for files by filename in blob storage
2. Translate found files
3. Upload translated results back to blob storage
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

def test_blob_search_workflow():
    """Test the complete blob storage search and translate workflow."""
    print("🧪 Testing Blob Storage Search & Translate Workflow")
    print("=" * 55)
    
    load_env()
    
    try:
        from audit_iq_document_translator import AuditIqDocumentTranslator
        tool = AuditIqDocumentTranslator()
        print("✅ Tool initialized")
    except Exception as e:
        print(f"❌ Tool initialization failed: {e}")
        return False
    
    # Test 1: List available files in blob storage
    print("\n📂 Step 1: Scanning blob storage for available files...")
    
    try:
        blob_helper = tool.blob_helper
        if not blob_helper.blob_service_client:
            print("❌ Blob storage not configured")
            return False
        
        # List containers and files
        containers = list(blob_helper.blob_service_client.list_containers())
        available_files = []
        
        for container in containers:
            print(f"   📁 Container: {container.name}")
            try:
                container_client = blob_helper.blob_service_client.get_container_client(container.name)
                blobs = list(container_client.list_blobs())
                
                for blob in blobs:
                    if Path(blob.name).suffix.lower() in blob_helper.supported_extensions:
                        blob_path = f"{container.name}/{blob.name}"
                        available_files.append((blob.name, blob_path))
                        print(f"      📄 {blob.name}")
            except Exception as e:
                print(f"      ❌ Error listing blobs: {e}")
        
        if not available_files:
            print("⚠️  No translatable files found in blob storage")
            return False
        
        print(f"✅ Found {len(available_files)} translatable files")
        
    except Exception as e:
        print(f"❌ Error scanning blob storage: {e}")
        return False
    
    # Test 2: Search for specific filenames
    print("\n🔍 Step 2: Testing filename search...")
    
    # Test with actual filenames from blob storage
    test_filenames = [file[0] for file in available_files[:2]]  # Test first 2 files
    
    for filename in test_filenames:
        print(f"   Searching for: {filename}")
        found_path = blob_helper.find_blob_by_filename(filename)
        
        if found_path:
            print(f"   ✅ Found: {found_path}")
        else:
            print(f"   ❌ Not found: {filename}")
    
    # Test 3: Complete workflow - search and translate
    print("\n🔄 Step 3: Testing complete search + translate + upload workflow...")
    
    if available_files:
        # Take the first available file
        test_filename, test_blob_path = available_files[0]
        target_language = "spanish"
        
        print(f"   Testing with: {test_filename}")
        print(f"   Target language: {target_language}")
        
        try:
            # This should:
            # 1. Find the file in blob storage by filename
            # 2. Download it temporarily
            # 3. Translate it
            # 4. Upload the result to translated container
            result = tool._run(
                file_path=test_filename,  # Just filename - should search blob storage
                target_language=target_language,
                use_blob_storage=True  # Force blob storage mode
            )
            
            print(f"   Result: {result[:200]}...")
            
            if "successfully translated" in result.lower():
                print("   ✅ Complete workflow successful!")
                
                # Check if it mentions blob storage upload
                if "blob" in result.lower() and "translated" in result.lower():
                    print("   ✅ File uploaded to blob storage")
                else:
                    print("   ⚠️  Translation successful but upload status unclear")
                
                return True
                
            elif "not found" in result.lower():
                print("   ❌ File search failed")
                return False
            else:
                print("   ❌ Translation failed")
                print(f"      Error: {result}")
                return False
                
        except Exception as e:
            print(f"   ❌ Workflow error: {e}")
            return False
    
    return False

def test_direct_blob_path():
    """Test direct blob path translation."""
    print("\n🎯 Step 4: Testing direct blob path translation...")
    
    try:
        from audit_iq_document_translator import AuditIqDocumentTranslator
        tool = AuditIqDocumentTranslator()
        
        # List a file from blob storage
        blob_helper = tool.blob_helper
        containers = list(blob_helper.blob_service_client.list_containers())
        
        for container in containers:
            if container.name != 'translated':  # Don't translate already translated files
                try:
                    container_client = blob_helper.blob_service_client.get_container_client(container.name)
                    blobs = list(container_client.list_blobs())
                    
                    for blob in blobs:
                        if Path(blob.name).suffix.lower() in ['.docx']:  # Test with DOCX
                            blob_path = f"{container.name}/{blob.name}"
                            print(f"   Testing direct path: {blob_path}")
                            
                            result = tool._run(
                                file_path=blob_path,
                                target_language="french"
                            )
                            
                            if "successfully translated" in result.lower():
                                print("   ✅ Direct blob path translation successful!")
                                return True
                            else:
                                print(f"   ❌ Direct translation failed: {result[:100]}...")
                            
                            break  # Test only one file
                    break  # Test only one container
                except Exception as e:
                    continue
        
        print("   ⚠️  No suitable files found for direct path test")
        return False
        
    except Exception as e:
        print(f"   ❌ Direct path test error: {e}")
        return False

def main():
    """Main test function."""
    success1 = test_blob_search_workflow()
    success2 = test_direct_blob_path()
    
    print(f"\n📊 Test Results:")
    print(f"   Filename search workflow: {'✅ Success' if success1 else '❌ Failed'}")
    print(f"   Direct blob path workflow: {'✅ Success' if success2 else '❌ Failed'}")
    
    if success1 and success2:
        print("\n🎉 All blob storage workflows are working correctly!")
        print("   The tool is ready for CrewAI integration")
        return True
    else:
        print("\n⚠️  Some workflows need attention")
        return False

if __name__ == "__main__":
    main()