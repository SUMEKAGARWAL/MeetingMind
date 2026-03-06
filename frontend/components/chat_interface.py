"""
Chat interface component
"""
import streamlit as st
import sys
import os

# Add parent directory to import backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from api.chat_api import send_message

def render_chat_interface():
    """Render the chat interface."""
    
    # Check if a video is selected
    if not st.session_state.selected_video:
        st.info("👈 Select a financial meeting from the sidebar to start analyzing")
        return
    
    # Create a scrollable container for chat messages
    chat_container = st.container(height=500)
    
    with chat_container:
        # Display chat history
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                with st.chat_message("user", avatar="👩‍💼"):
                    st.markdown(message['content'])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message['content'])
    
    # Chat input (always at bottom, outside the scrollable container)
    user_input = st.chat_input("Ask about financial metrics, insights, or meeting details...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })
        
        # Get assistant response
        with st.spinner("Analyzing financial data..."):
            try:
                response = send_message(user_input)
                
                # Add assistant message to history
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response
                })
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': error_msg
                })
        
        st.rerun()
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Analysis", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
