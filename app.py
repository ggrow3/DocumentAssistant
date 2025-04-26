import streamlit as st
import os
import gc
import tempfile
import atexit
from ui_components import apply_custom_css, add_tag_management_js
from sidebar import build_sidebar
from chat_interface import build_chat_interface
from about_page import about_page
from system_check import check_dependencies
from auth import display_auth_interface, create_default_admin

# Configure tempfile to not delete files immediately
# This allows us to handle file closing more carefully
tempfile.tempdir = tempfile.gettempdir()

# Register cleanup function to remove any leftover temporary files on exit
def cleanup_temp_files():
    temp_dir = tempfile.gettempdir()
    try:
        # Force garbage collection to release file handles
        gc.collect()
    except Exception as e:
        print(f"Error during cleanup: {e}")

atexit.register(cleanup_temp_files)

# Configure page
st.set_page_config(
    page_title="Legal Document AI Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS and add JavaScript for tag management
apply_custom_css()
add_tag_management_js()

# Initialize session state
def initialize_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'documents' not in st.session_state:
        st.session_state.documents = []
    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Chat"
    if 'tags' not in st.session_state:
        st.session_state.tags = set()  # Set of all unique tags
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False
    if "settings" not in st.session_state:
        st.session_state.settings = {
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7
        }
    if "show_sources" not in st.session_state:
        st.session_state.show_sources = True
    if "show_citations" not in st.session_state:
        st.session_state.show_citations = True

# Handle custom component events
def handle_custom_events():
    # Handle tag removal events
    if "tag_event" in st.session_state:
        event_data = st.session_state.tag_event
        if event_data and "type" in event_data and event_data["type"] == "removeTag":
            doc_id = event_data["doc_id"]
            tag = event_data["tag"]
            # Set a session state flag to remove this tag in the sidebar
            st.session_state[f"remove_tag_{doc_id}"] = tag
            # Clear the event
            st.session_state.tag_event = None
            st.rerun()

# Display a welcome message after login
def display_welcome_message():
    if st.session_state.current_user:
        current_time = st.session_state.get('last_activity').strftime('%H:%M')
        st.write(f"### Welcome to Legal Document AI Assistant, {st.session_state.current_user['full_name']}!")
        st.write(f"You logged in at {current_time}. Start by uploading documents in the sidebar.")
        
        # Show a tip for first-time users
        with st.expander("New to Legal Document AI Assistant?"):
            st.markdown("""
            **Getting Started Guide:**
            
            1. Upload your legal documents using the Document Management tab in the sidebar
            2. Add tags to organize and categorize your documents
            3. Ask questions about your documents using the chat interface
            4. View source documents and their context in the Document Context panel
            
            Need more help? Check out the About tab for detailed information on features and usage.
            """)

# Main app layout
def main():
    # Initialize session state
    initialize_session_state()
    
    # Create default admin user if no users exist
    create_default_admin()
    
    # Display authentication interface
    # This will stop execution if user is not authenticated
    display_auth_interface()
    
    # Handle any custom events
    handle_custom_events()
    
    # Create sidebar (for authenticated users)
    build_sidebar()
    
    # Create main interface
    tabs = ["Chat", "About"]
    selected_tab = st.radio("Main interface sections", tabs, horizontal=True, label_visibility="collapsed")
    
    if selected_tab == "Chat":
        # Display welcome message if this is the first view after login
        if st.session_state.get('show_welcome', True):
            display_welcome_message()
            st.session_state.show_welcome = False
        
        # Build chat interface
        build_chat_interface()
    
    elif selected_tab == "About":
        about_page()

    # Check for required dependencies
    with st.expander("System Information", expanded=False):
        check_dependencies()

if __name__ == "__main__":
    main()