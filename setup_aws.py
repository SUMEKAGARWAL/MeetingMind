#!/usr/bin/env python3
"""
MeetingMind AWS Setup Script (Python version)
Creates S3 bucket, Bedrock Knowledge Base, and Bedrock Agent using boto3
"""
import boto3
import json
import time
import sys
from datetime import datetime
from backend.config import config

def print_step(step_num, message):
    """Print formatted step message."""
    print(f"\nStep {step_num}: {message}...")

def print_success(message):
    """Print success message."""
    print(f"✓ {message}")

def print_error(message):
    """Print error message."""
    print(f"❌ {message}")

def main():
    print("=" * 60)
    print("MeetingMind AWS Setup")
    print("=" * 60)
    print()
    
    # Configuration
    region = config.AWS_REGION
    timestamp = int(datetime.now().timestamp())
    bucket_name = f"meetingmind-{timestamp}"
    kb_name = "MeetingMind-KB"
    agent_name = "MeetingMind-Agent"
    embedding_model = "amazon.titan-embed-text-v1"
    chat_model = "meta.llama3-3-70b-instruct-v1:0"
    
    print("Configuration:")
    print(f"  Region: {region}")
    print(f"  S3 Bucket: {bucket_name}")
    print(f"  Knowledge Base: {kb_name}")
    print(f"  Agent: {agent_name}")
    print()
    
    # Initialize AWS clients
    print_step(1, "Initializing AWS clients")
    try:
        sts = boto3.client(
            'sts',
            region_name=region,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            aws_session_token=config.AWS_SESSION_TOKEN
        )
        
        # Verify credentials
        identity = sts.get_caller_identity()
        account_id = identity['Account']
        user_arn = identity['Arn']
        print_success(f"AWS credentials valid (Account: {account_id})")
        
        # Initialize other clients
        s3 = boto3.client(
            's3',
            region_name=region,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            aws_session_token=config.AWS_SESSION_TOKEN
        )
        
        iam = boto3.client(
            'iam',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            aws_session_token=config.AWS_SESSION_TOKEN
        )
        
        aoss = boto3.client(
            'opensearchserverless',
            region_name=region,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            aws_session_token=config.AWS_SESSION_TOKEN
        )
        
        bedrock_agent = boto3.client(
            'bedrock-agent',
            region_name=region,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            aws_session_token=config.AWS_SESSION_TOKEN
        )
        
    except Exception as e:
        print_error(f"Failed to initialize AWS clients: {e}")
        print("\nPlease check your AWS credentials in .env file")
        return 1
    
    # Create S3 Bucket
    print_step(2, "Creating S3 bucket")
    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
        print_success(f"S3 bucket created: s3://{bucket_name}")
        
        # Enable versioning
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print_success("Versioning enabled")
        
    except Exception as e:
        print_error(f"S3 bucket creation failed: {e}")
        return 1
    
    # Create IAM role for Knowledge Base
    print_step(3, "Creating IAM role for Knowledge Base")
    try:
        kb_role_name = f"MeetingMind-KB-Role-{timestamp}"
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        role_response = iam.create_role(
            RoleName=kb_role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        kb_role_arn = role_response['Role']['Arn']
        print_success(f"IAM role created: {kb_role_arn}")
        
        # Attach S3 access policy
        s3_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            }]
        }
        
        iam.put_role_policy(
            RoleName=kb_role_name,
            PolicyName="S3Access",
            PolicyDocument=json.dumps(s3_policy)
        )
        print_success("S3 access policy attached")
        
        # Attach Bedrock model access policy
        bedrock_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": ["bedrock:InvokeModel"],
                "Resource": f"arn:aws:bedrock:{region}::foundation-model/{embedding_model}"
            }]
        }
        
        iam.put_role_policy(
            RoleName=kb_role_name,
            PolicyName="BedrockAccess",
            PolicyDocument=json.dumps(bedrock_policy)
        )
        print_success("Bedrock access policy attached")
        
        # Wait for IAM role to propagate
        print("  Waiting for IAM role to propagate (10 seconds)...")
        time.sleep(10)
        
    except Exception as e:
        print_error(f"IAM role creation failed: {e}")
        return 1
    
    # Create OpenSearch Serverless collection
    print_step(4, "Creating OpenSearch Serverless collection")
    try:
        collection_name = f"meetingmind-vectors-{timestamp}"
        
        # Create encryption policy
        aoss.create_security_policy(
            name=f"{collection_name}-encryption",
            type='encryption',
            policy=json.dumps({
                "Rules": [{
                    "ResourceType": "collection",
                    "Resource": [f"collection/{collection_name}"]
                }],
                "AWSOwnedKey": True
            })
        )
        print_success("Encryption policy created")
        
        # Create network policy
        aoss.create_security_policy(
            name=f"{collection_name}-network",
            type='network',
            policy=json.dumps([{
                "Rules": [
                    {"ResourceType": "collection", "Resource": [f"collection/{collection_name}"]},
                    {"ResourceType": "dashboard", "Resource": [f"collection/{collection_name}"]}
                ],
                "AllowFromPublic": True
            }])
        )
        print_success("Network policy created")
        
        # Create data access policy
        aoss.create_access_policy(
            name=f"{collection_name}-access",
            type='data',
            policy=json.dumps([{
                "Rules": [
                    {
                        "ResourceType": "collection",
                        "Resource": [f"collection/{collection_name}"],
                        "Permission": [
                            "aoss:CreateCollectionItems",
                            "aoss:DeleteCollectionItems",
                            "aoss:UpdateCollectionItems",
                            "aoss:DescribeCollectionItems"
                        ]
                    },
                    {
                        "ResourceType": "index",
                        "Resource": [f"index/{collection_name}/*"],
                        "Permission": [
                            "aoss:CreateIndex", "aoss:DeleteIndex",
                            "aoss:UpdateIndex", "aoss:DescribeIndex",
                            "aoss:ReadDocument", "aoss:WriteDocument"
                        ]
                    }
                ],
                "Principal": [user_arn, kb_role_arn]
            }])
        )
        print_success("Data access policy created")
        
        # Create collection
        collection_response = aoss.create_collection(
            name=collection_name,
            type='VECTORSEARCH'
        )
        collection_id = collection_response['createCollectionDetail']['id']
        print_success(f"OpenSearch collection created: {collection_id}")
        print("  Waiting for collection to become active (this may take 2-3 minutes)...")
        
        # Wait for collection to be active
        while True:
            response = aoss.batch_get_collection(ids=[collection_id])
            status = response['collectionDetails'][0]['status']
            
            if status == 'ACTIVE':
                collection_endpoint = response['collectionDetails'][0]['collectionEndpoint']
                break
            
            print(f"  Status: {status} (waiting...)")
            time.sleep(15)
        
        print_success(f"Collection is active: {collection_endpoint}")
        
    except Exception as e:
        print_error(f"OpenSearch collection creation failed: {e}")
        return 1
    
    # Create Bedrock Knowledge Base
    print_step(5, "Creating Bedrock Knowledge Base")
    try:
        kb_response = bedrock_agent.create_knowledge_base(
            name=kb_name,
            roleArn=kb_role_arn,
            knowledgeBaseConfiguration={
                'type': 'VECTOR',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': f"arn:aws:bedrock:{region}::foundation-model/{embedding_model}"
                }
            },
            storageConfiguration={
                'type': 'OPENSEARCH_SERVERLESS',
                'opensearchServerlessConfiguration': {
                    'collectionArn': f"arn:aws:aoss:{region}:{account_id}:collection/{collection_id}",
                    'vectorIndexName': 'meetingmind-index',
                    'fieldMapping': {
                        'vectorField': 'embedding',
                        'textField': 'text',
                        'metadataField': 'metadata'
                    }
                }
            }
        )
        
        kb_id = kb_response['knowledgeBase']['knowledgeBaseId']
        print_success(f"Knowledge Base created: {kb_id}")
        
    except Exception as e:
        print_error(f"Knowledge Base creation failed: {e}")
        return 1
    
    # Create Data Source
    print_step(6, "Creating S3 Data Source")
    try:
        ds_response = bedrock_agent.create_data_source(
            knowledgeBaseId=kb_id,
            name="S3-MeetingRecordings",
            dataSourceConfiguration={
                'type': 'S3',
                's3Configuration': {
                    'bucketArn': f"arn:aws:s3:::{bucket_name}"
                }
            }
        )
        
        data_source_id = ds_response['dataSource']['dataSourceId']
        print_success(f"Data Source created: {data_source_id}")
        
    except Exception as e:
        print_error(f"Data Source creation failed: {e}")
        return 1
    
    # Create IAM role for Bedrock Agent
    print_step(7, "Creating IAM role for Bedrock Agent")
    try:
        agent_role_name = f"MeetingMind-Agent-Role-{timestamp}"
        
        agent_trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {"aws:SourceAccount": account_id},
                    "ArnLike": {"aws:SourceArn": f"arn:aws:bedrock:{region}:{account_id}:agent/*"}
                }
            }]
        }
        
        agent_role_response = iam.create_role(
            RoleName=agent_role_name,
            AssumeRolePolicyDocument=json.dumps(agent_trust_policy)
        )
        agent_role_arn = agent_role_response['Role']['Arn']
        print_success(f"Agent IAM role created: {agent_role_arn}")
        
        # Attach policies
        agent_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["bedrock:InvokeModel"],
                    "Resource": f"arn:aws:bedrock:{region}::foundation-model/{chat_model}"
                },
                {
                    "Effect": "Allow",
                    "Action": ["bedrock:Retrieve"],
                    "Resource": f"arn:aws:bedrock:{region}:{account_id}:knowledge-base/{kb_id}"
                }
            ]
        }
        
        iam.put_role_policy(
            RoleName=agent_role_name,
            PolicyName="BedrockAgentAccess",
            PolicyDocument=json.dumps(agent_policy)
        )
        print_success("Agent policies attached")
        
        print("  Waiting for agent IAM role to propagate (10 seconds)...")
        time.sleep(10)
        
    except Exception as e:
        print_error(f"Agent IAM role creation failed: {e}")
        return 1
    
    # Create Bedrock Agent
    print_step(8, "Creating Bedrock Agent")
    try:
        agent_instruction = (
            "You are MeetingMind, an AI assistant that answers questions about meeting recordings. "
            "Your knowledge comes from both spoken content (what was said) and visual content (what was shown on screen). "
            "Always cite the meeting name, date, and timestamp when answering. "
            "If information came from screen content, indicate it with [SCREEN]. "
            "If from spoken content, indicate with [SPOKEN]."
        )
        
        agent_response = bedrock_agent.create_agent(
            agentName=agent_name,
            agentResourceRoleArn=agent_role_arn,
            foundationModel=chat_model,
            instruction=agent_instruction
        )
        
        agent_id = agent_response['agent']['agentId']
        print_success(f"Agent created: {agent_id}")
        
    except Exception as e:
        print_error(f"Agent creation failed: {e}")
        return 1
    
    # Associate Knowledge Base with Agent
    print_step(9, "Associating Knowledge Base with Agent")
    try:
        bedrock_agent.associate_agent_knowledge_base(
            agentId=agent_id,
            agentVersion='DRAFT',
            knowledgeBaseId=kb_id,
            description="MeetingMind Knowledge Base",
            knowledgeBaseState='ENABLED'
        )
        print_success("Knowledge Base associated with Agent")
        
    except Exception as e:
        print_error(f"Knowledge Base association failed: {e}")
        return 1
    
    # Prepare Agent
    print_step(10, "Preparing Agent")
    try:
        bedrock_agent.prepare_agent(agentId=agent_id)
        print_success("Agent prepared")
        
    except Exception as e:
        print_error(f"Agent preparation failed: {e}")
        return 1
    
    # Create Agent Alias
    print_step(11, "Creating Agent Alias")
    try:
        alias_response = bedrock_agent.create_agent_alias(
            agentId=agent_id,
            agentAliasName="production"
        )
        agent_alias_id = alias_response['agentAlias']['agentAliasId']
        print_success(f"Agent alias created: {agent_alias_id}")
        
    except Exception as e:
        print_error(f"Agent alias creation failed: {e}")
        return 1
    
    # Update .env file
    print_step(12, "Updating .env file")
    try:
        # Read current .env
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Update values
        updated_lines = []
        for line in lines:
            if line.startswith('S3_BUCKET_NAME='):
                updated_lines.append(f'S3_BUCKET_NAME={bucket_name}\n')
            elif line.startswith('BEDROCK_KB_ID='):
                updated_lines.append(f'BEDROCK_KB_ID={kb_id}\n')
            elif line.startswith('BEDROCK_DATA_SOURCE_ID='):
                updated_lines.append(f'BEDROCK_DATA_SOURCE_ID={data_source_id}\n')
            elif line.startswith('BEDROCK_AGENT_ID='):
                updated_lines.append(f'BEDROCK_AGENT_ID={agent_id}\n')
            else:
                updated_lines.append(line)
        
        # Write back
        with open('.env', 'w') as f:
            f.writelines(updated_lines)
        
        print_success(".env file updated")
        
    except Exception as e:
        print_error(f".env update failed: {e}")
        return 1
    
    # Summary
    print()
    print("=" * 60)
    print("✅ AWS Setup Complete!")
    print("=" * 60)
    print()
    print("Resources Created:")
    print(f"  S3 Bucket:        {bucket_name}")
    print(f"  Knowledge Base:   {kb_id}")
    print(f"  Data Source:      {data_source_id}")
    print(f"  Agent:            {agent_id}")
    print(f"  Agent Alias:      {agent_alias_id}")
    print()
    print("Configuration saved to .env file")
    print()
    print("Next Steps:")
    print("  1. Install ffmpeg: brew install ffmpeg")
    print("  2. Start ingestion: python3 ingest.py")
    print("  3. Drop recording: cp your_meeting.mp4 recordings/")
    print("  4. Ask questions: python3 chat.py")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
