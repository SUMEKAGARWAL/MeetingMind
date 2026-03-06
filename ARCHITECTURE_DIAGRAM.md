# MeetingMind Financial AI - Architecture Diagram

## System Architecture Flow

```mermaid
flowchart TB
    subgraph Users["👩‍💼 Women in Finance Professionals"]
        U[User Interface]
    end
    
    subgraph Frontend["🖥️ Frontend - Streamlit Web UI"]
        UI[Streamlit App<br/>Upload & Chat Interface]
    end
    
    subgraph Backend["⚙️ Backend Processing Pipeline"]
        subgraph VideoProc["📹 Video Processing"]
            VP[Video Pipeline<br/>FFmpeg]
            AE[Audio Extraction<br/>Whisper Transcription]
            FE[Frame Extraction<br/>Keyframes Every 20s]
        end
        
        subgraph AIProc["🤖 AI Processing"]
            VA[AWS Bedrock<br/>Nova Pro Vision<br/>Frame Description]
        end
        
        subgraph DataProc["📊 Data Processing"]
            MG[Content Merger<br/>Audio + Visual]
            MF[Manifest Manager<br/>Track Recordings]
        end
    end
    
    subgraph AWS["☁️ AWS Cloud Services"]
        S3[(S3 Bucket<br/>meetingmind-s3<br/>JSON Documents)]
        KB[Bedrock Knowledge Base<br/>Vector Search & RAG]
        AG[Bedrock Agent<br/>Q&A Assistant]
    end
    
    U -->|Upload .mp4<br/>Financial Meeting| UI
    UI -->|Process Video| VP
    
    VP -->|Extract Audio| AE
    VP -->|Extract Frames| FE
    
    AE -->|Transcript| MG
    FE -->|Frames| VA
    VA -->|Visual Descriptions| MG
    
    MG -->|Unified JSON<br/>Document| S3
    MG -->|Update Status| MF
    
    S3 -->|Sync Data| KB
    KB -->|RAG Context| AG
    
    UI -->|User Query| AG
    AG -->|AI Response| UI
    UI -->|Financial Insights| U
    
    style Users fill:#e1f5ff
    style Frontend fill:#fff4e6
    style Backend fill:#f3e5f5
    style AWS fill:#fff9c4
    style VideoProc fill:#e8f5e9
    style AIProc fill:#fce4ec
    style DataProc fill:#e0f2f1
```

## Key Components

### 1. **Frontend (Streamlit Web UI)**
- 📤 Video upload interface
- 💬 Chat interface for Q&A
- 📈 Financial meeting records sidebar
- 👩‍💼 Professional women-focused design

### 2. **Backend Processing Pipeline**

#### Video Processing
- **FFmpeg**: Extract audio and video frames
- **Whisper (tiny model)**: Fast audio transcription
- **Frame Extraction**: Keyframes every 20 seconds
- **Deduplication**: Remove similar frames using perceptual hashing

#### AI Processing
- **AWS Bedrock Nova Pro**: Vision AI for describing financial charts, presentations, and visual content

#### Data Processing
- **Content Merger**: Combines audio transcripts with visual descriptions
- **Manifest Manager**: Tracks processed recordings and metadata

### 3. **AWS Cloud Services**

#### S3 Storage
- Stores unified JSON documents
- Contains merged audio + visual content
- Bucket: `meetingmind-s3`

#### Bedrock Knowledge Base
- Vector search and indexing
- RAG (Retrieval Augmented Generation)
- Enables semantic search across meetings

#### Bedrock Agent
- Conversational AI assistant
- Answers questions about financial meetings
- Provides insights and summaries

## Data Flow

1. **Upload**: User uploads .mp4 financial meeting recording
2. **Process**: Backend extracts audio (Whisper) and frames (FFmpeg)
3. **Analyze**: AWS Bedrock Nova Pro describes visual content
4. **Merge**: Combine audio transcript + visual descriptions
5. **Store**: Upload unified JSON to S3
6. **Index**: Sync with Bedrock Knowledge Base
7. **Query**: User asks questions via chat interface
8. **Respond**: Bedrock Agent retrieves context and generates answers

## Technology Stack

- **Frontend**: Streamlit (Python)
- **Backend**: Python 3.11+
- **Video Processing**: FFmpeg, OpenCV
- **Audio Transcription**: OpenAI Whisper
- **AI/ML**: AWS Bedrock (Nova Pro, Knowledge Base, Agent)
- **Storage**: AWS S3
- **Region**: us-west-2

## Use Cases

- 📈 Quarterly Earnings Call Analysis
- 🏦 Board Meeting Summaries
- 💰 Investor Presentation Insights
- 📊 Financial Planning Review
- 🎯 Budget & Strategy Meeting Q&A

---

**Built for**: Women in Financial AI - AWS Cloud Women Agentic AI Hackathon 🏆
