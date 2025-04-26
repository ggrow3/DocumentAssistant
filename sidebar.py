import streamlit as st
import os
import pytesseract
from document_processing import process_document, parse_tags
from vector_store import initialize_vectorstore
from utils import format_tags_html, add_tags_to_document, remove_tag_from_document, debug_document_format, test_retriever_functionality

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
    
    # Document inputs
    doc_type = st.selectbox(
        "Document Type",
        ["Deposition", "Demand Letter", "Medical Record", "Police Report", "Expert Opinion", "Court Filing", "Other"]
    )
    
    case_id = st.text_input("Case ID (Optional)")
    doc_title = st.text_input("Document Title (Optional)")
    
    # Tags input
    tags_input = st.text_input(
        "Tags (comma-separated)", 
        help="Add tags separated by commas, e.g., important, needs-review, client-requested"
    )
    tags = parse_tags(tags_input)
    
    # Display preview of selected tags
    if tags:
        st.markdown(format_tags_html(tags), unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload Document",
        type=["pdf", "docx", "doc", "txt", "jpg", "jpeg", "png"],
        help="Upload PDFs, Word documents, or images to add them to the knowledge base"
    )
    
    # OCR settings
    with st.expander("OCR Settings"):
        perform_ocr = st.checkbox("Enable OCR for images", value=True, 
                                help="Extract text from images using Optical Character Recognition")
        
        if perform_ocr:
            st.info("OCR is enabled for images and PDFs with embedded images.")
            
            # Additional OCR library info
            st.markdown("""
            **Note**: For improved PDF OCR, install additional libraries:
            ```
            pip install PyMuPDF
            ```
            or
            ```
            pip install pdf2image poppler-utils
            ```
            """)
    
    # Process document button
    if uploaded_file is not None:
        if st.button("Process Document"):
            process_uploaded_document(uploaded_file, doc_type, case_id, doc_title, tags)
    
    # Show uploaded documents
    if st.session_state.documents:
        display_uploaded_documents()

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

def display_uploaded_documents():
    """Display the uploaded documents with filtering options"""
    st.markdown("### Uploaded Documents")
    
    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        filter_case = st.text_input("Filter by Case ID", key="filter_case_id")
    with col2:
        filter_type = st.selectbox(
            "Filter by Document Type",
            ["All"] + ["Deposition", "Demand Letter", "Medical Record", "Police Report", "Expert Opinion", "Court Filing", "Other"]
        )
    
    # Tag filter
    if st.session_state.tags:
        tag_list = list(st.session_state.tags)
        tag_list.sort()
        selected_tags = st.multiselect(
            "Filter by Tags",
            tag_list,
            help="Select one or more tags to filter documents"
        )
    
    # Apply filters
    filtered_docs = st.session_state.documents
    if filter_case:
        filtered_docs = [doc for doc in filtered_docs if filter_case.lower() in doc["case_id"].lower()]
    if filter_type != "All":
        filtered_docs = [doc for doc in filtered_docs if doc["type"] == filter_type]
    if st.session_state.tags and selected_tags:
        filtered_docs = [doc for doc in filtered_docs if any(tag in selected_tags for tag in doc.get("tags", []))]
    
    # Display documents
    for doc in filtered_docs:
        with st.expander(f"{doc['title']} ({doc['type']})"):
            st.write(f"**Case ID:** {doc['case_id']}")
            st.write(f"**Uploaded:** {doc['uploaded_at']}")
            
            # Display tags with ability to remove them
            st.markdown("**Tags:**")
            if doc.get("tags"):
                st.markdown(format_tags_html(doc["tags"], doc_id=doc["id"], editable=True), unsafe_allow_html=True)
            else:
                st.markdown("*No tags added yet*")
            
            # Simple tag management UI
            st.markdown("##### Add or Remove Tags")
            
            # Add new tags
            new_tag_input = st.text_input(
                "Add Tags (comma-separated)", 
                key=f"add_tags_{doc['id']}",
                placeholder="Enter tags to add..."
            )
            
            if new_tag_input:
                new_tags = parse_tags(new_tag_input)
                if new_tags and st.button("Add Tags", key=f"add_tags_btn_{doc['id']}"):
                    if add_tags_to_document(doc["id"], new_tags, st.session_state.documents, st.session_state.tags):
                        st.success(f"Added tags to {doc['title']}")
                        # Reinitialize vectorstore
                        with st.spinner("Updating knowledge base..."):
                            st.session_state.vectorstore = initialize_vectorstore(st.session_state.documents)
                        st.rerun()
            
            # Remove tags dropdown
            if doc.get("tags"):
                tag_to_remove = st.selectbox(
                    "Select tag to remove",
                    ["Select a tag..."] + doc["tags"],
                    key=f"remove_tag_select_{doc['id']}"
                )
                
                if tag_to_remove != "Select a tag...":
                    if st.button(f"Remove '{tag_to_remove}'", key=f"remove_tag_btn_{doc['id']}"):
                        if remove_tag_from_document(doc["id"], tag_to_remove, st.session_state.documents, st.session_state.tags):
                            st.success(f"Removed tag '{tag_to_remove}' from {doc['title']}")
                            # Reinitialize vectorstore
                            with st.spinner("Updating knowledge base..."):
                                st.session_state.vectorstore = initialize_vectorstore(st.session_state.documents)
                            st.rerun()
            
            # Option to remove document
            st.markdown("---")
            if st.button(f"Remove Document", key=f"remove_{doc['id']}"):
                st.session_state.documents = [d for d in st.session_state.documents if d["id"] != doc["id"]]
                st.success(f"Removed {doc['title']}")
                
                # Reinitialize vectorstore
                with st.spinner("Updating knowledge base..."):
                    st.session_state.vectorstore = initialize_vectorstore(st.session_state.documents)
                    st.success("Knowledge base updated!")
                st.rerun()
    
    # Button to clear all documents
    if st.button("Clear All Documents"):
        st.session_state.documents = []
        st.session_state.vectorstore = None
        st.session_state.tags = set()
        st.success("All documents cleared from the knowledge base")
        st.rerun()

def build_settings_panel():
    """Build the settings panel in the sidebar"""
    st.markdown("### API Settings")
    
    # OpenAI API Key input
    openai_api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key here. It's required for embeddings and the chat model."
    )
    
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    
    # Model settings
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
    
    # Save settings in session state
    if "settings" not in st.session_state:
        st.session_state.settings = {}
    
    st.session_state.settings["model_name"] = model_name
    st.session_state.settings["temperature"] = temperature
    
    # Global tag management
    st.markdown("### Tag Management")
    
    if st.session_state.tags:
        all_tags = list(st.session_state.tags)
        all_tags.sort()
        
        st.markdown("**All Tags in System:**")
        for tag in all_tags:
            st.markdown(f"- {tag}")
        
        # Global tag rename functionality
        st.markdown("**Rename Tags Globally:**")
        tag_to_rename = st.selectbox(
            "Select tag to rename",
            ["Select a tag..."] + all_tags
        )
        
        if tag_to_rename != "Select a tag...":
            new_tag_name = st.text_input("New tag name", key="global_rename_tag")
            
            if new_tag_name and st.button("Rename Tag"):
                rename_tag_globally(tag_to_rename, new_tag_name, st.session_state.documents, st.session_state.tags)
                st.success(f"Renamed tag '{tag_to_rename}' to '{new_tag_name}'")
                # Reinitialize vectorstore
                with st.spinner("Updating knowledge base..."):
                    st.session_state.vectorstore = initialize_vectorstore(st.session_state.documents)
                st.rerun()
    else:
        st.info("No tags in the system yet. Add tags to documents to manage them here.")
    
    # Debug mode toggle
    st.markdown("### Debug Settings")
    debug_mode = st.checkbox("Enable Debug Mode", 
                          value=st.session_state.get("debug_mode", False),
                          help="Shows additional diagnostic information when errors occur")
    st.session_state.debug_mode = debug_mode
    
    if debug_mode:
        build_debug_panel()

def rename_tag_globally(old_tag, new_tag, documents, global_tags):
    """
    Rename a tag across all documents.
    
    Args:
        old_tag: The tag to rename
        new_tag: The new tag name
        documents: List of all documents
        global_tags: Set of all unique tags
    """
    if old_tag == new_tag:
        return
    
    # Update the tag in all documents
    for i, doc in enumerate(documents):
        if "tags" in doc and old_tag in doc["tags"]:
            tags = doc["tags"].copy()
            tags.remove(old_tag)
            tags.append(new_tag)
            documents[i]["tags"] = tags
    
    # Update global tags
    if old_tag in global_tags:
        global_tags.remove(old_tag)
        global_tags.add(new_tag)

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