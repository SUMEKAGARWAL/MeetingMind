# Getting Fresh AWS Credentials

Your AWS session token has expired. Here's how to get new credentials:

## Option 1: AWS SSO / IAM Identity Center (Recommended)

If your organization uses AWS SSO:

1. Go to your AWS SSO portal (ask your admin for the URL)
2. Click on your AWS account
3. Click "Command line or programmatic access"
4. Copy the credentials shown
5. Paste them into your `.env` file

## Option 2: AWS Console (Temporary Credentials)

1. Go to: https://console.aws.amazon.com/
2. Log in to your account
3. Click your username (top right) → Security credentials
4. Scroll to "Access keys" section
5. Click "Create access key"
6. Choose "Command Line Interface (CLI)"
7. Copy the Access Key ID and Secret Access Key
8. Update your `.env` file (remove AWS_SESSION_TOKEN line if using permanent keys)

## Option 3: Use AWS CloudShell (Easiest!)

If you have AWS Console access, you can use CloudShell to create resources:

1. Go to: https://console.aws.amazon.com/
2. Click the CloudShell icon (>_) in the top navigation bar
3. Wait for CloudShell to start
4. Run these commands:

```bash
# Install git
sudo yum install -y git

# Clone or upload the setup script
# (You'll need to copy the setup_aws.sh content)

# Or manually create resources:

# 1. Create S3 bucket
BUCKET_NAME="meetingmind-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region us-west-2
echo "S3_BUCKET_NAME=$BUCKET_NAME"

# 2. Create Knowledge Base (via Console is easier)
# Go to: https://console.aws.amazon.com/bedrock/home?region=us-west-2#/knowledge-bases
# Click "Create knowledge base"
# Follow the wizard

# 3. Create Agent (via Console)
# Go to: https://console.aws.amazon.com/bedrock/home?region=us-west-2#/agents
# Click "Create agent"
# Follow the wizard
```

## Option 4: Manual Setup via AWS Console (Simplest!)

Since AWS CLI isn't installed and credentials expired, the easiest way is:

### Step 1: Create S3 Bucket
1. Go to: https://s3.console.aws.amazon.com/s3/home?region=us-west-2
2. Click "Create bucket"
3. Name: `meetingmind-YOUR_NAME` (must be globally unique)
4. Region: `us-west-2`
5. Keep defaults, click "Create bucket"
6. **Copy the bucket name**

### Step 2: Create Knowledge Base
1. Go to: https://console.aws.amazon.com/bedrock/home?region=us-west-2#/knowledge-bases
2. Click "Create knowledge base"
3. Name: `MeetingMind-KB`
4. Click "Next"
5. Data source:
   - Type: S3
   - Browse and select your bucket from Step 1
   - Click "Next"
6. Embeddings model: `Titan Embeddings G1 - Text`
7. Vector database: "Quick create a new vector store"
8. Click "Next" → "Create"
9. **Copy the Knowledge Base ID** (looks like: `ABCDEFGHIJ`)
10. Click on "Data sources" tab
11. **Copy the Data Source ID** (looks like: `KLMNOPQRST`)

### Step 3: Create Agent
1. Go to: https://console.aws.amazon.com/bedrock/home?region=us-west-2#/agents
2. Click "Create agent"
3. Name: `MeetingMind-Agent`
4. Instructions:
   ```
   You are MeetingMind, an AI assistant that answers questions about meeting recordings. 
   Your knowledge comes from both spoken content (what was said) and visual content 
   (what was shown on screen). Always cite the meeting name, date, and timestamp when answering.
   ```
5. Model: `Llama 3.3 70B Instruct`
6. Click "Next"
7. Add Knowledge Base:
   - Click "Add"
   - Select the Knowledge Base you created in Step 2
   - Click "Add"
8. Click "Next" → "Create"
9. **Copy the Agent ID** (looks like: `UVWXYZ1234`)

### Step 4: Update .env File

Edit `MeetingMind/.env` and update these lines:

```bash
S3_BUCKET_NAME=meetingmind-YOUR_NAME
BEDROCK_KB_ID=ABCDEFGHIJ
BEDROCK_DATA_SOURCE_ID=KLMNOPQRST
BEDROCK_AGENT_ID=UVWXYZ1234
```

### Step 5: You're Done!

Now you can run:
```bash
cd MeetingMind
python3 ingest.py
```

---

## Which Option Should I Choose?

- **Have AWS Console access?** → Use Option 4 (Manual via Console) - Takes 10 minutes
- **Have AWS SSO?** → Use Option 1 - Get fresh credentials
- **Need permanent keys?** → Use Option 2 - Create access keys
- **Want to use CLI?** → Use Option 3 (CloudShell)

The manual console approach (Option 4) is the fastest and doesn't require AWS CLI or fresh credentials!
