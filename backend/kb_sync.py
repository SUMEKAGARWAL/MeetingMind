"""
Bedrock Knowledge Base synchronization.
"""
import boto3
from backend.config import config


def sync_knowledge_base(
    bedrock_agent_client,
    kb_id: str = None,
    data_source_id: str = None
) -> bool:
    """
    Trigger Bedrock Knowledge Base sync.
    
    Args:
        bedrock_agent_client: Boto3 Bedrock Agent client
        kb_id: Knowledge Base ID (uses config if not provided)
        data_source_id: Data Source ID (uses config if not provided)
        
    Returns:
        True if sync started successfully, False otherwise
    """
    if kb_id is None:
        kb_id = config.BEDROCK_KB_ID
    if data_source_id is None:
        data_source_id = config.BEDROCK_DATA_SOURCE_ID
    
    if not kb_id or not data_source_id:
        print("   ⚠️  Warning: KB_ID or DATA_SOURCE_ID not configured, skipping KB sync")
        return False
    
    try:
        # Start ingestion job
        response = bedrock_agent_client.start_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=data_source_id
        )
        
        job_id = response['ingestionJob']['ingestionJobId']
        print(f"   Knowledge Base sync started (job: {job_id})")
        
        return True
        
    except bedrock_agent_client.exceptions.ConflictException as e:
        # Another ingestion job is already running - this is not a fatal error
        print(f"   ⚠️  KB sync skipped: Another ingestion job is already running")
        print(f"   The file was uploaded to S3 and will be synced when the current job completes")
        return False
        
    except Exception as e:
        # Other errors - log but don't fail the entire ingestion
        print(f"   ⚠️  KB sync failed: {e}")
        print(f"   The file was uploaded to S3 but may need manual sync")
        return False
