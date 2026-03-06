"""
Ingestion API - wraps backend ingestion logic
"""
import sys
import os
import boto3

# Add parent directory to import backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.config import config
from backend.ingestion import ingest_meeting, generate_meeting_id

def process_video_async(video_path, callback):
    """
    Process a video file asynchronously.
    
    Args:
        video_path: Path to video file
        callback: Function to call with (success: bool, message: str)
    """
    try:
        # Validate config
        config.validate()
        
        # Initialize AWS clients
        s3_client = boto3.client(
            's3',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            aws_session_token=config.AWS_SESSION_TOKEN
        )
        
        bedrock_runtime_client = boto3.client(
            'bedrock-runtime',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            aws_session_token=config.AWS_SESSION_TOKEN
        )
        
        bedrock_agent_client = boto3.client(
            'bedrock-agent',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            aws_session_token=config.AWS_SESSION_TOKEN
        )
        
        # Generate meeting ID
        filename = os.path.basename(video_path)
        meeting_id = generate_meeting_id(filename)
        
        # Process video
        success = ingest_meeting(
            video_path,
            meeting_id,
            config.MANIFEST_PATH,
            s3_client,
            bedrock_runtime_client,
            bedrock_agent_client
        )
        
        if success:
            callback(True, f"Video processed successfully: {meeting_id}")
        else:
            callback(False, "Processing failed - check logs for details")
    
    except Exception as e:
        callback(False, str(e))
