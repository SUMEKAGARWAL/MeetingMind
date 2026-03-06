#!/usr/bin/env python3
"""
MeetingMind Ingestion Entry Point

Automatically processes meeting recordings from the recordings/ folder.
Scans for unprocessed files on startup, then watches for new files.
"""
import os
import sys
import boto3

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.config import config
from backend.file_watcher import scan_and_process_folder, watch_recordings_folder


def main():
    """Main entry point for ingestion service."""
    print("=" * 60)
    print("MeetingMind Ingestion Service")
    print("=" * 60)
    print()
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease create a .env file with your AWS credentials.")
        print("See .env.example for template.")
        return 1
    
    # Initialize AWS clients
    print("Initializing AWS clients...")
    try:
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
        
        print("✓ AWS clients initialized\n")
        
    except Exception as e:
        print(f"❌ Failed to initialize AWS clients: {e}")
        return 1
    
    # Ensure directories exist
    os.makedirs(config.RECORDINGS_DIR, exist_ok=True)
    os.makedirs(config.AUDIO_DIR, exist_ok=True)
    os.makedirs(config.FRAMES_DIR, exist_ok=True)
    os.makedirs(config.TRANSCRIPTS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(config.MANIFEST_PATH), exist_ok=True)
    
    # Step 1: Scan for existing unprocessed files
    print("Step 1: Scanning for unprocessed recordings...")
    processed = scan_and_process_folder(
        config.RECORDINGS_DIR,
        config.MANIFEST_PATH,
        s3_client,
        bedrock_runtime_client,
        bedrock_agent_client
    )
    
    if processed:
        print(f"✓ Processed {len(processed)} recordings on startup\n")
    
    # Step 2: Start watching for new files
    print("Step 2: Starting file watcher...")
    try:
        watch_recordings_folder(
            config.RECORDINGS_DIR,
            config.MANIFEST_PATH,
            s3_client,
            bedrock_runtime_client,
            bedrock_agent_client
        )
    except KeyboardInterrupt:
        print("\n\n✓ Ingestion service stopped")
        return 0


if __name__ == "__main__":
    sys.exit(main())
