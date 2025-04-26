import streamlit as st
import os
import pytesseract
from document_processing import process_document, parse_tags
from vector_store import initialize_vectorstore
from utils import format_tags_html, add_tags_to_document, remove_tag_from_document, debug_document_format, test_retriever_functionality
from sidebar_components import document_uploader, document_list, ocr_settings, tag_manager

def build_sidebar():
    """Build the sidebar interface with document management and settings"""
    with st.sidebar:
        st.header("Personal Injury Law Assistant")
        
        # Tabs for sidebar content
        sidebar_tabs = ["Document Management", "Settings"]
        selected_tab = st.radio("Select tab", sidebar_tabs)
        
        if selected_tab == "Document Management":
            build_document_management()
        
        elif selected_tab == "Settings":
            build_settings_panel()

def build_document_management():
    """Build the document management interface in the sidebar"""
    st.markdown("### Upload Documents")
    
    # Document upload section
    doc_type, case_id, doc_title, tags, uploaded_file = document_uploader()
    
    # OCR settings
    ocr_settings()
    
    # Process document button
    if uploaded_file is not None:
        if st.button("Process Document"):
            process_uploaded_document(uploaded_file, doc_type, case_id, doc_title, tags)
    
    # Show uploaded documents
    if st.session_state.documents:
        document_list()

def process_uploaded_document(uploaded_file, doc_type, case_id, doc_title, tags):
    """Process an uploaded document and add it to the knowledge base"""
    with st.spinner("Processing document..."):
        document = process_document(uploaded_file, doc_type, case_id, doc_title, tags)
        
        if document:
            st.session_state.documents.append(document)
            st.success(f"Successfully processed {document['title']}")
            
            # Reinitialize vectorstore
            try:
                with st.spinner("Updating knowledge base..."):
                    # Debug mode - show document format if there's an issue
                    debug_mode = st.session_state.get("debug_mode", False)
                    if debug_mode:
                        st.write("### Document Format Debug")
                        debug_document_format(st.session_state.documents)
                    
                    st.session_state.vectorstore = initialize_vectorstore(st.session_state.documents)
                    
                    if st.session_state.vectorstore:
                        st.success("Knowledge base updated!")
                    else:
                        st.error("Failed to create vector store. Check document formats.")
            except Exception as e:
                st.error(f"Error updating knowledge base: {str(e)}")
                st.info("Try reinstalling Chromadb or check the error message for details.")
                
                # Enable debug mode automatically when there's an error
                st.session_state.debug_mode = True
                st.warning("Debug mode enabled. Please try again to see document format details.")
        else:
            st.error("Failed to process document")

def build_settings_panel():
    """Build the settings panel in the sidebar"""
    st.markdown("### API Settings")
    
    # API settings
    api_settings()
    
    # Model settings
    model_settings()
    
    # OCR settings
    st.markdown("### OCR Settings")
    
    # Path to Tesseract executable (Windows only)
    if os.name == 'nt':  # Windows
        tesseract_path = st.text_input(
            "Tesseract Path", 
            value="C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
            help="Path to tesseract.exe (Windows only)"
        )
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    # Tag management
    st.markdown("### Tag Management")
    tag_manager()
    
    # Debug mode toggle
    debug_settings()

def api_settings():
    """API key settings"""
    # OpenAI API Key input
    openai_api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key here. It's required for embeddings and the chat model."
    )
    
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key

def model_settings():
    """LLM model settings"""
    st.markdown("### Model Settings")
    
    model_name = st.selectbox(
        "Chat Model",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"]
    )
    
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher values make the model more creative but less predictable"
    )
    
    # Save settings in session state
    if "settings" not in st.session_state:
        st.session_state.settings = {}
    
    st.session_state.settings["model_name"] = model_name
    st.session_state.settings["temperature"] = temperature

def debug_settings():
    """Debug mode settings"""
    st.markdown("### Debug Settings")
    debug_mode = st.checkbox("Enable Debug Mode", 
                          value=st.session_state.get("debug_mode", False),
                          help="Shows additional diagnostic information when errors occur")
    st.session_state.debug_mode = debug_mode
    
    if debug_mode:
        build_debug_panel()

def build_debug_panel():
    """Build the debug panel in the settings sidebar"""
    st.info("Debug mode is enabled. Document format information will be displayed when processing documents.")
    
    # Add a button to test document formats
    if st.button("Debug Document Formats") and st.session_state.documents:
        st.write("### Document Format Debug")
        debug_document_format(st.session_state.documents)
    
    # Add a button to test retriever functionality
    if st.session_state.vectorstore:
        st.write("### Retriever Functionality Test")
        test_query = st.text_input("Test query", value="test query")
        if st.button("Run Test Query"):
            test_retriever_functionality(st.session_state.vectorstore, test_query)