"""
S3 upload for unified documents.
"""
import json
import boto3
from backend.models import UnifiedDocument
from backend.config import config


def upload_to_s3(
    document: UnifiedDocument,
    s3_client,
    bucket: str = None,
    key_prefix: str = "meetings"
) -> str:
    """
    Upload unified document to S3.
    
    Args:
        document: UnifiedDocument to upload
        s3_client: Boto3 S3 client
        bucket: S3 bucket name (uses config if not provided)
        key_prefix: Prefix for S3 key (default: "meetings")
        
    Returns:
        S3 URI (s3://bucket/key)
    """
    if bucket is None:
        bucket = config.S3_BUCKET_NAME
    
    # Generate S3 key
    key = f"{key_prefix}/{document.meeting_id}.json"
    
    # Serialize document to JSON
    document_json = json.dumps(document.model_dump(), indent=2, default=str)
    
    try:
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=document_json.encode('utf-8'),
            ContentType='application/json'
        )
        
        # Return S3 URI
        s3_uri = f"s3://{bucket}/{key}"
        return s3_uri
        
    except Exception as e:
        raise Exception(f"S3 upload failed: {e}")
