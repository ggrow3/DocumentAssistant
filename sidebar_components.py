import streamlit as st
from utils import format_tags_html, add_tags_to_document, remove_tag_from_document
from document_processing import parse_tags
from vector_store import initialize_vectorstore

def document_uploader():
    """
    UI component for uploading a document and adding metadata
    
    Returns:
        tuple: (doc_type, case_id, doc_title, tags, uploaded_file)
    """
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
    
    return doc_type, case_id, doc_title, tags, uploaded_file

def ocr_settings():
    """UI component for OCR settings"""
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

def document_list():
    """UI component for displaying and filtering documents"""
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
    tag_filter_controls()
    
    # Apply filters
    filtered_docs = filter_documents(filter_case, filter_type)
    
    # Display documents
    for doc in filtered_docs:
        display_document_item(doc)
    
    # Button to clear all documents
    if st.button("Clear All Documents"):
        st.session_state.documents = []
        st.session_state.vectorstore = None
        st.session_state.tags = set()
        st.success("All documents cleared from the knowledge base")
        st.rerun()

def tag_filter_controls():
    """UI controls for filtering by tags"""
    if st.session_state.tags:
        tag_list = list(st.session_state.tags)
        tag_list.sort()
        selected_tags = st.multiselect(
            "Filter by Tags",
            tag_list,
            help="Select one or more tags to filter documents"
        )
        
        # Store selected tags in session state for use in filtering
        st.session_state.selected_filter_tags = selected_tags

def filter_documents(filter_case, filter_type):
    """
    Filter documents based on case ID, type, and tags
    
    Returns:
        list: Filtered document list
    """
    filtered_docs = st.session_state.documents
    
    # Filter by case ID
    if filter_case:
        filtered_docs = [doc for doc in filtered_docs if filter_case.lower() in doc["case_id"].lower()]
    
    # Filter by document type
    if filter_type != "All":
        filtered_docs = [doc for doc in filtered_docs if doc["type"] == filter_type]
    
    # Filter by tags
    selected_tags = st.session_state.get("selected_filter_tags", [])
    if st.session_state.tags and selected_tags:
        filtered_docs = [doc for doc in filtered_docs if any(tag in selected_tags for tag in doc.get("tags", []))]
    
    return filtered_docs

def display_document_item(doc):
    """Display a single document item with its controls"""
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
        
        document_tag_controls(doc)
        
        # Option to remove document
        st.markdown("---")
        if st.button(f"Remove Document", key=f"remove_{doc['id']}"):
            remove_document(doc)

def document_tag_controls(doc):
    """Tag management controls for a document"""
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

def remove_document(doc):
    """Remove a document from the system"""
    st.session_state.documents = [d for d in st.session_state.documents if d["id"] != doc["id"]]
    st.success(f"Removed {doc['title']}")
    
    # Reinitialize vectorstore
    with st.spinner("Updating knowledge base..."):
        st.session_state.vectorstore = initialize_vectorstore(st.session_state.documents)
        st.success("Knowledge base updated!")
    st.rerun()

def tag_manager():
    """Global tag management UI"""
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