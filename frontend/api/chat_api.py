"""
Chat API - wraps backend chat logic
"""
import sys
import os
import boto3

# Add parent directory to import backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.config import config
from backend.chat import retrieve_and_generate

# Initialize AWS client (reuse across requests)
_bedrock_agent_runtime_client = None

def get_bedrock_client():
    """Get or create Bedrock Agent Runtime client."""
    global _bedrock_agent_runtime_client
    
    if _bedrock_agent_runtime_client is None:
        _bedrock_agent_runtime_client = boto3.client(
            'bedrock-agent-runtime',
            region_name=config.AWS_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            aws_session_token=config.AWS_SESSION_TOKEN
        )
    
    return _bedrock_agent_runtime_client

def send_message(user_message: str) -> str:
    """
    Send a message to the Bedrock Agent and get response.
    
    Args:
        user_message: User's question
        
    Returns:
        Agent's response text
    """
    try:
        client = get_bedrock_client()
        response = retrieve_and_generate(user_message, [], client)
        return response.answer
    except Exception as e:
        raise Exception(f"Bedrock Agent call failed: {e}")
