# Personal Injury Law Firm AI Assistant

A Streamlit application that helps personal injury law firms manage, process, and query their case documents using AI.

## Features

- **Document Management**: Upload, organize, and tag case documents
- **Document Processing**: Extract text from PDFs, Word documents, and images
- **AI-Powered Search**: Ask questions in natural language about your case documents
- **Citation Tracking**: See the exact sources for information provided by the AI
- **Tag-Based Organization**: Add and filter documents using tags
- **OCR Support**: Extract text from images and scanned PDFs

## Project Structure

- **app.py**: Main application entry point
- **sidebar.py**: Sidebar interface with document management and settings
- **chat_interface.py**: Chat interface and processing
- **document_context.py**: Document context panel display
- **about_page.py**: About page content
- **system_check.py**: System dependency checking
- **document_processing.py**: Document extraction and processing
- **vector_store.py**: Vector database and embedding functionality
- **citation_handler.py**: Citation tracking functionality
- **ui_components.py**: UI components and styling
- **utils.py**: Utility functions
- **requirements.txt**: Dependencies

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. For OCR functionality (optional but recommended):
   - Install Tesseract OCR on your system ([Windows](https://github.com/UB-Mannheim/tesseract/wiki) | [macOS](https://brew.sh/) `brew install tesseract` | Linux `apt-get install tesseract-ocr`)
   - For enhanced PDF OCR:
     ```bash
     pip install PyMuPDF
     ```
     or
     ```bash
     pip install pdf2image
     # On Ubuntu/Debian: sudo apt-get install poppler-utils
     # On macOS: brew install poppler
     ```

## Usage

1. Run the Streamlit app:

```bash
streamlit run app.py
```

2. Open your browser and navigate to the provided URL (typically http://localhost:8501)

3. Enter your OpenAI API key in the Settings tab (sidebar)

4. Upload and process documents in the Document Management tab (sidebar)

5. Use the chat interface to ask questions about your documents

## Document Types Supported

- PDF files (.pdf)
- Word documents (.docx, .doc)
- Text files (.txt)
- Images with text (.jpg, .jpeg, .png)

## Advanced Features

### Tag-Based Search

You can search for documents with specific tags using:
- `tag:important` in your queries
- `#important` in your queries

### OCR Settings

OCR settings can be configured in the sidebar for better text extraction from images and scanned PDFs.

## Privacy & Security

- All documents are processed locally
- Your OpenAI API key is stored only in your current session
- No document data is sent to external servers beyond what's needed for AI processing with OpenAI

## Requirements

- Python 3.8+
- OpenAI API key
- Tesseract OCR (for image text extraction)

## License

This project is open source and available under the MIT License.