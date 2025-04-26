import streamlit as st
import os
import pytesseract
from document_processing import process_document, parse_tags
from vector_store import initialize_vectorstore
from utils import format_tags_html, add_tags_to_document, remove_tag_from_document, debug_document_format, test_retriever_functionality
from sidebar_components import (document_uploader, document_list, ocr_settings, 
                               tag_manager, storage_settings)

def build_sidebar():
    """Build the sidebar interface with document management and settings"""
    with st.sidebar:
        # For authenticated users, show firm name if available
        if st.session_state.get('current_user') and st.session_state.current_user.get('firm_name'):
            st.header(f"{st.session_state.current_user['firm_name']} Legal Assistant")
        else:
            st.header("Legal Document AI Assistant")
        
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
            # Add user information to document metadata
            if st.session_state.get('current_user'):
                document['uploaded_by'] = st.session_state.current_user['username']
                document['uploaded_by_name'] = st.session_state.current_user['full_name']
            
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
                    
                    # Get vectorstore settings
                    vectorstore_type = st.session_state.get("vectorstore_type", "chroma")
                    use_in_memory = True  # Always use in-memory for Chroma
                    pinecone_index = st.session_state.get("pinecone_index", None)
                    
                    # Initialize vector store with appropriate settings
                    st.session_state.vectorstore = initialize_vectorstore(
                        st.session_state.documents, 
                        use_in_memory=use_in_memory,
                        vectorstore_type=vectorstore_type,
                        pinecone_index=pinecone_index
                    )
                    
                    if st.session_state.vectorstore:
                        st.success("Knowledge base updated!")
                    else:
                        st.error("Failed to create vector store. Check settings and try again.")
            except Exception as e:
                st.error(f"Error updating knowledge base: {str(e)}")
                
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
    
    # Vector store settings
    vectorstore_settings()
    
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
    
    # User settings section for admin users
    if st.session_state.get('current_user') and st.session_state.current_user.get('role') == 'admin':
        user_admin_settings()
    
    # Debug mode toggle
    debug_settings()

def user_admin_settings():
    """Admin settings for user management"""
    st.markdown("### User Management (Admin)")
    
    with st.expander("User Administration"):
        st.info("This section is only visible to administrators.")
        
        from auth import load_users
        
        # Load users
        user_data = load_users()
        users = user_data.get('users', [])
        
        # Display user list
        if users:
            st.markdown("#### Registered Users")
            for user in users:
                st.markdown(f"""
                **{user['full_name']}** ({user['username']})  
                Email: {user['email']}  
                Role: {user.get('role', 'user')}  
                Created: {user.get('created_at', 'Unknown')}
                """)
                st.markdown("---")
        else:
            st.warning("No users found in the system.")

def api_settings():
    """API key settings"""
    # OpenAI API Key input
    openai_api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.environ.get("OPENAI_API_KEY", ""),
        help="Enter your OpenAI API key here. It's required for embeddings and the chat model."
    )
    
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
    # Pinecone API Key input
    pinecone_api_key = st.text_input(
        "Pinecone API Key",
        type="password",
        value=os.environ.get("PINECONE_API_KEY", ""),
        help="Enter your Pinecone API key here if you want to use Pinecone as your vector store."
    )
    
    if pinecone_api_key:
        os.environ["PINECONE_API_KEY"] = pinecone_api_key

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

def vectorstore_settings():
    """Vector store settings"""
    st.markdown("### Vector Store Settings")
    
    # Vector store type selection
    vectorstore_type = st.radio(
        "Vector Store Type",
        ["Chroma", "Pinecone"],
        index=0 if st.session_state.get("vectorstore_type", "chroma") == "chroma" else 1,
        help="Select which vector database to use"
    )
    
    # Convert selection to lowercase for internal use
    st.session_state.vectorstore_type = vectorstore_type.lower()
    
    # Show appropriate settings based on vector store type
    if vectorstore_type == "Chroma":
        # For Chroma, always use in-memory storage
        st.info("Using Chroma with in-memory storage. Vector database will not be saved between sessions.")
    
    elif vectorstore_type == "Pinecone":
        # Pinecone settings
        st.markdown("#### Pinecone Settings")
        
        # Index name
        pinecone_index = st.text_input(
            "Pinecone Index Name",
            value=st.session_state.get("pinecone_index", ""),
            help="Enter the name of your Pinecone index"
        )
        st.session_state.pinecone_index = pinecone_index
        
        # Dimension info
        st.info("For OpenAI embeddings, use a Pinecone index with dimension=1536")
        
        # Check if Pinecone API key is set
        if not os.environ.get("PINECONE_API_KEY"):
            st.warning("Pinecone API key not set. Please enter it in the API Settings section above.")
            
        # Check if Pinecone index is set    
        if not pinecone_index:
            st.warning("Pinecone index name not set. Please enter a valid index name.")
            
        # Provide button to test Pinecone connection
        if st.button("Test Pinecone Connection"):
            with st.spinner("Testing Pinecone connection..."):
                try:
                    from pinecone import Pinecone
                    
                    # Initialize Pinecone client
                    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY", ""))
                    
                    # List indexes to test connection
                    indexes = pc.list_indexes().names()
                    
                    # Check if specified index exists
                    if pinecone_index in indexes:
                        st.success(f"Successfully connected to Pinecone. Index '{pinecone_index}' exists.")
                        
                        # Get index stats if available
                        try:
                            index = pc.Index(pinecone_index)
                            stats = index.describe_index_stats()
                            st.write(f"Index contains {stats.namespaces.get('', {}).get('vector_count', 0)} vectors")
                        except:
                            pass
                    else:
                        available_indexes = ", ".join(indexes) if indexes else "none"
                        st.warning(f"Connected to Pinecone, but index '{pinecone_index}' does not exist. Available indexes: {available_indexes}")
                        
                        # Offer to create the index
                        create_index = st.button("Create Index")
                        if create_index:
                            try:
                                # Try with ServerlessSpec
                                try:
                                    from pinecone import ServerlessSpec
                                    
                                    # Use ServerlessSpec for index creation
                                    pc.create_index(
                                        name=pinecone_index,
                                        dimension=1536,
                                        metric="cosine",
                                        spec=ServerlessSpec(
                                            cloud="aws",
                                            region="us-west-2"
                                        )
                                    )
                                except ImportError:
                                    # Fallback to basic index creation
                                    pc.create_index(
                                        name=pinecone_index,
                                        dimension=1536,
                                        metric="cosine"
                                    )
                                
                                st.success(f"Index '{pinecone_index}' created successfully!")
                            except Exception as e:
                                st.error(f"Error creating index: {str(e)}")
                
                except ImportError:
                    st.error("Pinecone Python client not installed. Please install with: pip install pinecone-client>=3.0.0")
                except Exception as e:
                    st.error(f"Error connecting to Pinecone: {str(e)}")
                    import traceback
                    st.error(f"Traceback: {traceback.format_exc()}")
                    
    # Add button to rebuild vector store
    if st.session_state.documents:
        if st.button("Rebuild Vector Store"):
            with st.spinner("Rebuilding vector store..."):
                try:
                    # Get vectorstore settings
                    use_in_memory = True  # Always use in-memory for Chroma
                    vectorstore_type = st.session_state.get("vectorstore_type", "chroma")
                    pinecone_index = st.session_state.get("pinecone_index", None)
                    
                    # Initialize vector store with appropriate settings
                    st.session_state.vectorstore = initialize_vectorstore(
                        st.session_state.documents, 
                        use_in_memory=use_in_memory,
                        vectorstore_type=vectorstore_type,
                        pinecone_index=pinecone_index
                    )
                    
                    if st.session_state.vectorstore:
                        st.success("Vector store rebuilt successfully!")
                    else:
                        st.error("Failed to rebuild vector store. Check settings and try again.")
                except Exception as e:
                    st.error(f"Error rebuilding vector store: {str(e)}")

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
    
    # Add authentication debug information
    st.write("### Authentication Debug")
    if st.session_state.get('current_user'):
        st.json(st.session_state.current_user)
    else:
        st.warning("No user is currently authenticated")
    
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
    
    # Add debug info based on vector store type
    vectorstore_type = st.session_state.get("vectorstore_type", "chroma")
    
    if vectorstore_type == "chroma":
        # Add information about SQLite version requirements
        st.markdown("""
        ### Chroma Information
        Chroma vector store has these requirements:
        - In-memory storage: Works with any SQLite version
        - Persistent storage: Requires SQLite 3.35.0+
        
        You can check your SQLite version by running:
        ```python
        import sqlite3
        print(sqlite3.sqlite_version)
        ```
        """)
    
    elif vectorstore_type == "pinecone":
        # Add Pinecone debug info
        st.markdown("""
        ### Pinecone Information
        Debug information for Pinecone:
        
        - Check Pinecone API key is set correctly
        - Verify index exists in your Pinecone account
        - Ensure the index dimension is 1536 for OpenAI embeddings
        
        You can check your Pinecone installation with:
        ```python
        import pinecone
        print(f"Pinecone client version: {pinecone.__version__}")
        ```
        
        This application uses a custom Pinecone implementation that doesn't rely on
        LangChain's Pinecone integration, which eliminates compatibility issues.
        """)

    