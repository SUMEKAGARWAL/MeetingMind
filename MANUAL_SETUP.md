# Manual AWS Setup (10 Minutes)

Since your AWS credentials expired, here's the easiest way to set up via AWS Console:

## Step 1: Create S3 Bucket (2 minutes)

1. Go to: https://s3.console.aws.amazon.com/s3/home?region=us-west-2
2. Click **"Create bucket"**
3. Settings:
   - Bucket name: `meetingmind-akshay` (or any unique name)
   - Region: **us-west-2**
   - Keep all other defaults
4. Click **"Create bucket"**
5. ✅ **Copy the bucket name** → You'll need this for .env

---

## Step 2: Create Knowledge Base (5 minutes)

1. Go to: https://console.aws.amazon.com/bedrock/home?region=us-west-2#/knowledge-bases
2. Click **"Create knowledge base"**

### Page 1: Provide knowledge base details
- Name: `MeetingMind-KB`
- Description: `Meeting recordings knowledge base`
- Click **"Next"**

### Page 2: Set up data source
- Data source name: `MeetingRecordings`
- S3 URI: Click **"Browse S3"** → Select your bucket from Step 1
- Click **"Next"**

### Page 3: Select embeddings model
- Embeddings model: **Titan Embeddings G1 - Text**
- Vector database: **"Quick create a new vector store"**
- Click **"Next"**

### Page 4: Review and create
- Click **"Create knowledge base"**
- Wait ~2 minutes for creation

### Get IDs:
1. After creation, you'll see the Knowledge Base details page
2. ✅ **Copy the Knowledge Base ID** (top of page, looks like: `ABCDEFGHIJ`)
3. Click **"Data sources"** tab
4. ✅ **Copy the Data Source ID** (looks like: `KLMNOPQRST`)

---

## Step 3: Create Bedrock Agent (3 minutes)

1. Go to: https://console.aws.amazon.com/bedrock/home?region=us-west-2#/agents
2. Click **"Create agent"**

### Page 1: Provide agent details
- Agent name: `MeetingMind-Agent`
- Description: `Meeting intelligence assistant`
- User input: **Enable**
- Click **"Next"**

### Page 2: Select model
- Model: **Llama 3.3 70B Instruct**
- Instructions (paste this):
  ```
  You are MeetingMind, an AI assistant that answers questions about meeting recordings. 
  Your knowledge comes from both spoken content (what was said) and visual content 
  (what was shown on screen). Always cite the meeting name, date, and timestamp when answering.
  ```
- Click **"Next"**

### Page 3: Add action groups
- Skip this (click **"Next"**)

### Page 4: Add knowledge bases
- Click **"Add"**
- Select **MeetingMind-KB** (the one you created in Step 2)
- Click **"Add"**
- Click **"Next"**

### Page 5: Review and create
- Click **"Create agent"**
- Wait ~1 minute

### Get Agent ID:
1. After creation, you'll see the Agent details page
2. ✅ **Copy the Agent ID** (top of page, looks like: `UVWXYZ1234`)

---

## Step 4: Update .env File

Open `MeetingMind/.env` in a text editor and update these 4 lines:

```bash
S3_BUCKET_NAME=meetingmind-akshay
BEDROCK_KB_ID=ABCDEFGHIJ
BEDROCK_DATA_SOURCE_ID=KLMNOPQRST
BEDROCK_AGENT_ID=UVWXYZ1234
```

Replace with your actual IDs from the steps above.

---

## Step 5: Install ffmpeg

```bash
brew install ffmpeg
```

---

## Step 6: Start Using MeetingMind!

```bash
cd MeetingMind

# Terminal 1: Start ingestion service
python3 ingest.py

# Terminal 2: Drop your recording
cp ~/Downloads/your_meeting.mp4 recordings/

# Terminal 3: Ask questions (after processing completes)
python3 chat.py
```

---

## Troubleshooting

### "InvalidClientTokenId" error
Your AWS session token expired. You have two options:
1. **Get fresh credentials** from your AWS SSO portal
2. **Use permanent credentials** (create access keys in IAM)

### Can't access AWS Console
Contact your AWS administrator for access to:
- S3
- Bedrock (Knowledge Bases and Agents)
- IAM (for creating roles)

### Need help?
Check `get_credentials.md` for detailed credential options.
