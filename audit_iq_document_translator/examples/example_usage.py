#!/usr/bin/env python3
"""
Example usage of the AuditIQ Document Translator Tool

This script demonstrates how to use the document translation tool
in various scenarios.
"""

import os
from pathlib import Path
from audit_iq_document_translator import AuditIqDocumentTranslator


def setup_environment():
    """
    Setup environment variables for Azure Document Translation.
    
    Note: In a real application, these should be set in your environment
    or loaded from a secure configuration file, not hardcoded.
    """
    # These are example values - replace with your actual Azure credentials
    os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"] = "https://your-service.cognitiveservices.azure.com/"
    os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"] = "your-document-translation-api-key"
    
    # Optional: Set custom Documents folder path
    # os.environ["DOCUMENTS_FOLDER_PATH"] = "/path/to/your/documents"


def example_simple_translation():
    """
    Example 1: Simple translation using filename only
    
    This will search for the file in the Documents folder automatically.
    """
    print("=== Example 1: Simple Translation ===")
    
    translator = AuditIqDocumentTranslator()
    
    # Translate a PDF to Spanish
    result = translator._run(
        file_path="sample_report.pdf",  # File in Documents folder
        target_language="spanish"
    )
    
    print("Result:", result)
    print()


def example_language_variations():
    """
    Example 2: Different ways to specify languages
    """
    print("=== Example 2: Language Variations ===")
    
    translator = AuditIqDocumentTranslator()
    
    # Using language codes
    print("Using language code 'es':")
    result = translator._run(
        file_path="document.pdf",
        target_language="es"
    )
    print("Result:", result)
    
    # Using language names
    print("\nUsing language name 'french':")
    result = translator._run(
        file_path="document.pdf",
        target_language="french"
    )
    print("Result:", result)
    print()


def example_full_path_translation():
    """
    Example 3: Translation using full file paths
    """
    print("=== Example 3: Full Path Translation ===")
    
    translator = AuditIqDocumentTranslator()
    
    # Using absolute path
    result = translator._run(
        file_path="/absolute/path/to/contract.docx",
        target_language="german",
        source_language="english"
    )
    
    print("Result:", result)
    print()


def example_custom_output_path():
    """
    Example 4: Translation with custom output path
    """
    print("=== Example 4: Custom Output Path ===")
    
    translator = AuditIqDocumentTranslator()
    
    result = translator._run(
        file_path="invoice.pdf",
        target_language="italian",
        source_language="auto",
        output_file_path="translated_documents/fattura_italiana.pdf"
    )
    
    print("Result:", result)
    print()


def example_batch_translation():
    """
    Example 5: Batch translation of multiple documents
    """
    print("=== Example 5: Batch Translation ===")
    
    translator = AuditIqDocumentTranslator()
    
    # List of documents to translate
    documents = [
        "audit_report_2024.pdf",
        "compliance_checklist.docx",
        "financial_summary.pdf"
    ]
    
    target_language = "spanish"
    
    for document in documents:
        print(f"Translating {document}...")
        result = translator._run(
            file_path=document,
            target_language=target_language
        )
        
        # Check if translation was successful
        if "successfully translated" in result.lower():
            print(f"✅ {document} translated successfully")
        else:
            print(f"❌ Failed to translate {document}")
            print(f"   Error: {result}")
        print()


def example_error_handling():
    """
    Example 6: Error handling and troubleshooting
    """
    print("=== Example 6: Error Handling ===")
    
    translator = AuditIqDocumentTranslator()
    
    # Try to translate a non-existent file
    print("Attempting to translate non-existent file:")
    result = translator._run(
        file_path="non_existent_file.pdf",
        target_language="french"
    )
    print("Result:", result)
    
    # Try with unsupported file format
    print("\nAttempting to translate unsupported file format:")
    result = translator._run(
        file_path="document.txt",  # Unsupported format
        target_language="spanish"
    )
    print("Result:", result)
    
    # Try with invalid language
    print("\nAttempting to use invalid language:")
    result = translator._run(
        file_path="document.pdf",
        target_language="klingon"  # Invalid language
    )
    print("Result:", result)
    print()


def example_multilingual_translation():
    """
    Example 7: Translating the same document to multiple languages
    """
    print("=== Example 7: Multilingual Translation ===")
    
    translator = AuditIqDocumentTranslator()
    
    source_document = "policy_document.pdf"
    target_languages = ["spanish", "french", "german", "italian", "portuguese"]
    
    print(f"Translating {source_document} to multiple languages...")
    
    for language in target_languages:
        print(f"Translating to {language}...")
        result = translator._run(
            file_path=source_document,
            target_language=language
        )
        
        if "successfully translated" in result.lower():
            print(f"✅ {language} translation completed")
        else:
            print(f"❌ {language} translation failed")
        print()


def example_crewai_integration():
    """
    Example 8: Using the tool in a CrewAI workflow
    """
    print("=== Example 8: CrewAI Integration ===")
    
    # This shows how you would integrate the tool into a CrewAI crew
    from crewai import Agent, Task, Crew
    
    # Create a translation agent
    translator_agent = Agent(
        role="Document Translator",
        goal="Translate audit and compliance documents to different languages",
        backstory="You are an expert in document translation specializing in audit and compliance materials.",
        tools=[AuditIqDocumentTranslator()],
        verbose=True
    )
    
    # Create a translation task
    translation_task = Task(
        description="""
        Translate the following documents to Spanish:
        1. audit_report.pdf
        2. compliance_guidelines.docx
        
        Ensure that all formatting and structure is preserved.
        """,
        agent=translator_agent,
        expected_output="A summary of the translation results for each document"
    )
    
    # Create and run the crew
    translation_crew = Crew(
        agents=[translator_agent],
        tasks=[translation_task],
        verbose=True
    )
    
    print("CrewAI integration example prepared.")
    print("In a real scenario, you would run: translation_crew.kickoff()")
    print()


def main():
    """
    Main function to run all examples
    """
    print("AuditIQ Document Translator Tool - Usage Examples")
    print("=" * 50)
    
    # Setup environment (you would do this once in your application)
    setup_environment()
    
    # Run examples
    try:
        example_simple_translation()
        example_language_variations()
        example_full_path_translation()
        example_custom_output_path()
        example_batch_translation()
        example_error_handling()
        example_multilingual_translation()
        example_crewai_integration()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have set up your Azure Document Translation credentials.")
    
    print("Examples completed!")


if __name__ == "__main__":
    main()