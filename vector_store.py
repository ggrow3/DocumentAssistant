import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import os
import uuid

def initialize_vectorstore(documents, use_in_memory=True, vectorstore_type="chroma", pinecone_index=None):
    """
    Initialize vector store with documents.
    
    Args:
        documents: List of document objects
        use_in_memory: Whether to use in-memory storage (True) or persistent storage (False) for Chroma
        vectorstore_type: Type of vectorstore to use ("chroma" or "pinecone")
        pinecone_index: Name of Pinecone index to use (if vectorstore_type is "pinecone")
    
    Returns:
        Vector store object
    """
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
                            "chunk": j,
                            "text": chunk  # Add text as metadata for Pinecone
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
        # Create embeddings
        embeddings = OpenAIEmbeddings()
        
        # Log the first few documents for debugging
        if st.session_state.get("debug_mode", False):
            st.write("### Sample Documents For Vector Store:")
            for i, doc in enumerate(langchain_docs[:3]):  # Show first 3
                st.write(f"Document {i}:")
                st.write(f"  Content: {doc.page_content[:100]}...")
                st.write(f"  Metadata: {doc.metadata}")
        
        # Create vectorstore based on selected type
        if vectorstore_type == "pinecone":
            # Create a custom Pinecone vectorstore wrapper
            return PineconeVectorStore(
                langchain_docs=langchain_docs,
                embeddings=embeddings,
                pinecone_index=pinecone_index
            )
        else:
            # Default to Chroma
            st.info(f"Creating Chroma vector store with {len(langchain_docs)} document chunks (using in-memory storage)...")
            
            # Always create vectorstore with in-memory storage for now
            vectorstore = Chroma.from_documents(
                documents=langchain_docs,
                embedding=embeddings
                # No persist_directory parameter means in-memory storage
            )
            return vectorstore
        
    except Exception as e:
        st.error(f"Error creating vector store: {str(e)}")
        
        if st.session_state.get("debug_mode", False):
            # More detailed error info in debug mode
            st.write("Error details:")
            st.write(str(e))
            import traceback
            st.write(f"Traceback: {traceback.format_exc()}")
            
            # Print the first few documents to help diagnose
            st.write("First document metadata sample:")
            if langchain_docs:
                st.write(langchain_docs[0].metadata)
            
        return None


class PineconeVectorStore:
    """
    Custom wrapper for Pinecone that implements a compatible interface with LangChain
    but doesn't rely on LangChain's Pinecone integration.
    """
    
    def __init__(self, langchain_docs, embeddings, pinecone_index):
        """Initialize the Pinecone vector store"""
        # Check if Pinecone API key is available
        pinecone_api_key = os.environ.get("PINECONE_API_KEY")
        if not pinecone_api_key:
            st.error("Pinecone API key not found. Please enter it in settings.")
            raise ValueError("Pinecone API key not found")
            
        # Check if Pinecone index name is provided
        if not pinecone_index:
            st.error("Pinecone index name not provided. Please enter it in settings.")
            raise ValueError("Pinecone index name not provided")
            
        st.info(f"Creating Pinecone vector store with {len(langchain_docs)} document chunks...")
        
        # Import and initialize Pinecone with new API
        try:
            from pinecone import Pinecone
            
            # Store for use in queries
            self.embeddings = embeddings
            self.index_name = pinecone_index
            
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=pinecone_api_key)
            
            # Check if index exists
            indexes = self.pc.list_indexes().names()
            if pinecone_index not in indexes:
                st.error(f"Pinecone index '{pinecone_index}' not found. Please create it first.")
                raise ValueError(f"Pinecone index '{pinecone_index}' not found")
            
            # Get the index
            self.index = self.pc.Index(pinecone_index)
            
            # Upload documents if provided
            if langchain_docs:
                self._upload_documents(langchain_docs)
                
            st.success(f"Successfully connected to Pinecone index '{pinecone_index}'")
            
        except ImportError:
            st.error("Pinecone Python client not installed. Please install with: pip install pinecone-client>=3.0.0")
            raise
        except Exception as e:
            st.error(f"Error initializing Pinecone vector store: {str(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _upload_documents(self, langchain_docs):
        """Upload documents to Pinecone"""
        try:
            # Process in batches to avoid overloading
            batch_size = 100
            total_docs = len(langchain_docs)
            
            for i in range(0, total_docs, batch_size):
                # Get current batch
                batch = langchain_docs[i:min(i+batch_size, total_docs)]
                
                # Create vectors for batch
                vectors = []
                for doc in batch:
                    # Generate embedding for the document text
                    embedding = self.embeddings.embed_query(doc.page_content)
                    
                    # Create a vector with a unique ID
                    vector_id = str(uuid.uuid4())
                    
                    # Create the vector record
                    vector = {
                        "id": vector_id,
                        "values": embedding,
                        "metadata": doc.metadata
                    }
                    
                    vectors.append(vector)
                
                # Upsert vectors to Pinecone
                self.index.upsert(vectors=vectors)
                
                st.write(f"Uploaded {min(i+batch_size, total_docs)}/{total_docs} documents to Pinecone")
            
            st.success(f"Successfully uploaded {total_docs} documents to Pinecone")
        
        except Exception as e:
            st.error(f"Error uploading documents to Pinecone: {str(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def as_retriever(self, search_type="similarity", search_kwargs=None):
        """Return a retriever that can be used with LangChain"""
        return PineconeRetriever(
            pinecone_store=self,
            search_kwargs=search_kwargs or {"k": 5}
        )
    
    def similarity_search(self, query, k=5):
        """Search for similar documents to the query"""
        # Generate embedding for the query
        query_embedding = self.embeddings.embed_query(query)
        
        # Search Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=k,
            include_metadata=True
        )
        
        # Convert to LangChain documents
        documents = []
        for match in results.matches:
            metadata = match.metadata
            text = metadata.get("text", "")
            # Remove text from metadata to avoid duplication
            if "text" in metadata:
                metadata_copy = metadata.copy()
                del metadata_copy["text"]
            else:
                metadata_copy = metadata
                
            documents.append(Document(
                page_content=text,
                metadata=metadata_copy
            ))
        
        return documents


class PineconeRetriever:
    """
    Custom retriever that wraps PineconeVectorStore and provides a compatible
    interface with LangChain.
    """
    
    def __init__(self, pinecone_store, search_kwargs=None):
        """Initialize the retriever"""
        self.pinecone_store = pinecone_store
        self.search_kwargs = search_kwargs or {"k": 5}
    
    def get_relevant_documents(self, query):
        """Get relevant documents for a query"""
        return self.pinecone_store.similarity_search(
            query,
            k=self.search_kwargs.get("k", 5)
        )
    
    def invoke(self, query):
        """Invoke the retriever (compatible with LangChain)"""
        return self.get_relevant_documents(query)