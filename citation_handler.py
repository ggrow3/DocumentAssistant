from langchain_core.callbacks import BaseCallbackHandler

class CitationTrackingHandler(BaseCallbackHandler):
    """
    Callback handler for tracking citations in LangChain.
    
    This handler captures documents returned by the retriever and converts
    them to a format suitable for displaying citations in the UI.
    """
    def __init__(self):
        """Initialize the citation handler"""
        self.citations = []
        
    def on_chain_start(self, serialized, inputs, **kwargs):
        """Called when the chain starts running."""
        import streamlit as st
        if st.session_state.get("debug_mode", False):
            st.write("Chain started")
        
    def on_chain_end(self, outputs, **kwargs):
        """Called when the chain finishes running."""
        import streamlit as st
        
        # Check if we have source documents in the output
        if 'source_documents' in outputs and outputs['source_documents']:
            if st.session_state.get("debug_mode", False):
                st.write(f"Chain finished with {len(outputs['source_documents'])} source documents")
            
            # Process the source documents
            self.on_retriever_end(outputs['source_documents'])
        else:
            if st.session_state.get("debug_mode", False):
                st.write("Chain finished but no source documents were found in outputs")
    
    def on_retriever_start(self, query, **kwargs):
        """Called when the retriever starts retrieving documents."""
        import streamlit as st
        if st.session_state.get("debug_mode", False):
            st.write(f"Retriever started with query: {query}")
        # Clear existing citations when starting a new retrieval
        self.citations = []
        
    def on_retriever_end(self, documents, **kwargs):
        """
        Callback that runs after the retriever finishes retrieving documents.
        
        Args:
            documents: The documents returned by the retriever
            **kwargs: Additional keyword arguments
        """
        import streamlit as st
        
        self.citations = []
        
        if not documents:
            if st.session_state.get("debug_mode", False):
                st.warning("No documents were retrieved")
            return
        
        if st.session_state.get("debug_mode", False):
            st.write(f"Retrieved {len(documents)} documents")
        
        for doc in documents:
            try:
                # Make sure we're dealing with a Document object
                if hasattr(doc, 'page_content') and hasattr(doc, 'metadata'):
                    # Get content and metadata
                    content = doc.page_content
                    metadata = doc.metadata
                    
                    # Debug the metadata
                    if st.session_state.get("debug_mode", False):
                        st.write(f"Document metadata: {metadata}")
                    
                    # Convert tags_str back to a list if it exists
                    tags = []
                    tags_str = metadata.get("tags_str", "")
                    if tags_str and isinstance(tags_str, str):
                        tags = tags_str.split(",")
                    
                    self.citations.append({
                        "text": content,
                        "source": metadata.get("source", "Unknown"),
                        "doc_id": metadata.get("doc_id", "Unknown"),
                        "doc_type": metadata.get("doc_type", "Unknown"),
                        "case_id": metadata.get("case_id", "Unknown"),
                        "tags": tags,
                        "page": metadata.get("page", 0),
                        "chunk": metadata.get("chunk", 0)
                    })
                    
                    if st.session_state.get("debug_mode", False):
                        st.write(f"Successfully processed citation from {metadata.get('source', 'Unknown')}")
                elif isinstance(doc, dict):
                    # It's a dictionary format
                    metadata = doc.get("metadata", {})
                    
                    # Convert tags_str back to a list if it exists
                    tags = []
                    tags_str = metadata.get("tags_str", "")
                    if tags_str and isinstance(tags_str, str):
                        tags = tags_str.split(",")
                    
                    self.citations.append({
                        "text": doc.get("page_content", ""),
                        "source": metadata.get("source", "Unknown"),
                        "doc_id": metadata.get("doc_id", "Unknown"),
                        "doc_type": metadata.get("doc_type", "Unknown"),
                        "case_id": metadata.get("case_id", "Unknown"),
                        "tags": tags,
                        "page": metadata.get("page", 0),
                        "chunk": metadata.get("chunk", 0)
                    })
                elif isinstance(doc, str):
                    # It's just a string
                    self.citations.append({
                        "text": doc,
                        "source": "Unknown",
                        "doc_id": "Unknown",
                        "doc_type": "Unknown",
                        "case_id": "Unknown",
                        "tags": [],
                        "page": 0,
                        "chunk": 0
                    })
                else:
                    # Unknown format - try to get some info
                    self.citations.append({
                        "text": str(doc),
                        "source": "Unknown",
                        "doc_id": "Unknown",
                        "doc_type": "Unknown",
                        "case_id": "Unknown",
                        "tags": [],
                        "page": 0,
                        "chunk": 0
                    })
            except Exception as e:
                # If anything goes wrong, add an error citation
                if st.session_state.get("debug_mode", False):
                    st.error(f"Error processing citation: {str(e)}")
                self.citations.append({
                    "text": f"[Error processing document: {str(e)}]",
                    "source": "Error",
                    "doc_id": "Error",
                    "doc_type": "Error",
                    "case_id": "Error",
                    "tags": [],
                    "page": 0,
                    "chunk": 0
                })
        
        if st.session_state.get("debug_mode", False):
            st.write(f"Total citations processed: {len(self.citations)}")