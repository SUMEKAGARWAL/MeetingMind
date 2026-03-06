#!/usr/bin/env python3
"""
MeetingMind Web UI - Main Streamlit Application
"""
import streamlit as st
import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from components.sidebar import render_sidebar
from components.upload import render_upload_section
from components.chat_interface import render_chat_interface

# Page configuration
st.set_page_config(
    page_title="MeetingMind - Financial AI Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'selected_video' not in st.session_state:
    st.session_state.selected_video = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = None

# Sidebar with video list
with st.sidebar:
    render_sidebar()

# Main layout - Chat in middle, Upload on right
st.title("💼 MeetingMind Financial AI")
st.markdown("*Empowering Women in Finance with AI-Powered Meeting Intelligence*")
st.caption("🏆 Women in Financial AI - AWS Cloud Women Agentic AI Hackathon")
st.markdown("---")

# Two columns: Chat (larger) and Upload (smaller)
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("💬 Financial Insights Chat")
    render_chat_interface()

with col2:
    st.subheader("📊 Upload Financial Meeting")
    render_upload_section()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.85em;'>"
    "💡 Built by Women, For Women in Finance | Powered by AWS Bedrock & Agentic AI"
    "</div>",
    unsafe_allow_html=True
)
