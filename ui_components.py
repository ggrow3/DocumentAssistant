import streamlit as st

# CSS styles for the UI
def apply_custom_css():
    """Apply custom CSS styles to the Streamlit app"""
    st.markdown("""
    <style>
     
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