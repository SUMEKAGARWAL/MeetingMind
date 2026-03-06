#!/usr/bin/env python3
"""
MeetingMind Chat Entry Point

Interactive CLI for asking questions about processed meetings.
"""
import os
import sys
import boto3

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.config import config
from backend.cli_chat import run_cli_chat


def main():
    """Main entry point for chat interface."""
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease create a .env file with your AWS credentials.")
        print("See .env.example for template.")
        return 1
    
    # Initialize Bedrock Agent client
    try:
        bedrock_agent_client = boto3.client(
            'bedrock-agent-runtime',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            aws_session_token=config.AWS_SESSION_TOKEN
        )
    except Exception as e:
        print(f"❌ Failed to initialize Bedrock client: {e}")
        return 1
    
    # Run chat interface
    try:
        run_cli_chat(bedrock_agent_client, agent_id=config.BEDROCK_AGENT_ID)
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        return 0
    except Exception as e:
        print(f"\n❌ Chat error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
