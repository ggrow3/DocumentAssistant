import streamlit as st

def about_page():
    """Display the about page with information about the application"""
    st.markdown("""
    # About Personal Injury Law Firm AI Assistant
    
    This AI assistant is designed specifically for personal injury law firms to help manage and search through case documents.
    
    ## Features
    
    - **Document Management**: Upload and organize documents related to personal injury cases
    - **AI-Powered Search**: Get relevant information from your documents using natural language questions
    - **Citation Tracking**: See the exact sources the AI uses to answer your questions
    - **Document Context**: View the full context of referenced documents
    - **OCR Processing**: Extract text from images and PDFs with embedded images
    - **Document Tagging**: Add tags to documents for better organization and search
    
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
    
    ## Privacy & Security
    
    All documents are processed locally and are not sent to external servers beyond what's needed for AI processing. Your OpenAI API key is stored only in your current session.
    """)