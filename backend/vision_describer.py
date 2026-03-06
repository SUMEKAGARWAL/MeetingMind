"""
Vision description using Claude 3.5 Sonnet on AWS Bedrock.
"""
import base64
import json
import boto3
from typing import List
from backend.models import FrameDescription
from backend.config import config


def describe_frame(
    frame_path: str,
    timestamp: float,
    bedrock_client
) -> FrameDescription:
    """
    Generate description of frame using Nova Pro Vision.
    
    Args:
        frame_path: Path to frame image
        timestamp: Timestamp of frame in seconds
        bedrock_client: Boto3 Bedrock Runtime client
        
    Returns:
        FrameDescription with timestamp and description
    """
    # Read and encode image
    with open(frame_path, 'rb') as f:
        image_bytes = f.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # Prepare prompt for Nova Pro Vision
    prompt = """Describe in detail what is shown on this screen. Focus on:
- Any text visible on screen (code, configuration, documents, chat messages)
- Any diagrams, charts, graphs, or visual elements
- UI elements (which application is shown, what section is visible)
- Any data values, numbers, or metrics visible

Be specific and include exact text/values where readable."""
    
    # Prepare request body for Nova Pro
    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": "jpeg",
                            "source": {
                                "bytes": image_base64
                            }
                        }
                    },
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "inferenceConfig": {
            "max_new_tokens": 1000
        }
    }
    
    try:
        # Call Nova Pro Vision API
        response = bedrock_client.invoke_model(
            modelId=config.BEDROCK_MODEL_ID_VISION,
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        description = response_body['output']['message']['content'][0]['text']
        
        return FrameDescription(
            timestamp=timestamp,
            description=description,
            frame_path=frame_path
        )
        
    except Exception as e:
        raise Exception(f"Nova Pro Vision API call failed: {e}")


def describe_all_frames(
    frames: List,
    bedrock_client
) -> List[FrameDescription]:
    """
    Describe all frames with progress logging.
    
    Args:
        frames: List of Keyframe objects
        bedrock_client: Boto3 Bedrock Runtime client
        
    Returns:
        List of FrameDescription objects
    """
    descriptions = []
    
    for i, frame in enumerate(frames, 1):
        try:
            desc = describe_frame(frame.frame_path, frame.timestamp, bedrock_client)
            descriptions.append(desc)
            print(f"      Described frame {i}/{len(frames)}")
        except Exception as e:
            print(f"      ⚠️  Failed to describe frame {i}: {e}")
            # Continue with remaining frames
            continue
    
    return descriptions
