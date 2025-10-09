# AuditIQ Document Translator Tool

A standalone CrewAI tool for translating documents while preserving formatting using Azure AI Document Translation service.

## Features

- **Format Preservation**: Maintains document structure, images, tables, and layout
- **Multi-language Support**: 90+ language pairs with automatic detection
- **Smart File Finding**: Cross-platform Documents folder detection
- **User-friendly Interface**: Supports both filenames and full paths
- **Language Flexibility**: Accepts language codes (es, fr) or names (spanish, french)
- **Cross-platform**: Works on Windows, macOS, and Linux

## Supported Document Types

- PDF documents (`.pdf`)
- Microsoft Word documents (`.docx`, `.doc`)

## Installation

### Prerequisites

- Python >= 3.10, < 3.14
- Azure Document Translation service account

### Install the Tool

```bash
# Clone or copy the tool directory
cd audit_iq_document_translator

# Install dependencies using UV (recommended)
uv sync

# Or install using pip
pip install -e .
```

## Configuration

Set up your Azure Document Translation credentials as environment variables:

```bash
# Required environment variables
export AZURE_DOCUMENT_TRANSLATION_ENDPOINT="https://your-service.cognitiveservices.azure.com/"
export AZURE_DOCUMENT_TRANSLATION_KEY="your-api-key"

# Optional: Custom Documents folder path
export DOCUMENTS_FOLDER_PATH="/path/to/your/documents"
```

## Usage

### As a CrewAI Tool

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

## Examples

### Simple Translation
```python
# Translate a PDF to Spanish (searches Documents folder automatically)
result = translator._run(
    file_path="audit_report.pdf",
    target_language="spanish"
)
```

### Advanced Translation
```python
# Translate with specific source language and custom output
result = translator._run(
    file_path="/full/path/to/contract.docx",
    target_language="fr",
    source_language="en",
    output_file_path="/output/contrat_fr.docx"
)
```

### Batch Translation
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
  - Full absolute path: `/path/to/document.pdf`
  - Relative path: `./documents/file.docx`
  - Filename only: `report.pdf` (searches Documents folder)

- `target_language` (str, required): Target language for translation
  - Language code: `es`, `fr`, `de`
  - Language name: `spanish`, `french`, `german`

- `source_language` (str, optional): Source language
  - Default: `auto` (automatic detection)
  - Language code: `en`, `es`, `fr`

- `output_file_path` (str, optional): Custom output path
  - Default: Auto-generated with language suffix
  - Example: `document_es.pdf`

#### Return Value

Returns a formatted string with translation results:
- Success: Detailed information about the translated document
- Error: Specific error message with troubleshooting guidance

## Troubleshooting

### Common Issues

1. **"Azure Document Translation credentials not configured"**
   - Set `AZURE_DOCUMENT_TRANSLATION_ENDPOINT` and `AZURE_DOCUMENT_TRANSLATION_KEY`

2. **"File not found"**
   - Check if the file exists in the Documents folder
   - Use full path if file is in a different location
   - Check file permissions

3. **"Unsupported file format"**
   - Only PDF, DOCX, and DOC files are supported
   - Ensure file has the correct extension

4. **"Cannot find Documents folder"**
   - Set custom path using `DOCUMENTS_FOLDER_PATH` environment variable
   - Create a Documents folder in your project directory

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