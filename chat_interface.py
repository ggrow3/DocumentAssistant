import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from citation_handler import CitationTrackingHandler
from document_context import build_document_context_panel
from utils import format_tags_html

def get_system_prompt(legal_expert_mode=True):
    """
    Get the system prompt for the chat model based on settings
    
    Args:
        legal_expert_mode: Whether to use legal expert mode
        
    Returns:
        String containing the system prompt
    """
    # Base system prompt
    base_prompt = """You are a helpful AI assistant for a law firm handling legal documents and cases."""
    
    # Legal expert mode prompt
    if legal_expert_mode:
        legal_prompt = """
        You are an expert legal assistant with extensive knowledge of legal terminology, procedures, and precedents.
        
        Adhere to the following guidelines in all responses:
        
        1. FACTUAL ACCURACY: Provide only factually accurate information. Do not make anything up. If you are unsure about a fact, clearly state your uncertainty and refrain from speculation.
        
        2. LEGAL LANGUAGE: Use precise legal terminology and legalese when appropriate. Demonstrate your knowledge of proper legal vernacular, citations, and formatting.
        
        3. EVIDENCE-BASED REASONING: Base all analyses on the documents and evidence provided. Cite specific passages and sources when available.
        
        4. FORMAL STRUCTURE: Structure responses in a formal, professional manner consistent with legal documentation.
        
        5. OBJECTIVE ANALYSIS: Maintain objectivity and present multiple perspectives when addressing complex legal questions.
        
        6. CONTEXTUAL AWARENESS: Consider the relevant jurisdiction, practice area, and specific legal context in all responses.
        
        7. CLARITY IN LIMITATIONS: Clearly state when a question falls outside the scope of the provided documents or your capabilities.
        
        Remember: You are assisting legal professionals who require precision, accuracy, and adherence to formal conventions in legal practice.
        """
        return base_prompt + legal_prompt
    else:
        # Default mode - more conversational but still professional
        return base_prompt + """
        Provide helpful information about legal documents and answer questions in a clear, professional manner.
        Focus on accuracy and clarity in your responses.
        """

def build_chat_interface():
    """Build the main chat interface"""
    # Create two columns for the chat layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat messages and input
        build_chat_messages_panel()
        
    with col2:
        # Document context panel
        build_document_context_panel()

def build_chat_messages_panel():
    """Build the chat messages panel"""
    st.markdown("### Legal Document Assistant Chat")
    
    # Add a toggle for showing/hiding citations in chat
    if 'show_citations' not in st.session_state:
        st.session_state.show_citations = True
    
    # Toggle button for showing/hiding citations
    show_citations = st.toggle("Show Citations in Messages", value=st.session_state.show_citations)
    st.session_state.show_citations = show_citations
    
    # Display chat messages from history
    display_chat_history(show_citations)
    
    # User input area
    user_input = st.text_area("Your message:", key="user_input", height=100)
    
    # Get OpenAI API key
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    
    # Check conditions for enabling the chat
    chat_disabled = not openai_api_key or st.session_state.vectorstore is None
    
    # Send button with conditional enabling
    send_button = st.button("Send", disabled=chat_disabled)
    
    if chat_disabled:
        display_chat_disabled_warnings(openai_api_key)
    
    # Process user input and generate response
    if send_button and user_input and not chat_disabled:
        process_chat_input(user_input)

def display_chat_history(show_citations=True):
    """Display the chat history with messages and citations"""
    for i, message in enumerate(st.session_state.chat_history):
        avatar = "👨‍⚖️" if message["role"] == "user" else "🤖"
        with st.container():
            st.markdown(f"""
            <div class="chat-message {message['role']}">
                <div class="avatar">{avatar}</div>
                <div class="message">{message['content']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display citations if available and if show_citations is True
            if message.get("citations") and show_citations:
                st.markdown("<div style='margin-left: 40px;'>Sources:</div>", unsafe_allow_html=True)
                for citation in message["citations"]:
                    # Include tags in the citation display if they exist
                    tag_html = format_tags_html(citation.get("tags", [])) if citation.get("tags") else ""
                    
                    with st.expander(f"From: {citation['source']} (Page {citation['page'] + 1})"):
                        st.markdown(f"""
                        <div class="citation">
                            {citation['text']}
                        </div>
                        {tag_html}
                        """, unsafe_allow_html=True)
            elif message.get("citations") and not show_citations:
                st.markdown(f"<div style='margin-left: 40px; font-style: italic; color: #888;'>{len(message['citations'])} citations hidden. Toggle 'Show Citations in Messages' to view them.</div>", unsafe_allow_html=True)

def display_chat_disabled_warnings(openai_api_key):
    """Display warnings when chat is disabled"""
    if not openai_api_key:
        st.warning("Please enter your OpenAI API key in the settings panel to enable chat.")
    if st.session_state.vectorstore is None:
        st.warning("Please upload at least one document to enable chat.")

def process_chat_input(user_input):
    """Process the user input and generate a response"""
    # Add user message to chat history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })
    
    # Setup citation handler
    citation_handler = CitationTrackingHandler()
    
    # Get the retriever from the vectorstore
    retriever = st.session_state.vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}  # Return top 5 relevant documents
    )
    
    # Initialize the model with system prompt from settings
    model_name = st.session_state.settings.get("model_name", "gpt-4")
    temperature = st.session_state.settings.get("temperature", 0.0)
    legal_expert_mode = st.session_state.settings.get("legal_expert_mode", True)
    
    # Get the system prompt based on settings
    system_prompt = get_system_prompt(legal_expert_mode)
    
    # Initialize the ChatOpenAI (without system parameter)
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=temperature
        # Remove the system parameter
    )
    
    # Show spinner while processing
    with st.spinner("Thinking..."):
        try:
            # First retrieve relevant documents using invoke() method
            retrieved_docs = retriever.invoke(user_input)
            
            # Debug information
            if st.session_state.get("debug_mode", False):
                st.write(f"Retrieved {len(retrieved_docs)} documents")
                for i, doc in enumerate(retrieved_docs[:2]):
                    st.write(f"Document {i}:")
                    st.write(f"  Content: {doc.page_content[:100]}...")
                    st.write(f"  Metadata: {doc.metadata}")
            
            # Process citations from retrieved documents
            citation_handler.on_retriever_end(retrieved_docs)
            
            # Set up a simple template that includes the system prompt
            template = f"""
            {system_prompt}
            
            Answer the question based on the following context:

            Context:
            {{context}}

            Question: {{question}}

            Instructions:
            1. Base your answer only on the provided context
            2. If you don't know the answer based on the context, say so
            3. Keep your answer concise and focused on the question
            4. Include specific references to the documents you're using
            5. Use formal legal terminology when appropriate
            6. Provide only factually accurate information and do not make anything up
            7. If you're unsure about a fact, clearly state your uncertainty
            """
            
            prompt = PromptTemplate(
                input_variables=["context", "question"],
                template=template
            )
            
            # Format context from retrieved documents
            context = "\n\n".join([doc.page_content for doc in retrieved_docs])
            
            # Call LLM
            response = llm.invoke(
                prompt.format(context=context, question=user_input)
            ).content
            
            # Add assistant message to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "citations": citation_handler.citations
            })
            
            # Clear user input
            st.rerun()
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            
            # Enable debug mode automatically when there's an error
            st.session_state.debug_mode = True
            st.warning("Debug mode enabled due to error.")