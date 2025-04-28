import streamlit as st
import base64
from datetime import datetime
import io

def build_document_manager():
    """
    Build a comprehensive document management interface
    """
    st.title("Document Management")
    
    # Create tabs for different views
    tabs = ["Document Library", "Document Viewer", "Document History"]
    selected_tab = st.tabs(tabs)
    
    with selected_tab[0]:
        document_library()
    
    with selected_tab[1]:
        document_viewer()
    
    with selected_tab[2]:
        document_history()

def document_library():
    """
    Display a library of all documents with filtering and download options
    """
    st.header("Document Library")
    
    # Check if documents exist
    if not st.session_state.documents:
        st.info("No documents have been uploaded yet. Use the Document Management tab in the sidebar to upload documents.")
        return
    
    # Create filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        document_types = ["All Types"] + list(set(doc["type"] for doc in st.session_state.documents))
        selected_type = st.selectbox("Document Type", document_types)
    
    with col2:
        case_ids = ["All Cases"] + list(set(doc["case_id"] for doc in st.session_state.documents if doc["case_id"]))
        selected_case = st.selectbox("Case ID", case_ids)
    
    with col3:
        # Get all unique tags
        all_tags = set()
        for doc in st.session_state.documents:
            if "tags" in doc and doc["tags"]:
                all_tags.update(doc["tags"])
        
        selected_tag = st.selectbox("Filter by Tag", ["No Tag Filter"] + sorted(list(all_tags)))
    
    # Filter the documents based on selections
    filtered_docs = []
    for doc in st.session_state.documents:
        type_match = selected_type == "All Types" or doc["type"] == selected_type
        case_match = selected_case == "All Cases" or doc["case_id"] == selected_case
        tag_match = selected_tag == "No Tag Filter" or (
            "tags" in doc and selected_tag in doc["tags"]
        )
        
        if type_match and case_match and tag_match:
            filtered_docs.append(doc)
    
    # Display document count
    st.write(f"Found {len(filtered_docs)} document(s)")
    
    # Display documents as cards
    if filtered_docs:
        for doc in filtered_docs:
            with st.expander(f"{doc['title']} ({doc['type']})"):
                # Document info
                st.write(f"**Case ID:** {doc.get('case_id', 'N/A')}")
                st.write(f"**Uploaded:** {doc.get('uploaded_at', 'Unknown')}")
                if "tags" in doc and doc["tags"]:
                    st.write(f"**Tags:** {', '.join(doc['tags'])}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("View Document", key=f"view_{doc['id']}"):
                        st.session_state.selected_doc_for_viewing = doc
                        st.rerun()
                
                with col2:
                    if st.button("Download", key=f"download_{doc['id']}"):
                        download_document(doc)
                
                with col3:
                    if st.button("History", key=f"history_{doc['id']}"):
                        st.session_state.selected_doc_for_history = doc
                        st.rerun()

def document_viewer():
    """
    Document viewer to display document content with passage highlighting
    """
    st.header("Document Viewer")
    
    # Check if a document is selected for viewing
    if "selected_doc_for_viewing" not in st.session_state or not st.session_state.selected_doc_for_viewing:
        # If not, provide a dropdown to select one
        if not st.session_state.documents:
            st.info("No documents have been uploaded yet.")
            return
            
        doc_options = [(doc["id"], doc["title"]) for doc in st.session_state.documents]
        selected_option = st.selectbox("Select a document to view", 
                                      options=doc_options, 
                                      format_func=lambda x: x[1])
        
        if selected_option:
            doc_id = selected_option[0]
            st.session_state.selected_doc_for_viewing = next(
                (doc for doc in st.session_state.documents if doc["id"] == doc_id), None
            )
            st.rerun()
        else:
            st.info("Please select a document to view.")
            return
    
    # Get the selected document
    doc = st.session_state.selected_doc_for_viewing
    
    # Display document info
    st.subheader(f"{doc['title']} ({doc['type']})")
    st.write(f"Case ID: {doc['case_id']}")
    
    # Display tags if available
    if "tags" in doc and doc["tags"]:
        st.write("Tags: " + ", ".join(doc["tags"]))
    
    # Content display options
    view_options = ["Full Document", "Page View", "Search for Passage"]
    selected_view = st.radio("View Options", view_options, horizontal=True)
    
    if selected_view == "Full Document":
        display_full_document(doc)
    
    elif selected_view == "Page View":
        display_document_pages(doc)
    
    elif selected_view == "Search for Passage":
        search_document_passage(doc)
    
    # Button to clear current document
    if st.button("Clear Document Viewer"):
        st.session_state.selected_doc_for_viewing = None
        st.rerun()

def document_history():
    """
    Display document history and versions
    """
    st.header("Document History")
    
    # Check if a document is selected for history viewing
    if "selected_doc_for_history" not in st.session_state or not st.session_state.selected_doc_for_history:
        # If not, provide a dropdown to select one
        if not st.session_state.documents:
            st.info("No documents have been uploaded yet.")
            return
            
        doc_options = [(doc["id"], doc["title"]) for doc in st.session_state.documents]
        selected_option = st.selectbox("Select a document to view history", 
                                      options=doc_options, 
                                      format_func=lambda x: x[1])
        
        if selected_option:
            doc_id = selected_option[0]
            st.session_state.selected_doc_for_history = next(
                (doc for doc in st.session_state.documents if doc["id"] == doc_id), None
            )
            st.rerun()
        else:
            st.info("Please select a document to view history.")
            return
    
    # Get the selected document
    doc = st.session_state.selected_doc_for_history
    
    # Display document info
    st.subheader(f"History for: {doc['title']}")
    
    # In a real application, this would query a database for document history
    # For this example, we'll simulate some history events
    
    # Simulate history events
    if "document_history" not in st.session_state:
        st.session_state.document_history = {}
    
    doc_id = doc["id"]
    if doc_id not in st.session_state.document_history:
        # Create some sample history for this document
        upload_time = doc.get("uploaded_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Create sample history events
        st.session_state.document_history[doc_id] = [
            {
                "event_type": "Upload",
                "timestamp": upload_time,
                "user": doc.get("uploaded_by_name", "Unknown User"),
                "details": f"Document uploaded to system"
            }
        ]
        
        # Add tag events if document has tags
        if "tags" in doc and doc["tags"]:
            for i, tag in enumerate(doc["tags"]):
                # Create events spaced 5 minutes apart
                st.session_state.document_history[doc_id].append({
                    "event_type": "Tag Added",
                    "timestamp": upload_time,
                    "user": doc.get("uploaded_by_name", "Unknown User"),
                    "details": f"Added tag: {tag}"
                })
        
        # Add a view event
        st.session_state.document_history[doc_id].append({
            "event_type": "View",
            "timestamp": upload_time,
            "user": "Current User",
            "details": f"Document viewed"
        })
    
    # Display history events
    history = st.session_state.document_history[doc_id]
    
    # Display as a simple table
    if history:
        # Sort by timestamp
        history = sorted(history, key=lambda x: x["timestamp"], reverse=True)
        
        # Display as a simple table
        for event in history:
            st.write(f"**{event['timestamp']}** - {event['event_type']} by {event['user']}")
            st.write(f"_{event['details']}_")
            st.write("---")
    else:
        st.info("No history available for this document.")
    
    # Button to clear current document
    if st.button("Clear History View"):
        st.session_state.selected_doc_for_history = None
        st.rerun()

# Helper functions

def download_document(doc):
    """Provide a download link for a document"""
    # For this demo, we'll create a text version of the document
    # In a real application, you would provide the original file
    
    content = ""
    
    # Extract text content from pages
    for i, page in enumerate(doc.get("pages", [])):
        content += f"--- Page {i+1} ---\n\n"
        
        if hasattr(page, 'page_content'):
            content += page.page_content
        elif isinstance(page, str):
            content += page
        elif isinstance(page, dict) and "page_content" in page:
            content += page["page_content"]
        else:
            content += str(page)
        
        content += "\n\n"
    
    # Create a download link
    b64 = base64.b64encode(content.encode()).decode()
    filename = f"{doc['title'].replace(' ', '_')}.txt"
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Download {filename}</a>'
    st.markdown(href, unsafe_allow_html=True)

def display_full_document(doc):
    """Display the full document content"""
    # Extract text content from pages
    content = ""
    
    for i, page in enumerate(doc.get("pages", [])):
        content += f"<h3>Page {i+1}</h3>\n\n"
        
        if hasattr(page, 'page_content'):
            content += page.page_content
        elif isinstance(page, str):
            content += page
        elif isinstance(page, dict) and "page_content" in page:
            content += page["page_content"]
        else:
            content += str(page)
        
        content += "\n\n"
    
    # Display in scrollable container
    st.markdown(
        f'<div style="height:500px;overflow-y:scroll;padding:10px;border:1px solid #ddd;border-radius:5px;">{content}</div>',
        unsafe_allow_html=True
    )

def display_document_pages(doc):
    """Display document by pages with navigation"""
    # Page selector
    pages = doc.get("pages", [])
    if not pages:
        st.warning("This document has no pages.")
        return
    
    page_number = st.slider("Page", 1, len(pages), 1)
    
    # Get the selected page (0-indexed)
    page = pages[page_number - 1]
    
    # Extract text content
    if hasattr(page, 'page_content'):
        content = page.page_content
    elif isinstance(page, str):
        content = page
    elif isinstance(page, dict) and "page_content" in page:
        content = page["page_content"]
    else:
        content = str(page)
    
    # Display the page content
    st.subheader(f"Page {page_number} of {len(pages)}")
    st.markdown(
        f'<div style="height:400px;overflow-y:scroll;padding:10px;border:1px solid #ddd;border-radius:5px;">{content}</div>',
        unsafe_allow_html=True
    )
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if page_number > 1:
            if st.button("Previous Page"):
                st.session_state.page_number = page_number - 1
                st.rerun()
    
    with col2:
        if page_number < len(pages):
            if st.button("Next Page"):
                st.session_state.page_number = page_number + 1
                st.rerun()

def search_document_passage(doc):
    """Search for a specific passage in the document"""
    # Search input
    search_query = st.text_input("Search for passage", "")
    
    if search_query:
        # Search in all pages
        results = []
        
        for i, page in enumerate(doc.get("pages", [])):
            # Extract text content
            if hasattr(page, 'page_content'):
                content = page.page_content
            elif isinstance(page, str):
                content = page
            elif isinstance(page, dict) and "page_content" in page:
                content = page["page_content"]
            else:
                content = str(page)
            
            # Check if query is in content (case-insensitive)
            if search_query.lower() in content.lower():
                # Find the position of the query
                pos = content.lower().find(search_query.lower())
                
                # Extract a snippet around the query (100 chars before and after)
                start = max(0, pos - 100)
                end = min(len(content), pos + len(search_query) + 100)
                
                # Extract the snippet
                snippet = content[start:end]
                
                # Highlight the query in the snippet
                highlighted = snippet.replace(
                    search_query, 
                    f"<span style='background-color:yellow'>{search_query}</span>"
                )
                
                results.append({
                    "page": i + 1,
                    "snippet": highlighted,
                    "full_content": content
                })
        
        # Display results
        if results:
            st.success(f"Found {len(results)} occurrences of '{search_query}'")
            
            for i, result in enumerate(results):
                with st.expander(f"Result {i+1} (Page {result['page']})"):
                    st.markdown(f"<div>{result['snippet']}</div>", unsafe_allow_html=True)
                    
                    if st.button(f"View full page {result['page']}", key=f"view_page_{i}"):
                        # Set up the page view
                        st.session_state.page_number = result['page']
                        st.session_state.view_mode = "Page View"
                        st.rerun()
        else:
            st.warning(f"No occurrences of '{search_query}' found in the document.")
    else:
        st.info("Enter a search term to find passages in the document.")