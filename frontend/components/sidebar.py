"""
Sidebar component - displays list of processed videos
"""
import streamlit as st
import os
import json
from datetime import datetime

def load_processed_videos():
    """Load list of processed videos from manifest."""
    # Get the MeetingMind root directory (parent of frontend)
    meetingmind_root = os.path.dirname(os.path.dirname(__file__))
    manifest_path = os.path.join(meetingmind_root, "data", "manifest.json")
    
    if not os.path.exists(manifest_path):
        return []
    
    try:
        with open(manifest_path, 'r') as f:
            data = json.load(f)
            return data.get('recordings', [])
    except Exception as e:
        st.error(f"Error loading videos: {e}")
        return []

def render_sidebar():
    """Render the sidebar with video list."""
    # Project title at the top
    st.markdown("""
    <div style='text-align: center; padding: 10px 0 20px 0; border-bottom: 2px solid #4a5568; margin-bottom: 20px;'>
        <h2 style='color: #4a5568; margin: 0; font-size: 1.3em;'>💼 MeetingMind</h2>
        <p style='color: #718096; margin: 5px 0 0 0; font-size: 0.85em;'>Financial AI Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📈 Financial Meeting Records")
    
    # Add custom CSS for selected video styling
    st.markdown("""
    <style>
    /* Override primary button styling with dark background */
    div[data-testid="stSidebar"] button[kind="primary"] {
        background-color: #2d3748 !important;
        border: 2px solid #4a5568 !important;
        border-radius: 8px !important;
        color: white !important;
    }
    div[data-testid="stSidebar"] button[kind="primary"]:hover {
        background-color: #374151 !important;
        border-color: #6b7280 !important;
    }
    div[data-testid="stSidebar"] button[kind="secondary"] {
        border: 1px solid transparent !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    videos = load_processed_videos()
    
    if not videos:
        st.info("📊 No financial meetings processed yet. Upload a recording to get started!")
        return
    
    # Sort by processed date (newest first)
    videos_sorted = sorted(
        videos,
        key=lambda x: x.get('processed_at', ''),
        reverse=True
    )
    
    for video in videos_sorted:
        meeting_id = video.get('meeting_id', 'Unknown')
        filename = video.get('filename', 'Unknown')
        duration = video.get('duration', 0)
        processed_at = video.get('processed_at', '')
        
        # Format date
        try:
            date_obj = datetime.fromisoformat(processed_at.replace('Z', '+00:00'))
            date_str = date_obj.strftime("%b %d, %H:%M")
        except:
            date_str = "Unknown date"
        
        # Format duration
        duration_str = f"{int(duration)}s" if duration else "N/A"
        
        # Create clickable card
        is_selected = st.session_state.selected_video == meeting_id
        
        if st.button(
            f"{'💼' if is_selected else '📄'} {filename}\n{date_str} • {duration_str}",
            key=f"video_{meeting_id}",
            use_container_width=True,
            type="primary" if is_selected else "secondary"
        ):
            st.session_state.selected_video = meeting_id
            st.session_state.chat_history = []  # Clear chat history when switching videos
            st.rerun()
    
    st.markdown("---")
    st.caption(f"📊 Total meetings analyzed: {len(videos)}")
