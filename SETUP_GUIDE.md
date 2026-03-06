# MeetingMind Setup Guide

## ✅ What's Already Done

1. ✓ All Python code implemented
2. ✓ Dependencies installed
3. ✓ AWS credentials configured in .env
4. ✓ Project structure created
5. ✓ recordings/ folder ready for your .mp4 files

## ⚠️ What You Need To Do

### 1. Install ffmpeg (REQUIRED)

```bash
brew install ffmpeg
```

Verify:
```bash
ffmpeg -version
```

### 2. Create AWS Resources

You need to create these in AWS Console:

#### A. Create S3 Bucket
```bash
aws s3 mb s3://meetingmind-akshay --region us-west-2
```

#### B. Create Bedrock Knowledge Base
1. Go to: https://console.aws.amazon.com/bedrock/home?region=us-west-2#/knowledge-bases
2. Click "Create knowledge base"
3. Settings:
   - Name: `MeetingMind-KB`
   - Data source: S3 bucket `s3://meetingmind-akshay`
   - Embedding model: `Titan Embeddings G1 - Text`
   - Vector store: Create new OpenSearch Serverless collection
4. Copy the **Knowledge Base ID** and **Data Source ID**

#### C. Create Bedrock Agent
1. Go to: https://console.aws.amazon.com/bedrock/home?region=us-west-2#/agents
2. Click "Create agent"
3. Settings:
   - Name: `MeetingMind-Agent`
   - Model: `Llama 3.3 70B Instruct`
   - Instructions: 
     ```
     You are MeetingMind, an AI assistant that answers questions about meeting recordings. 
     Your knowledge comes from both spoken content (what was said) and visual content (what was shown on screen). 
     Always cite the meeting name, date, and timestamp when answering.
     ```
4. Add Knowledge Base: Select the KB you created above
5. Copy the **Agent ID**

### 3. Update .env File

Edit `MeetingMind/.env` and add your AWS resource IDs:

```bash
# Add these lines (replace with your actual IDs):
S3_BUCKET_NAME=meetingmind-akshay
BEDROCK_KB_ID=YOUR_KB_ID_HERE
BEDROCK_DATA_SOURCE_ID=YOUR_DATA_SOURCE_ID_HERE
BEDROCK_AGENT_ID=YOUR_AGENT_ID_HERE
```

## 🚀 How To Use

### Step 1: Start Ingestion Service

Open Terminal 1:
```bash
cd MeetingMind
python3 ingest.py
```

You should see:
```
============================================================
MeetingMind Ingestion Service
============================================================

Initializing AWS clients...
✓ AWS clients initialized

Step 1: Scanning for unprocessed recordings...
Scanning recordings/ for recordings...
Found 0 video files
0 files need processing
Batch processing complete: 0/0 succeeded

Step 2: Starting file watcher...
Watching recordings/ for new recordings...
Press Ctrl+C to stop
```

### Step 2: Drop Your Meeting Recording

Open Terminal 2:
```bash
cd MeetingMind
cp ~/Downloads/your_meeting.mp4 recordings/
```

Watch Terminal 1 - it will automatically:
1. Extract audio → Transcribe with Whisper
2. Extract keyframes → Deduplicate → Detect screen-share
3. Describe frames with Claude Vision
4. Merge transcript + descriptions
5. Upload to S3
6. Sync Knowledge Base

### Step 3: Ask Questions

After processing completes, open Terminal 3:
```bash
cd MeetingMind
python3 chat.py
```

Example:
```
You: What were the main topics discussed?
Assistant: The meeting covered three main topics: Q4 revenue projections, 
new product launch timeline, and team hiring plans...

Sources:
  [1] meeting_20240305_143022_my_meeti at 05:32 (SPOKEN)
  [2] meeting_20240305_143022_my_meeti at 15:45 (SCREEN)
```

## 🐛 Troubleshooting

### "ffmpeg: command not found"
```bash
brew install ffmpeg
```

### "Configuration error: Missing required configuration"
- Make sure you've updated `.env` with your AWS resource IDs
- Check that S3 bucket, KB, and Agent are created

### "Bedrock Agent call failed"
- Verify Agent ID is correct in `.env`
- Make sure Agent has the Knowledge Base attached
- Check AWS credentials are valid (session token may expire)

### Processing is slow
- Using `WHISPER_MODEL_SIZE=tiny` (fastest, less accurate)
- To improve accuracy: change to `medium` in `.env` (slower)

## 📊 What Gets Created

```
MeetingMind/
├── recordings/              # Drop .mp4 files here
├── data/
│   ├── manifest.json       # Tracks processed files
│   ├── audio/              # Temp audio files (auto-deleted)
│   ├── frames/             # Temp keyframes (auto-deleted)
│   └── transcripts/        # (not used in current version)
└── backend/                # All Python code
```

## 🎯 Next Steps

1. Install ffmpeg
2. Create AWS resources (S3, KB, Agent)
3. Update .env with resource IDs
4. Drop a test meeting recording
5. Watch it process
6. Ask questions!

Need help? Check the main README.md for more details.
