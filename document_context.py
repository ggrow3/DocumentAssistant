import streamlit as st
from utils import format_tags_html

def build_document_context_panel():
    """Build the document context panel showing documents used in the current conversation"""
    st.markdown("### Document Context")
    st.markdown("Recent documents used for answering will appear here.")
    
    # Add a toggle for showing/hiding sources
    if 'show_sources' not in st.session_state:
        st.session_state.show_sources = True
    
    # Toggle button for showing/hiding sources
    show_sources = st.toggle("Show Sources", value=st.session_state.show_sources)
    st.session_state.show_sources = show_sources
    
    # Get unique citation sources from the last assistant message
    last_assistant_msg = next(
        (msg for msg in reversed(st.session_state.chat_history) if msg["role"] == "assistant"),
        None
    )
    
    if last_assistant_msg and last_assistant_msg.get("citations") and show_sources:
        # Show number of citations in debug mode
        if st.session_state.get("debug_mode", False):
            st.write(f"Number of citations: {len(last_assistant_msg['citations'])}")
        
        # Process citations
        unique_sources = get_unique_sources_from_citations(last_assistant_msg['citations'])
        
        if unique_sources:
            display_source_documents(unique_sources)
        else:
            st.info("No valid documents found in citations.")
    elif last_assistant_msg and last_assistant_msg.get("citations") and not show_sources:
        st.info(f"{len(get_unique_sources_from_citations(last_assistant_msg['citations']))} sources are hidden. Toggle 'Show Sources' to view them.")
    else:
        st.info("No documents referenced in the current conversation.")
    
    # Add option to clear chat history
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

def get_unique_sources_from_citations(citations):
    """
    Extract unique document sources from citations, preventing duplicates
    
    Args:
        citations: List of citation objects
        
    Returns:
        Dictionary of unique document sources
    """
    unique_sources = {}
    
    for citation in citations:
        source = citation["source"]
        doc_id = citation["doc_id"]
        
        # Skip unknown sources and errors
        if source == "Unknown" or source == "Error":
            continue
            
        # Use source + doc_id as the unique key to prevent duplicates
        unique_key = f"{source}_{doc_id}"
        
        if unique_key not in unique_sources:
            unique_sources[unique_key] = {
                "source": source,
                "doc_id": doc_id,
                "doc_type": citation["doc_type"],
                "case_id": citation["case_id"],
                "tags": citation.get("tags", []),
                "text": citation.get("text", "")
            }
    
    return unique_sources

def display_source_documents(unique_sources):
    """Display the source documents with expandable details"""
    for unique_key, info in unique_sources.items():
        source = info["source"]
        
        with st.expander(f"{source} ({info['doc_type']})"):
            st.write(f"**Case ID:** {info['case_id']}")
            
            # Display tags with better formatting
            if info.get("tags"):
                st.markdown("**Tags:**")
                # Use read-only version of tags (not editable here)
                st.markdown(format_tags_html(info["tags"]), unsafe_allow_html=True)
            
            # Get the full document text
            doc = next((d for d in st.session_state.documents if d["id"] == info["doc_id"]), None)
            if doc:
                st.write(f"**Uploaded:** {doc['uploaded_at']}")
                
                # Option to view full document text
                if st.button(f"View full document", key=f"view_{info['doc_id']}"):
                    # Display in a dialog or expander
                    st.info("Document Preview")
                    st.markdown(doc["text"][:1000] + "..." if len(doc["text"]) > 1000 else doc["text"])
                    
                # Link to document in the sidebar
                if st.button(f"Manage tags", key=f"manage_tags_{info['doc_id']}"):
                    # Set a session state flag to open the document in the sidebar
                    st.session_state["open_doc_in_sidebar"] = info["doc_id"]
                    # Add a message to guide the user
                    st.info("Please check the Document Management tab in the sidebar to manage this document's tags.")
            else:
                # If we can't find the document, show the cited text at least
                st.warning("Full document not found in session. Showing citation only.")
                st.markdown(f"**Citation text:** {info['text'][:500]}...")