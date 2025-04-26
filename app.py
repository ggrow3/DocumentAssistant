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

# Main app layout
def main():
    # Initialize session state
    initialize_session_state()
    
    # Handle any custom events
    handle_custom_events()
    
    # Create sidebar
    build_sidebar()
    
    # Create main interface
    tabs = ["Chat", "About"]
    selected_tab = st.radio("Main interface sections", tabs, horizontal=True, label_visibility="collapsed")
    
    if selected_tab == "Chat":
        build_chat_interface()
    
    elif selected_tab == "About":
        about_page()

    # Check for required dependencies
    with st.expander("System Information", expanded=False):
        check_dependencies()

if __name__ == "__main__":
    main()