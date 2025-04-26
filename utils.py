def format_tags_html(tags, doc_id=None, editable=False):
    """
    Format tags as HTML for display in Streamlit.
    
    Args:
        tags: List of tag strings
        doc_id: Document ID for tag editing/removal functionality
        editable: Whether the tags should be editable/removable
        
    Returns:
        HTML string for displaying tags
    """
    if not tags:
        return ""
    
    html = '<div class="tag-container">'
    
    for tag in tags:
        if editable and doc_id:
            # Create editable/removable tag with remove button
            html += f'''
            <span class="tag-item">
                {tag}
                <button class="tag-remove-btn" data-doc-id="{doc_id}" data-tag="{tag}" 
                    title="Remove this tag">×</button>
            </span>
            '''
        else:
            # Create regular non-editable tag
            html += f'<span class="tag-item">{tag}</span>'
    
    html += '</div>'
    
    return html

def add_tags_to_document(doc_id, new_tags, documents, global_tags):
    """
    Add tags to an existing document.
    
    Args:
        doc_id: ID of the document to tag
        new_tags: List of new tags to add
        documents: List of all documents
        global_tags: Set of all unique tags
    
    Returns:
        Boolean indicating success
    """
    for i, doc in enumerate(documents):
        if doc["id"] == doc_id:
            current_tags = set(doc.get("tags", []))
            current_tags.update(new_tags)
            documents[i]["tags"] = list(current_tags)
            
            # Add to global tags set
            for tag in new_tags:
                global_tags.add(tag)
            
            return True
    
    return False

def remove_tag_from_document(doc_id, tag_to_remove, documents, global_tags):
    """
    Remove a tag from a document.
    
    Args:
        doc_id: ID of the document
        tag_to_remove: Tag to remove
        documents: List of all documents
        global_tags: Set of all unique tags
    
    Returns:
        Boolean indicating success
    """
    for i, doc in enumerate(documents):
        if doc["id"] == doc_id:
            current_tags = list(doc.get("tags", []))
            
            if tag_to_remove in current_tags:
                # Remove the tag from the document
                current_tags.remove(tag_to_remove)
                documents[i]["tags"] = current_tags
                
                # Update global tags if needed
                tag_still_used = any(tag_to_remove in d.get("tags", []) for d in documents)
                if not tag_still_used:
                    global_tags.discard(tag_to_remove)
                
                return True
    
    return False

def debug_document_format(documents):
    """
    Debug helper to print document format details
    
    Args:
        documents: List of document objects to examine
    """
    import streamlit as st
    
    st.write(f"Number of documents: {len(documents)}")
    
    for i, doc in enumerate(documents):
        st.write(f"Document {i}:")
        st.write(f"  Type: {type(doc)}")
        
        if isinstance(doc, dict):
            st.write(f"  Keys: {list(doc.keys())}")
            if "pages" in doc:
                st.write(f"  Number of pages: {len(doc['pages'])}")
                for j, page in enumerate(doc["pages"][:2]):  # Just first 2 pages
                    st.write(f"    Page {j} type: {type(page)}")
                    if hasattr(page, "page_content"):
                        st.write(f"    Has page_content attribute")
                    if hasattr(page, "metadata"):
                        st.write(f"    Has metadata attribute")
            
            if "tags" in doc:
                st.write(f"  Tags type: {type(doc['tags'])}")
                st.write(f"  Tags: {doc['tags']}")
        
        # Add a separator
        st.write("---")
        
        # Limit to 5 documents to avoid overload
        if i >= 4:
            st.write("(More documents not shown)")
            break

def test_retriever_functionality(vectorstore, query="test query"):
    """
    Function to test if the retriever is working properly
    
    Args:
        vectorstore: The Chroma vector store to test
        query: A test query string
        
    Returns:
        List of retrieved documents or None if error
    """
    import streamlit as st
    from langchain_openai import OpenAIEmbeddings
    
    try:
        # First check if the vectorstore is initialized
        if vectorstore is None:
            st.error("Vector store is not initialized")
            return None
            
        # Get the retriever from the vectorstore
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        # Try a basic retrieval
        docs = retriever.get_relevant_documents(query)
        
        # Print results
        st.success(f"Successfully retrieved {len(docs)} documents")
        
        # Display document info
        for i, doc in enumerate(docs):
            st.write(f"Document {i+1}:")
            st.write(f"  Content preview: {doc.page_content[:100]}...")
            st.write(f"  Metadata: {doc.metadata}")
            
        return docs
        
    except Exception as e:
        st.error(f"Error testing retriever: {str(e)}")
        
        # Try to diagnose the issue
        try:
            # Check if embeddings can be created
            st.write("Testing embeddings functionality...")
            embeddings = OpenAIEmbeddings()
            test_embedding = embeddings.embed_query("test")
            st.write(f"Embedding generation works. Vector length: {len(test_embedding)}")
            
            # Check if the collection exists and has documents
            st.write("Checking vector store collection...")
            
            # Try to access some internal components
            if hasattr(vectorstore, "_collection"):
                st.write(f"Collection exists with name: {vectorstore._collection.name}")
                count = vectorstore._collection.count()
                st.write(f"Collection contains {count} documents")
            elif hasattr(vectorstore, "collection"):
                st.write(f"Collection exists with name: {vectorstore.collection.name}")
                count = vectorstore.collection.count()
                st.write(f"Collection contains {count} documents")
            else:
                st.warning("Cannot access vector store collection information")
                
        except Exception as inner_e:
            st.error(f"Error during diagnostics: {str(inner_e)}")
            
        return None