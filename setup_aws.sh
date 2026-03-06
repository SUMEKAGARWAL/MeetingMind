#!/bin/bash
# MeetingMind AWS Setup Script
# Creates S3 bucket, Bedrock Knowledge Base, and Bedrock Agent

set -e  # Exit on error

echo "============================================================"
echo "MeetingMind AWS Setup"
echo "============================================================"
echo ""

# Configuration
REGION="us-west-2"
BUCKET_NAME="meetingmind-$(date +%s)"  # Unique bucket name with timestamp
KB_NAME="MeetingMind-KB"
AGENT_NAME="MeetingMind-Agent"
EMBEDDING_MODEL="amazon.titan-embed-text-v1"
CHAT_MODEL="meta.llama3-3-70b-instruct-v1:0"

echo "Configuration:"
echo "  Region: $REGION"
echo "  S3 Bucket: $BUCKET_NAME"
echo "  Knowledge Base: $KB_NAME"
echo "  Agent: $AGENT_NAME"
echo ""

# Check AWS CLI is configured
echo "Step 1: Checking AWS CLI configuration..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured or credentials invalid"
    echo "Please run: aws configure"
    exit 1
fi
echo "✓ AWS CLI configured"
echo ""

# Create S3 Bucket
echo "Step 2: Creating S3 bucket..."
if aws s3 mb s3://$BUCKET_NAME --region $REGION; then
    echo "✓ S3 bucket created: s3://$BUCKET_NAME"
else
    echo "⚠️  Bucket creation failed (may already exist)"
fi
echo ""

# Enable versioning on bucket
echo "Step 3: Enabling S3 versioning..."
aws s3api put-bucket-versioning \
    --bucket $BUCKET_NAME \
    --versioning-configuration Status=Enabled \
    --region $REGION
echo "✓ Versioning enabled"
echo ""

# Create IAM role for Bedrock Knowledge Base
echo "Step 4: Creating IAM role for Knowledge Base..."

# Trust policy for Bedrock
cat > /tmp/kb-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
KB_ROLE_NAME="MeetingMind-KB-Role-$(date +%s)"
KB_ROLE_ARN=$(aws iam create-role \
    --role-name $KB_ROLE_NAME \
    --assume-role-policy-document file:///tmp/kb-trust-policy.json \
    --query 'Role.Arn' \
    --output text)

echo "✓ IAM role created: $KB_ROLE_ARN"

# Attach S3 access policy
cat > /tmp/kb-s3-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::$BUCKET_NAME",
        "arn:aws:s3:::$BUCKET_NAME/*"
      ]
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name $KB_ROLE_NAME \
    --policy-name S3Access \
    --policy-document file:///tmp/kb-s3-policy.json

echo "✓ S3 access policy attached"

# Attach Bedrock model access policy
cat > /tmp/kb-bedrock-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:$REGION::foundation-model/$EMBEDDING_MODEL"
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name $KB_ROLE_NAME \
    --policy-name BedrockAccess \
    --policy-document file:///tmp/kb-bedrock-policy.json

echo "✓ Bedrock access policy attached"
echo ""

# Wait for IAM role to propagate
echo "Step 5: Waiting for IAM role to propagate (10 seconds)..."
sleep 10
echo "✓ Ready"
echo ""

# Create OpenSearch Serverless collection for vector store
echo "Step 6: Creating OpenSearch Serverless collection..."

COLLECTION_NAME="meetingmind-vectors-$(date +%s)"

# Create encryption policy
cat > /tmp/encryption-policy.json <<EOF
{
  "Rules": [
    {
      "ResourceType": "collection",
      "Resource": ["collection/$COLLECTION_NAME"]
    }
  ],
  "AWSOwnedKey": true
}
EOF

aws opensearchserverless create-security-policy \
    --name ${COLLECTION_NAME}-encryption \
    --type encryption \
    --policy file:///tmp/encryption-policy.json \
    --region $REGION > /dev/null

echo "✓ Encryption policy created"

# Create network policy
cat > /tmp/network-policy.json <<EOF
[
  {
    "Rules": [
      {
        "ResourceType": "collection",
        "Resource": ["collection/$COLLECTION_NAME"]
      },
      {
        "ResourceType": "dashboard",
        "Resource": ["collection/$COLLECTION_NAME"]
      }
    ],
    "AllowFromPublic": true
  }
]
EOF

aws opensearchserverless create-security-policy \
    --name ${COLLECTION_NAME}-network \
    --type network \
    --policy file:///tmp/network-policy.json \
    --region $REGION > /dev/null

echo "✓ Network policy created"

# Get current AWS account ID and user ARN
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
USER_ARN=$(aws sts get-caller-identity --query Arn --output text)

# Create data access policy
cat > /tmp/data-access-policy.json <<EOF
[
  {
    "Rules": [
      {
        "ResourceType": "collection",
        "Resource": ["collection/$COLLECTION_NAME"],
        "Permission": [
          "aoss:CreateCollectionItems",
          "aoss:DeleteCollectionItems",
          "aoss:UpdateCollectionItems",
          "aoss:DescribeCollectionItems"
        ]
      },
      {
        "ResourceType": "index",
        "Resource": ["index/$COLLECTION_NAME/*"],
        "Permission": [
          "aoss:CreateIndex",
          "aoss:DeleteIndex",
          "aoss:UpdateIndex",
          "aoss:DescribeIndex",
          "aoss:ReadDocument",
          "aoss:WriteDocument"
        ]
      }
    ],
    "Principal": [
      "$USER_ARN",
      "$KB_ROLE_ARN"
    ]
  }
]
EOF

aws opensearchserverless create-access-policy \
    --name ${COLLECTION_NAME}-access \
    --type data \
    --policy file:///tmp/data-access-policy.json \
    --region $REGION > /dev/null

echo "✓ Data access policy created"

# Create collection
COLLECTION_ID=$(aws opensearchserverless create-collection \
    --name $COLLECTION_NAME \
    --type VECTORSEARCH \
    --region $REGION \
    --query 'createCollectionDetail.id' \
    --output text)

echo "✓ OpenSearch collection created: $COLLECTION_ID"
echo "  Waiting for collection to become active (this may take 2-3 minutes)..."

# Wait for collection to be active
while true; do
    STATUS=$(aws opensearchserverless batch-get-collection \
        --ids $COLLECTION_ID \
        --region $REGION \
        --query 'collectionDetails[0].status' \
        --output text)
    
    if [ "$STATUS" = "ACTIVE" ]; then
        break
    fi
    echo "  Status: $STATUS (waiting...)"
    sleep 15
done

# Get collection endpoint
COLLECTION_ENDPOINT=$(aws opensearchserverless batch-get-collection \
    --ids $COLLECTION_ID \
    --region $REGION \
    --query 'collectionDetails[0].collectionEndpoint' \
    --output text)

echo "✓ Collection is active: $COLLECTION_ENDPOINT"
echo ""

# Create Bedrock Knowledge Base
echo "Step 7: Creating Bedrock Knowledge Base..."

cat > /tmp/kb-config.json <<EOF
{
  "type": "VECTOR",
  "vectorKnowledgeBaseConfiguration": {
    "embeddingModelArn": "arn:aws:bedrock:$REGION::foundation-model/$EMBEDDING_MODEL"
  }
}
EOF

cat > /tmp/storage-config.json <<EOF
{
  "type": "OPENSEARCH_SERVERLESS",
  "opensearchServerlessConfiguration": {
    "collectionArn": "arn:aws:aoss:$REGION:$ACCOUNT_ID:collection/$COLLECTION_ID",
    "vectorIndexName": "meetingmind-index",
    "fieldMapping": {
      "vectorField": "embedding",
      "textField": "text",
      "metadataField": "metadata"
    }
  }
}
EOF

KB_ID=$(aws bedrock-agent create-knowledge-base \
    --name "$KB_NAME" \
    --role-arn "$KB_ROLE_ARN" \
    --knowledge-base-configuration file:///tmp/kb-config.json \
    --storage-configuration file:///tmp/storage-config.json \
    --region $REGION \
    --query 'knowledgeBase.knowledgeBaseId' \
    --output text)

echo "✓ Knowledge Base created: $KB_ID"
echo ""

# Create Data Source
echo "Step 8: Creating S3 Data Source..."

cat > /tmp/data-source-config.json <<EOF
{
  "type": "S3",
  "s3Configuration": {
    "bucketArn": "arn:aws:s3:::$BUCKET_NAME"
  }
}
EOF

DATA_SOURCE_ID=$(aws bedrock-agent create-data-source \
    --knowledge-base-id $KB_ID \
    --name "S3-MeetingRecordings" \
    --data-source-configuration file:///tmp/data-source-config.json \
    --region $REGION \
    --query 'dataSource.dataSourceId' \
    --output text)

echo "✓ Data Source created: $DATA_SOURCE_ID"
echo ""

# Create IAM role for Bedrock Agent
echo "Step 9: Creating IAM role for Bedrock Agent..."

cat > /tmp/agent-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "$ACCOUNT_ID"
        },
        "ArnLike": {
          "aws:SourceArn": "arn:aws:bedrock:$REGION:$ACCOUNT_ID:agent/*"
        }
      }
    }
  ]
}
EOF

AGENT_ROLE_NAME="MeetingMind-Agent-Role-$(date +%s)"
AGENT_ROLE_ARN=$(aws iam create-role \
    --role-name $AGENT_ROLE_NAME \
    --assume-role-policy-document file:///tmp/agent-trust-policy.json \
    --query 'Role.Arn' \
    --output text)

echo "✓ Agent IAM role created: $AGENT_ROLE_ARN"

# Attach Bedrock model access policy for agent
cat > /tmp/agent-bedrock-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:$REGION::foundation-model/$CHAT_MODEL"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:Retrieve"
      ],
      "Resource": "arn:aws:bedrock:$REGION:$ACCOUNT_ID:knowledge-base/$KB_ID"
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name $AGENT_ROLE_NAME \
    --policy-name BedrockAgentAccess \
    --policy-document file:///tmp/agent-bedrock-policy.json

echo "✓ Agent policies attached"
echo ""

# Wait for agent role to propagate
echo "Step 10: Waiting for agent IAM role to propagate (10 seconds)..."
sleep 10
echo "✓ Ready"
echo ""

# Create Bedrock Agent
echo "Step 11: Creating Bedrock Agent..."

AGENT_INSTRUCTION="You are MeetingMind, an AI assistant that answers questions about meeting recordings. Your knowledge comes from both spoken content (what was said) and visual content (what was shown on screen). Always cite the meeting name, date, and timestamp when answering. If information came from screen content, indicate it with [SCREEN]. If from spoken content, indicate with [SPOKEN]."

AGENT_ID=$(aws bedrock-agent create-agent \
    --agent-name "$AGENT_NAME" \
    --agent-resource-role-arn "$AGENT_ROLE_ARN" \
    --foundation-model "$CHAT_MODEL" \
    --instruction "$AGENT_INSTRUCTION" \
    --region $REGION \
    --query 'agent.agentId' \
    --output text)

echo "✓ Agent created: $AGENT_ID"
echo ""

# Associate Knowledge Base with Agent
echo "Step 12: Associating Knowledge Base with Agent..."

aws bedrock-agent associate-agent-knowledge-base \
    --agent-id $AGENT_ID \
    --agent-version DRAFT \
    --knowledge-base-id $KB_ID \
    --description "MeetingMind Knowledge Base" \
    --knowledge-base-state ENABLED \
    --region $REGION > /dev/null

echo "✓ Knowledge Base associated with Agent"
echo ""

# Prepare Agent
echo "Step 13: Preparing Agent..."

aws bedrock-agent prepare-agent \
    --agent-id $AGENT_ID \
    --region $REGION > /dev/null

echo "✓ Agent prepared"
echo ""

# Create Agent Alias
echo "Step 14: Creating Agent Alias..."

AGENT_ALIAS_ID=$(aws bedrock-agent create-agent-alias \
    --agent-id $AGENT_ID \
    --agent-alias-name "production" \
    --region $REGION \
    --query 'agentAlias.agentAliasId' \
    --output text)

echo "✓ Agent alias created: $AGENT_ALIAS_ID"
echo ""

# Update .env file
echo "Step 15: Updating .env file..."

# Backup existing .env
cp .env .env.backup

# Update .env with new values
sed -i.bak "s|S3_BUCKET_NAME=.*|S3_BUCKET_NAME=$BUCKET_NAME|" .env
sed -i.bak "s|BEDROCK_KB_ID=.*|BEDROCK_KB_ID=$KB_ID|" .env
sed -i.bak "s|BEDROCK_DATA_SOURCE_ID=.*|BEDROCK_DATA_SOURCE_ID=$DATA_SOURCE_ID|" .env
sed -i.bak "s|BEDROCK_AGENT_ID=.*|BEDROCK_AGENT_ID=$AGENT_ID|" .env

rm .env.bak

echo "✓ .env file updated"
echo ""

# Cleanup temp files
rm -f /tmp/kb-trust-policy.json /tmp/kb-s3-policy.json /tmp/kb-bedrock-policy.json
rm -f /tmp/encryption-policy.json /tmp/network-policy.json /tmp/data-access-policy.json
rm -f /tmp/kb-config.json /tmp/storage-config.json /tmp/data-source-config.json
rm -f /tmp/agent-trust-policy.json /tmp/agent-bedrock-policy.json

echo "============================================================"
echo "✅ AWS Setup Complete!"
echo "============================================================"
echo ""
echo "Resources Created:"
echo "  S3 Bucket:        $BUCKET_NAME"
echo "  Knowledge Base:   $KB_ID"
echo "  Data Source:      $DATA_SOURCE_ID"
echo "  Agent:            $AGENT_ID"
echo "  Agent Alias:      $AGENT_ALIAS_ID"
echo ""
echo "Configuration saved to .env file"
echo ""
echo "Next Steps:"
echo "  1. Install ffmpeg: brew install ffmpeg"
echo "  2. Start ingestion: python3 ingest.py"
echo "  3. Drop recording: cp your_meeting.mp4 recordings/"
echo "  4. Ask questions: python3 chat.py"
echo ""
