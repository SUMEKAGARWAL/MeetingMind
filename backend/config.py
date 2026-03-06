"""
Configuration management for MeetingMind.
Loads settings from environment variables with sensible defaults.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration settings for MeetingMind."""
    
    # AWS Configuration
    AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN", None)  # Optional - only for temporary credentials
    
    # Bedrock Configuration
    BEDROCK_MODEL_ID_VISION = "us.amazon.nova-pro-v1:0"  # Nova Pro supports vision
    BEDROCK_MODEL_ID_CHAT = "meta.llama3-3-70b-instruct-v1:0"
    BEDROCK_KB_ID = os.getenv("BEDROCK_KB_ID")
    BEDROCK_DATA_SOURCE_ID = os.getenv("BEDROCK_DATA_SOURCE_ID")
    BEDROCK_AGENT_ID = os.getenv("BEDROCK_AGENT_ID")
    
    # S3 Configuration
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    
    # Directory Paths
    RECORDINGS_DIR = "recordings"
    FRAMES_DIR = "data/frames"
    AUDIO_DIR = "data/audio"
    TRANSCRIPTS_DIR = "data/transcripts"
    MANIFEST_PATH = "data/manifest.json"
    
    # Processing Configuration
    KEYFRAME_INTERVAL_SECONDS = int(os.getenv("KEYFRAME_INTERVAL_SECONDS", "20"))
    PHASH_THRESHOLD = int(os.getenv("PHASH_THRESHOLD", "8"))
    WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "tiny")
    
    # Screen-Share Detection Configuration
    SCREENSHARE_ENABLED = os.getenv("SCREENSHARE_ENABLED", "true").lower() == "true"
    SCREENSHARE_EDGE_DENSITY_MIN = float(os.getenv("SCREENSHARE_EDGE_DENSITY_MIN", "0.15"))
    SCREENSHARE_TEXT_REGION_MIN = int(os.getenv("SCREENSHARE_TEXT_REGION_MIN", "3"))
    
    # Chat Configuration
    MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "10"))
    
    @classmethod
    def validate(cls):
        """Validate that required configuration values are set."""
        required = [
            ("AWS_ACCESS_KEY_ID", cls.AWS_ACCESS_KEY_ID),
            ("AWS_SECRET_ACCESS_KEY", cls.AWS_SECRET_ACCESS_KEY),
            ("S3_BUCKET_NAME", cls.S3_BUCKET_NAME),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}. "
                "Please set these in your .env file."
            )
        
        # Warn about optional Bedrock IDs (needed for full functionality)
        optional = [
            ("BEDROCK_KB_ID", cls.BEDROCK_KB_ID),
            ("BEDROCK_DATA_SOURCE_ID", cls.BEDROCK_DATA_SOURCE_ID),
            ("BEDROCK_AGENT_ID", cls.BEDROCK_AGENT_ID),
        ]
        
        missing_optional = [name for name, value in optional if not value]
        if missing_optional:
            print(f"⚠️  Warning: Optional configuration not set: {', '.join(missing_optional)}")
            print("   Some features may not work until these are configured.")


# Create global config instance
config = Config()
