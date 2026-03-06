# MeetingMind Web UI

A Streamlit-based web interface for MeetingMind.

## Features

- 📤 Upload meeting recordings (.mp4)
- ⚙️ Real-time processing with progress tracking
- 📹 Video library with all processed meetings
- 💬 Interactive chat interface powered by AWS Bedrock
- 🎯 Clean, modern UI

## Installation

```bash
cd MeetingMind/frontend
pip3 install -r requirements.txt
```

## Running the Web UI

```bash
cd MeetingMind/frontend
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. **Upload a Video**: Click "Choose a meeting recording" and select an .mp4 file
2. **Process**: Click "Process Video" to start the ingestion pipeline
3. **Wait**: Processing takes 1-3 minutes depending on video length
4. **Chat**: Once complete, select the video from the sidebar and start asking questions!

## Architecture

```
frontend/
├── app.py                    # Main Streamlit app
├── components/               # UI components
│   ├── sidebar.py           # Video list
│   ├── upload.py            # Upload & processing
│   └── chat_interface.py    # Chat UI
└── api/                     # Backend wrappers
    ├── ingestion_api.py     # Wraps ingestion logic
    └── chat_api.py          # Wraps chat logic
```

## Notes

- The web UI uses the same backend as the CLI tools (`ingest.py` and `chat.py`)
- All existing CLI functionality remains unchanged
- Videos are saved to the same `recordings/` folder
- Uses the same `.env` configuration

## Troubleshooting

**"Module not found" errors:**
- Make sure you're running from the `frontend/` directory
- The app automatically adds the parent directory to Python path

**AWS credential errors:**
- Check that your `.env` file has valid credentials
- Restart the app after updating credentials

**Processing stuck:**
- Check the terminal for error messages
- Verify ffmpeg is installed: `ffmpeg -version`
- Ensure AWS services are accessible
