import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import filter_complex_metadata

def initialize_vectorstore(documents, use_in_memory=True):
    """
    Initialize vector store with documents.
    
    Args:
        documents: List of document objects
        use_in_memory: Whether to use in-memory storage (True) or persistent storage (False)
    
    Returns:
        Vector store object
    """
    # FORCING IN-MEMORY STORAGE: Always use in-memory storage to avoid SQLite issues
    use_in_memory = True
    
    # Handle empty documents case
    if not documents:
        st.warning("No documents provided for vectorstore initialization.")
        return None
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100
    )
    
    langchain_docs = []
    
    for doc in documents:
        try:
            # Skip invalid documents
            if not isinstance(doc, dict) or "pages" not in doc:
                st.warning(f"Skipping invalid document: {type(doc)}")
                continue
                
            # Get the tags as a comma-separated string
            tags_list = doc.get("tags", [])
            if not isinstance(tags_list, list):
                tags_list = []
            tags_str = ",".join(tags_list)
            
            # Process each page
            for i, page in enumerate(doc["pages"]):
                try:
                    # Extract page content based on type
                    if hasattr(page, 'page_content'):
                        # It's already a Document object
                        page_content = page.page_content
                    elif isinstance(page, str):
                        # It's a string
                        page_content = page
                    elif isinstance(page, dict) and "page_content" in page:
                        # It's a dict with page_content
                        page_content = page["page_content"]
                    else:
                        # Try to convert to string
                        page_content = str(page)
                    
                    # Split the content into chunks
                    chunks = text_splitter.split_text(page_content)
                    
                    # Create document objects for each chunk
                    for j, chunk in enumerate(chunks):
                        # Create metadata dictionary with only simple types
                        metadata = {
                            "source": str(doc.get("title", "")),
                            "doc_id": str(doc.get("id", "")),
                            "doc_type": str(doc.get("type", "")),
                            "case_id": str(doc.get("case_id", "")),
                            "tags_str": tags_str,  # Store as string
                            "page": i,
                            "chunk": j
                        }
                        
                        # Create a LangChain Document
                        langchain_docs.append(Document(
                            page_content=chunk,
                            metadata=metadata
                        ))
                        
                except Exception as e:
                    st.warning(f"Error processing page {i} of document {doc.get('title', 'Unknown')}: {str(e)}")
                    continue
        except Exception as e:
            st.warning(f"Error processing document: {str(e)}")
            continue
    
    if not langchain_docs:
        st.warning("No documents were processed successfully for the vector store.")
        return None
    
    try:
        # Create vectorstore
        st.info(f"Creating vector store with {len(langchain_docs)} document chunks (using in-memory storage)...")
        embeddings = OpenAIEmbeddings()
        
        # Log the first few documents for debugging
        if st.session_state.get("debug_mode", False):
            st.write("### Sample Documents For Vector Store:")
            for i, doc in enumerate(langchain_docs[:3]):  # Show first 3
                st.write(f"Document {i}:")
                st.write(f"  Content: {doc.page_content[:100]}...")
                st.write(f"  Metadata: {doc.metadata}")
        
        # ALWAYS create vectorstore with in-memory storage
        # DO NOT use persist_directory parameter
        vectorstore = Chroma.from_documents(
            documents=langchain_docs,
            embedding=embeddings
            # No persist_directory parameter means in-memory storage
        )
        
        # Configure retriever
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}  # Return top 5 most relevant chunks
        )
        
        # Test the retriever to make sure it's working
        if st.session_state.get("debug_mode", False) and langchain_docs:
            st.write("### Testing Retriever:")
            test_query = "sample test query"
            st.write(f"Test Query: {test_query}")
            try:
                test_docs = retriever.invoke(test_query)
                st.write(f"Retrieved {len(test_docs)} documents")
                for i, doc in enumerate(test_docs[:2]):  # Show first 2
                    st.write(f"Retrieved Doc {i}:")
                    st.write(f"  Content: {doc.page_content[:100]}...")
                    st.write(f"  Metadata: {doc.metadata}")
            except Exception as e:
                st.error(f"Error testing retriever: {str(e)}")
        
        return vectorstore
        
    except Exception as e:
        st.error(f"Error creating vector store: {str(e)}")
        st.info("If you're seeing SQLite errors with in-memory storage, there might be an issue with Chroma installation.")
        
        if st.session_state.get("debug_mode", False):
            # More detailed error info in debug mode
            st.write("Error details:")
            st.write(str(e))
            
            # Print the first few documents to help diagnose
            st.write("First document metadata sample:")
            if langchain_docs:
                st.write(langchain_docs[0].metadata)
                
            # Try to import and check sqlite3 version directly
            try:
                import sqlite3
                st.write(f"SQLite version: {sqlite3.sqlite_version}")
            except:
                st.write("Could not determine SQLite version")
            
        return None