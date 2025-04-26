import streamlit as st

def about_page():
    """Display the about page with information about the application"""
    st.markdown("""
    # About Legal Document AI Assistant
    
    This AI assistant is designed specifically for legal documents to help manage and search through case documents.
    
    ## Features
    
    - **Document Management**: Upload and organize documents related to personal injury cases
    - **AI-Powered Search**: Get relevant information from your documents using natural language questions
    - **Citation Tracking**: See the exact sources the AI uses to answer your questions
    - **Document Context**: View the full context of referenced documents
    - **OCR Processing**: Extract text from images and PDFs with embedded images
    - **Document Tagging**: Add tags to documents for better organization and search
    - **Vector Database Options**: Choose between Chroma (in-memory) and Pinecone (cloud-based) for document storage
    
    ## How to Use
    
    1. Upload your case documents in the sidebar
    2. Add tags to categorize and organize your documents
    3. Ask questions about your cases in the chat interface
    4. The AI will search through your documents and provide relevant answers with citations
    5. Search by tag using syntax like "tag:important" or "#important" in your questions
    
    ## Document Types Supported
    
    - PDF files
    - Word documents (.docx, .doc)
    - Text files (.txt)
    - Images with text (.jpg, .jpeg, .png) using OCR
    
    ## Vector Database Options
    
    - **Chroma (Default)**: Fast, in-memory vector database that works well for local usage
    - **Pinecone**: Cloud-based vector database for persistent storage and larger document collections
    
    ## Privacy & Security
    
    All documents are processed locally and are not sent to external servers beyond what's needed for AI processing. Your OpenAI API key and Pinecone API key are stored only in your current session.
    
    When using Pinecone, document embeddings are stored in your Pinecone account, which provides additional persistence between sessions.
    """)