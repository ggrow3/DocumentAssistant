# Legal Document AI Assistant

A Streamlit application that helps law firms manage, process, and query their case documents using AI.

## Features

- **Document Management**: Upload, organize, and tag case documents
- **Document Processing**: Extract text from PDFs, Word documents, and images
- **AI-Powered Search**: Ask questions in natural language about your case documents
- **Citation Tracking**: See the exact sources for information provided by the AI
- **Tag-Based Organization**: Add and filter documents using tags
- **OCR Support**: Extract text from images and scanned PDFs
- **Multiple Vector Database Options**: Choose between Chroma (in-memory) or Pinecone (cloud-based)

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
- **pinecone_setup.py**: Helper script for Pinecone setup
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

## Vector Database Options

### Chroma (Default)
- In-memory vector database that works well for local usage
- Fast and easy to set up
- Data is not persisted between sessions

### Pinecone
- Cloud-based vector database for persistent storage
- Requires a Pinecone account and API key
- Good for larger document collections and persistence between sessions

To set up Pinecone:
1. Sign up for a [Pinecone account](https://www.pinecone.io/)
2. Create an API key from the Pinecone console
3. Run the setup script to create an index (optional):
   ```bash
   python pinecone_setup.py --api-key YOUR_API_KEY --environment YOUR_ENVIRONMENT
   ```
4. In the application settings, select "Pinecone" as the vector store type
5. Enter your API key and index information

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
- If using Pinecone, document embeddings are stored in your Pinecone account
- No document data is sent to external servers beyond what's needed for AI processing with OpenAI

## Requirements

- Python 3.8+
- OpenAI API key
- Pinecone API key (optional)
- Tesseract OCR (for image text extraction)

## License

This project is open source and available under the MIT License.