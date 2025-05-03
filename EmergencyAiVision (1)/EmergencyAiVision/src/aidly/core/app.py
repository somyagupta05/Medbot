import streamlit as st
import os
import io
from PIL import Image
import time
import base64
import markdown
from ..utils.image_processing import preprocess_image
from ..utils.gemini_api import get_gemini_response
from ..utils.location_services import find_nearest_hospitals
from ..utils.translation import translate_text

# Clear all session state to force a complete refresh
for key in list(st.session_state.keys()):
    del st.session_state[key]

# Initialize session state for chat history if not exists
if 'chatbot_history' not in st.session_state:
    st.session_state.chatbot_history = []

# Initialize input state if not exists
if 'input_text' not in st.session_state:
    st.session_state.input_text = ''

# Set English as the default language
st.session_state.language = 'en'

def send_message():
    if st.session_state.input_text.strip():
        # Add user message to chat
        st.session_state.chatbot_history.append({"role": "user", "content": st.session_state.input_text})
        
        # Get AI response
        with st.spinner("Getting response..."):
            response = get_chatbot_response(st.session_state.input_text, 'en')
            st.session_state.chatbot_history.append({"role": "assistant", "content": response})
        
        # Clear input only after successful send
        st.session_state.input_text = ''
        st.rerun()

def format_message(content):
    """Format message content with proper escaping and markdown conversion"""
    # First escape HTML special characters
    content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # Convert markdown to HTML (if the content contains markdown)
    if any(md_char in content for md_char in ['*', '#', '`', '_', '[']):
        content = markdown.markdown(content)
    else:
        # If no markdown, just convert newlines to <br>
        content = content.replace('\n', '<br>')
    return content

# Tab 3: Emergency Chat
with tab3:
    st.header("Emergency Guidance Chat")
    st.info("Ask questions about first aid or emergency procedures")

    # Chat interface styling
    st.markdown("""
    <style>
    /* Input field styling */
    .stTextInput>div>div>input {
        background-color: #f0f2f6;
        border-radius: 20px;
        padding: 10px 20px;
        font-size: 16px;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    .stTextInput>div>div>input:focus {
        border-color: #FF4B4B;
        box-shadow: 0 0 0 2px rgba(255, 75, 75, 0.1);
    }

    /* Button styling */
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
        width: 100%;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ff3333;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    /* Chat container styling */
    .chat-container {
        margin-bottom: 20px;
        padding: 10px;
    }

    /* Message styling */
    .user-message, .assistant-message {
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        line-height: 1.5;
    }

    .user-message {
        background-color: #e1f5fe;
        margin-left: 20%;
    }

    .assistant-message {
        background-color: #f0f2f6;
        margin-right: 20%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* Message headers */
    .message-header {
        font-weight: bold;
        margin-bottom: 8px;
        color: #333;
    }

    /* Message content */
    .message-content {
        font-size: 15px;
    }
    .message-content p {
        margin: 0 0 10px 0;
    }
    .message-content ul, .message-content ol {
        margin: 0 0 10px 20px;
        padding: 0;
    }
    .message-content li {
        margin: 5px 0;
    }
    .message-content strong {
        color: #FF4B4B;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .user-message {
            margin-left: 10%;
        }
        .assistant-message {
            margin-right: 10%;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Create a container for chat history
    chat_container = st.container()
    
    # Display chat history in the container
    with chat_container:
        for message in st.session_state.chatbot_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <div class="message-header">You:</div>
                    <div class="message-content">{format_message(message['content'])}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                formatted_content = format_message(message['content'])
                st.markdown(f"""
                <div class="assistant-message">
                    <div class="message-header">Aidly:</div>
                    <div class="message-content">{formatted_content}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # User input at the bottom
    st.text_input(
        "Type your question",
        key="input_text",
        placeholder="Describe your emergency situation or ask for first aid guidance...",
        on_change=send_message if st.session_state.input_text else None
    )
    
    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Send", use_container_width=True):
            send_message()
    
    with col2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chatbot_history = []
            st.session_state.input_text = ''

# ... existing code ... 