# AuditIQ Document Translator Tool

A standalone CrewAI tool for translating documents while preserving formatting using Azure AI Document Translation service. Supports both local files and Azure Blob Storage.

## Features

- **Format Preservation**: Maintains document structure, images, tables, and layout
- **Multi-language Support**: 90+ language pairs with automatic detection
- **Azure Blob Storage**: Native support for cloud-based document storage
- **Smart File Finding**: Cross-platform Documents folder detection and blob search
- **Flexible Storage**: Mix local files and blob storage as needed
- **User-friendly Interface**: Supports filenames, full paths, blob URLs, and blob paths
- **Language Flexibility**: Accepts language codes (es, fr) or names (spanish, french)
- **Cross-platform**: Works on Windows, macOS, and Linux

## Supported Document Types

- PDF documents (`.pdf`)
- Microsoft Word documents (`.docx`, `.doc`)

## Installation

### Prerequisites

- Python >= 3.10, < 3.14
- Azure Document Translation service account
- Azure Storage account (optional, for blob storage features)

### Quick Setup (Recommended)

```bash
# Clone or copy the tool directory
cd audit_iq_document_translator

# Run the automated setup script
python3 setup_and_test.py
```

The setup script will:
1. Check your Python version
2. Install dependencies (UV or pip)
3. Create .env file from template
4. Guide you through Azure setup
5. Run tests to verify everything works

### Manual Installation

```bash
# Install dependencies using UV (recommended)
uv sync

# Or install using pip
pip install -e .

# Copy environment template
cp .env.example .env
# Edit .env with your Azure credentials
```

### Quick Test

```bash
# Test your setup and translation functionality
python3 test_translation.py

# Translate local files and upload to blob storage
python3 translate_and_upload.py
```

## Configuration

### Azure Document Translation (Required)

Set up your Azure Document Translation credentials:

```bash
# Required for all document translation
export AZURE_DOCUMENT_TRANSLATION_ENDPOINT="https://your-service.cognitiveservices.azure.com/"
export AZURE_DOCUMENT_TRANSLATION_KEY="your-api-key"
```

### Azure Blob Storage (Optional)

For blob storage features, configure one of the following:

**Option 1: Connection String (Recommended)**
```bash
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net"
```

**Option 2: Account Name and Key**
```bash
export AZURE_STORAGE_ACCOUNT_NAME="yourstorageaccount"
export AZURE_STORAGE_ACCOUNT_KEY="yourstoragekey"
```

### Local Files (Optional)

```bash
# Optional: Custom Documents folder path for local file search
export DOCUMENTS_FOLDER_PATH="/path/to/your/documents"
```

## Usage

### Local Files

```python
from audit_iq_document_translator import AuditIqDocumentTranslator

# Initialize the tool
translator = AuditIqDocumentTranslator()

# Simple filename-based translation (searches Documents folder)
result = translator._run(
    file_path="report.pdf",
    target_language="spanish"
)

# Full path translation
result = translator._run(
    file_path="/path/to/document.pdf",
    target_language="es",
    source_language="en"
)

# With custom output path
result = translator._run(
    file_path="invoice.docx",
    target_language="french",
    output_file_path="invoice_fr.docx"
)
```

### Azure Blob Storage

The tool automatically detects blob storage paths and handles the translation seamlessly:

```python
# Using blob URL
result = translator._run(
    file_path="https://youraccount.blob.core.windows.net/documents/report.pdf",
    target_language="spanish"
)

# Using blob path notation (container/blob)
result = translator._run(
    file_path="documents/compliance_report.docx",
    target_language="french"
)

# Search by filename in blob storage
result = translator._run(
    file_path="annual_report.pdf",
    target_language="german",
    use_blob_storage=True  # Force blob storage mode
)

# Mixed storage: blob input, local output
result = translator._run(
    file_path="documents/contract.pdf",
    target_language="italian",
    output_file_path="/local/path/contratto.pdf"
)

# Blob input and output
result = translator._run(
    file_path="source/document.pdf",
    target_language="spanish",
    output_file_path="translated/documento_es.pdf"
)
```

### File Path Formats

The tool supports multiple input formats and automatically detects the appropriate storage method:

| Format | Example | Storage Type |
|--------|---------|--------------|
| Local filename | `report.pdf` | Local Documents folder search |
| Local full path | `/path/to/file.pdf` | Local filesystem |
| Blob URL | `https://account.blob.core.windows.net/container/file.pdf` | Azure Blob Storage |
| Blob path | `container/folder/file.pdf` | Azure Blob Storage |
| Force blob mode | Any filename + `use_blob_storage=True` | Azure Blob Storage |

### Language Options

You can specify target languages using:

**Language Codes** (2-3 letters):
- `es` (Spanish)
- `fr` (French)
- `de` (German)
- `it` (Italian)
- `pt` (Portuguese)
- `zh` (Chinese)
- `ja` (Japanese)
- `ko` (Korean)
- And many more...

**Language Names** (full names):
- `spanish`
- `french`
- `german`
- `italian`
- `portuguese`
- `chinese`
- `japanese`
- `korean`
- And many more...

### Documents Folder Detection

The tool automatically searches for your Documents folder in this order:

1. Custom path from `DOCUMENTS_FOLDER_PATH` environment variable
2. `./Documents` (project Documents folder)
3. `../Documents` (parent directory Documents folder)
4. `~/Documents` (user's Documents folder)
5. Platform-specific locations:
   - **Windows**: OneDrive Documents, legacy paths
   - **macOS**: iCloud Documents, legacy paths
   - **Linux**: XDG user directories

## Testing & Examples

### Quick Test

After setup, test the tool with the provided test script:

```bash
python3 test_tool.py
```

This will:
- Verify your credentials are configured
- Test tool initialization
- Test path detection for different storage types
- Show usage examples

### Testing with Real Files

1. **Local File Testing**:
   ```bash
   # Place a PDF or DOCX file in your Documents folder
   # Then run:
   python3 -c "
   from audit_iq_document_translator import AuditIqDocumentTranslator
   tool = AuditIqDocumentTranslator()
   result = tool._run('your_file.pdf', 'spanish')
   print(result)
   "
   ```

2. **Blob Storage Testing**:
   ```bash
   # Upload a file to your Azure Storage container first
   # Then test with blob path:
   python3 -c "
   from audit_iq_document_translator import AuditIqDocumentTranslator
   tool = AuditIqDocumentTranslator()
   result = tool._run('documents/your_file.pdf', 'french')
   print(result)
   "
   ```

### Code Examples

#### Simple Translation
```python
# Translate a PDF to Spanish (searches Documents folder automatically)
result = translator._run(
    file_path="audit_report.pdf",
    target_language="spanish"
)
```

#### Advanced Translation
```python
# Translate with specific source language and custom output
result = translator._run(
    file_path="/full/path/to/contract.docx",
    target_language="fr",
    source_language="en",
    output_file_path="/output/contrat_fr.docx"
)
```

#### Batch Translation
```python
# Translate multiple documents
documents = ["report1.pdf", "report2.docx", "summary.pdf"]
target_lang = "german"

for doc in documents:
    result = translator._run(
        file_path=doc,
        target_language=target_lang
    )
    print(result)
```

#### CrewAI Integration Example
```python
from crewai import Agent, Task, Crew
from audit_iq_document_translator import AuditIqDocumentTranslator

# Create translator agent
translator_agent = Agent(
    role="Document Translator",
    goal="Translate audit documents to multiple languages",
    backstory="Expert in multilingual document translation",
    tools=[AuditIqDocumentTranslator()],
    verbose=True
)

# Create translation task
task = Task(
    description="Translate contract.pdf to Spanish and French",
    agent=translator_agent,
    expected_output="Translation results for both languages"
)

# Run the crew
crew = Crew(agents=[translator_agent], tasks=[task])
result = crew.kickoff()
```

## Error Handling

The tool provides detailed error messages for common issues:

- **File not found**: Suggests similar files in the Documents folder
- **Unsupported format**: Lists supported file types
- **Missing credentials**: Guides you to set up environment variables
- **Permission errors**: Indicates access issues with files or directories

## API Reference

### AuditIqDocumentTranslator

#### Parameters

- `file_path` (str, required): Path to the document file. Can be:
  - **Local files**: `/path/to/document.pdf`, `./documents/file.docx`, `report.pdf`
  - **Blob URLs**: `https://account.blob.core.windows.net/container/file.pdf`
  - **Blob paths**: `container/folder/file.pdf`
  - **Filename search**: `report.pdf` (searches Documents folder or blob containers)

- `target_language` (str, required): Target language for translation
  - Language code: `es`, `fr`, `de`
  - Language name: `spanish`, `french`, `german`

- `source_language` (str, optional): Source language
  - Default: `auto` (automatic detection)
  - Language code: `en`, `es`, `fr`

- `output_file_path` (str, optional): Custom output path
  - **Local files**: `/path/to/output.pdf`
  - **Blob paths**: `translated/document_es.pdf`
  - **Blob URLs**: `https://account.blob.core.windows.net/translated/file.pdf`
  - Default: Auto-generated with language suffix in same location as input

- `use_blob_storage` (bool, optional): Force blob storage mode
  - Default: `False` (auto-detected from file_path)
  - Set to `True` to search blob storage for filename-only inputs

#### Return Value

Returns a formatted string with translation results:
- Success: Detailed information about the translated document
- Error: Specific error message with troubleshooting guidance

## Troubleshooting

### Common Issues

#### General Issues

1. **"Azure Document Translation credentials not configured"**
   - Set `AZURE_DOCUMENT_TRANSLATION_ENDPOINT` and `AZURE_DOCUMENT_TRANSLATION_KEY`

2. **"Unsupported file format"**
   - Only PDF, DOCX, and DOC files are supported
   - Ensure file has the correct extension

#### Local File Issues

3. **"File not found"**
   - Check if the file exists in the Documents folder
   - Use full path if file is in a different location
   - Check file permissions

4. **"Cannot find Documents folder"**
   - Set custom path using `DOCUMENTS_FOLDER_PATH` environment variable
   - Create a Documents folder in your project directory

#### Blob Storage Issues

5. **"Azure Blob Storage client not initialized"**
   - Set `AZURE_STORAGE_CONNECTION_STRING` or account name/key
   - Verify your storage account credentials

6. **"Blob not found"**
   - Check the container and blob path
   - Verify the blob exists in your storage account
   - Ensure correct container permissions

7. **"Upload failed"**
   - Check write permissions to the destination container
   - Verify storage account has sufficient space
   - Check network connectivity

### Debug Information

The tool provides detailed debug information for troubleshooting:
- Searched folder paths
- Available files in Documents folder
- System information
- File validation results

## Development

### Project Structure

```
audit_iq_document_translator/
├── README.md
├── pyproject.toml
├── src/
│   └── audit_iq_document_translator/
│       ├── __init__.py
│       └── tool.py
├── tests/
│   ├── __init__.py
│   └── test_tool.py
├── examples/
│   ├── __init__.py
│   └── example_usage.py
└── uv.lock
```

### Running Tests

```bash
# Install test dependencies
uv sync --dev

# Run tests
python -m pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This tool is part of the AuditIQ project and follows the same licensing terms.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the Azure Document Translation documentation
3. Open an issue in the project repository