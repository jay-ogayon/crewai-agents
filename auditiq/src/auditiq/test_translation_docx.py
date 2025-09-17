import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import SingleDocumentTranslationClient
from azure.ai.translation.document.models import DocumentTranslateContent


def sample_single_document_translation():

    # create variables for your resource api key, document translation endpoint, and target language
    key = os.getenv("AZURE_TRANSLATION_KEY", "your-azure-translation-key-here")
    endpoint = "https://translator-sp-eng.cognitiveservices.azure.com/"
    target_language = "el"

    # initialize a new instance of the DocumentTranslationClient object to interact with the synchronous Document Translation feature
    client = SingleDocumentTranslationClient(endpoint, AzureKeyCredential(key))
    
    # absolute path to your document
    file_path = "/Users/ferdinanda/Downloads/AuditIQ - Copy/document-translation-sample.docx"
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return
    
    file_name = os.path.basename(file_path)
    print(f"File for translation: {file_name}")
    
    try:
        # Read the document file
        with open(file_path, "rb") as document:
            document_content = document.read()
            
        # Create translation content (file_name, file_contents, content_type)
        file_name_base = os.path.basename(file_path)
        document_content_tuple = (file_name_base, document_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        translate_content = DocumentTranslateContent(document=document_content_tuple)
        
        # Perform the translation
        response = client.translate(
            body=translate_content,
            target_language=target_language
        )
        
        # Save the translated document
        output_path = f"/Users/ferdinanda/Downloads/AuditIQ - Copy/translated-{file_name}"
        with open(output_path, "wb") as output_file:
            output_file.write(response)
            
        print(f"Translation completed successfully!")
        print(f"Translated document saved to: {output_path}")
        
    except Exception as e:
        print(f"Translation failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    sample_single_document_translation()