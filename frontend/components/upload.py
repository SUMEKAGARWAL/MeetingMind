"""
Upload component - handles video upload and processing
"""
import streamlit as st
import os
import sys
import subprocess
import time
import json

# Add parent directory to import backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def check_if_processed(filename):
    """Check if a video has been processed by looking at manifest."""
    # Get the MeetingMind root directory (parent of frontend)
    meetingmind_root = os.path.dirname(os.path.dirname(__file__))
    manifest_path = os.path.join(meetingmind_root, "data", "manifest.json")
    
    if not os.path.exists(manifest_path):
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            data = json.load(f)
            recordings = data.get('recordings', [])
            
            # Check if this filename is in the manifest
            # Note: The same filename can appear multiple times with different meeting_ids
            # We just check if ANY entry with this filename exists
            for rec in recordings:
                if rec.get('filename') == filename:
                    return True
            
            return False
    except Exception as e:
        # Debug: print error to help troubleshoot
        print(f"Error checking manifest: {e}")
        print(f"Manifest path: {manifest_path}")
        return False

def render_upload_section():
    """Render the video upload section."""
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload financial meeting recording (.mp4)",
        type=['mp4'],
        help="Upload earnings calls, board meetings, or financial presentations"
    )
    
    if uploaded_file is not None:
        # Show file info
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.info(f"📊 **{uploaded_file.name}** ({file_size_mb:.1f} MB)")
        
        # Process button
        if st.button("🚀 Analyze Meeting", type="primary", use_container_width=True):
            # Save uploaded file to MeetingMind/recordings
            meetingmind_root = os.path.dirname(os.path.dirname(__file__))
            recordings_dir = os.path.join(meetingmind_root, "recordings")
            os.makedirs(recordings_dir, exist_ok=True)
            
            file_path = os.path.join(recordings_dir, uploaded_file.name)
            
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"✅ Saved to recordings - AI analysis started!")
            st.info("⏳ Check the terminal for detailed progress. The meeting will appear in the sidebar when complete.")
            
            # Set processing status
            st.session_state.processing_status = {
                'filename': uploaded_file.name,
                'start_time': time.time()
            }
    
    # Check processing status
    if 'processing_status' in st.session_state and st.session_state.processing_status:
        status = st.session_state.processing_status
        filename = status['filename']
        
        # Check if processing is complete
        is_processed = check_if_processed(filename)
        
        if is_processed:
            st.success(f"✅ {filename} analyzed successfully!")
            st.balloons()
            if st.button("Clear", key="clear_success"):
                st.session_state.processing_status = None
                st.rerun()
        else:
            # Still processing
            elapsed = int(time.time() - status.get('start_time', time.time()))
            st.info(f"⏳ Analyzing {filename}... ({elapsed}s elapsed)")
            st.caption("Check terminal for detailed progress.")
            
            # Manual refresh button
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refresh Status", key="refresh_status"):
                    st.rerun()
            with col2:
                if st.button("❌ Clear", key="clear_processing"):
                    st.session_state.processing_status = None
                    st.rerun()
            
            # Auto-refresh every 5 seconds
            time.sleep(5)
            st.rerun()
    else:
        # Show informative content when not processing
        st.markdown("""
        <div style='margin-top: 30px; padding: 20px; background-color: #f7fafc; border-radius: 10px; border-left: 4px solid #667eea;'>
            <h4 style='color: #4a5568; margin-bottom: 15px;'>💼 Financial Meeting Types</h4>
            <ul style='color: #718096; line-height: 1.8;'>
                <li>📈 Quarterly Earnings Calls</li>
                <li>🏦 Board & Executive Meetings</li>
                <li>💰 Investor Presentations</li>
                <li>📊 Financial Planning Sessions</li>
                <li>🎯 Strategy & Budget Reviews</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='margin-top: 20px; padding: 20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 10px; color: white;'>
            <h4 style='margin-bottom: 10px;'>👩‍💼 Women Leading Finance</h4>
            <p style='font-size: 0.9em; line-height: 1.6;'>
                This AI assistant is built to empower women professionals in finance, 
                helping analyze complex financial discussions and extract actionable insights 
                from meetings with speed and accuracy.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Instructions
    with st.expander("ℹ️ How Financial AI Analysis Works"):
        st.markdown("""
        **AI-Powered Processing Pipeline:**
        1. 🎵 Extract and transcribe audio discussions
        2. 📊 Extract financial charts and presentations from video
        3. 🤖 AI describes visual financial data with context
        4. 📝 Merge audio insights with visual analytics
        5. ☁️ Upload to AWS Knowledge Base for intelligent search
        6. ✅ Ready for financial Q&A and insights!
        
        **Supported formats:** .mp4 video recordings
        
        **Best for:** Earnings calls, board meetings, financial presentations, investor meetings
        
        **Note:** Processing happens in the background using AWS Bedrock AI. 
        Check the terminal for detailed logs. The meeting will appear in the sidebar when analysis is complete.
        """)

