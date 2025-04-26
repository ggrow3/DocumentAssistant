import streamlit as st

# CSS styles for the UI
def apply_custom_css():
    """Apply custom CSS styles to the Streamlit app"""
    st.markdown("""
    <style>
        /* Base styling */
        .main {
            padding: 0rem 1rem;
        }
        
        /* Chat message styling */
        .chat-message {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: row;
            align-items: flex-start;
            gap: 0.5rem;
            background-color: #f0f0f0;
        }
        
        .chat-message.user {
            background-color: #e6f3ff;
            border-left: 5px solid #2e86de;
        }
        
        .chat-message.assistant {
            background-color: #f0f0f0;
            border-left: 5px solid #6c757d;
        }
        
        .chat-message .avatar {
            min-width: 40px;
        }
        
        .chat-message .message {
            flex-grow: 1;
        }
        
        /* Citation styling */
        .citation {
            background-color: #fff8e1;
            border-left: 3px solid #ffcc80;
            padding: 0.5rem;
            margin: 0.5rem 0;
            font-size: 0.9rem;
            border-radius: 0.25rem;
        }
        
        /* Document item styling */
        .doc-item {
            padding: 0.5rem;
            border-bottom: 1px solid #eee;
        }
        
        .doc-item:hover {
            background-color: #f0f0f0;
        }
        
        /* Tag styling */
        .tag-container {
            margin: 0.5rem 0;
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }
        
        .tag-item {
            display: inline-flex;
            align-items: center;
            background-color: #e9ecef;
            color: #495057;
            padding: 0.3rem 0.6rem;
            border-radius: 1rem;
            font-size: 0.8rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
            border: 1px solid #dee2e6;
        }
        
        .tag-item:hover {
            background-color: #dee2e6;
            box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        }
        
        .tag-remove-btn {
            margin-left: 0.3rem;
            color: #dc3545;
            background: none;
            border: none;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            padding: 0 0.3rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
        }
        
        .tag-remove-btn:hover {
            background-color: rgba(220, 53, 69, 0.2);
        }
        
        /* Tag editor styling */
        .tag-editor {
            margin-top: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .tag-editor input {
            flex-grow: 1;
            padding: 0.3rem 0.5rem;
            border-radius: 0.25rem;
            border: 1px solid #ced4da;
            font-size: 0.9rem;
        }
        
        .tag-editor button {
            background-color: #2e86de;
            color: white;
            border: none;
            border-radius: 0.25rem;
            padding: 0.3rem 0.6rem;
            font-size: 0.8rem;
            cursor: pointer;
        }
        
        .tag-editor button:hover {
            background-color: #1c7ed6;
        }
        
        /* Toggle styles */
        .stCheckbox {
            margin-bottom: 1rem;
        }
        
        /* Citation count style */
        .citation-count {
            color: #6c757d;
            font-style: italic;
            margin-left: 1rem;
            font-size: 0.9rem;
        }
        
        /* Tag management tools */
        .tag-tools {
            margin-top: 0.5rem;
            margin-bottom: 1rem;
            padding: 0.5rem;
            background-color: #f8f9fa;
            border-radius: 0.25rem;
            border: 1px solid #e9ecef;
        }
        
        .tag-tools-header {
            font-weight: bold;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            color: #495057;
        }
    </style>
    """, unsafe_allow_html=True)

def add_tag_management_js():
    """Add JavaScript for tag management"""
    st.markdown("""
    <script>
        // Function to handle tag removal events
        function setupTagRemoval() {
            // Add event listeners to all tag remove buttons
            document.querySelectorAll('.tag-remove-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const docId = this.getAttribute('data-doc-id');
                    const tag = this.getAttribute('data-tag');
                    // Send message to Streamlit
                    if (window.parent && window.parent.postMessage) {
                        window.parent.postMessage({
                            type: 'streamlit:removeTag',
                            docId: docId,
                            tag: tag
                        }, '*');
                    }
                });
            });
        }
        
        // Run setup when the DOM is fully loaded
        document.addEventListener('DOMContentLoaded', setupTagRemoval);
        
        // Also run setup when Streamlit reruns (for dynamically added buttons)
        if (window.parent) {
            window.parent.addEventListener('message', function(e) {
                if (e.data.type === 'streamlit:render') {
                    // Wait a bit for the DOM to update
                    setTimeout(setupTagRemoval, 100);
                }
            });
        }
    </script>
    """, unsafe_allow_html=True)