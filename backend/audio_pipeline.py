"""
Audio extraction and transcription pipeline.
"""
import os
import subprocess
from faster_whisper import WhisperModel
from backend.models import AudioTranscript, TranscriptSegment


def extract_audio(video_path: str, output_path: str) -> str:
    """
    Extract audio from video file using ffmpeg.
    
    Args:
        video_path: Path to input video file
        output_path: Path for output audio file (.wav)
        
    Returns:
        Path to extracted audio file, or None if video has no audio
        
    Raises:
        Exception if ffmpeg fails for reasons other than missing audio
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # First, check if video has audio stream
    probe_cmd = [
        "ffmpeg",
        "-i", video_path,
        "-hide_banner"
    ]
    
    probe_result = subprocess.run(
        probe_cmd,
        capture_output=True,
        text=True
    )
    
    # Check if there's an audio stream
    if "Audio:" not in probe_result.stderr:
        print(f"   ⚠️  Video has no audio stream - skipping audio extraction")
        return None
    
    # ffmpeg command: extract audio as 16kHz mono WAV
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-ar", "16000",  # 16kHz sample rate
        "-ac", "1",      # mono
        "-f", "wav",     # WAV format
        "-y",            # overwrite output file
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return output_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"ffmpeg audio extraction failed: {e.stderr}")


def transcribe_audio(audio_path: str, model_size: str = "tiny") -> AudioTranscript:
    """
    Transcribe audio using faster-whisper.
    
    Args:
        audio_path: Path to audio file
        model_size: Whisper model size (tiny, base, small, medium, large)
        
    Returns:
        AudioTranscript with timestamped segments
    """
    print(f"   Loading Whisper model ({model_size})...")
    
    # Initialize Whisper model
    # device="cpu" for compatibility, compute_type="int8" for speed
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    print(f"   Transcribing audio...")
    
    # Transcribe
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        language=None,  # auto-detect
        vad_filter=True  # voice activity detection
    )
    
    # Convert segments to our model
    transcript_segments = []
    for segment in segments:
        transcript_segments.append(
            TranscriptSegment(
                start=segment.start,
                end=segment.end,
                text=segment.text.strip()
            )
        )
    
    # Get audio duration from last segment
    duration = transcript_segments[-1].end if transcript_segments else 0.0
    
    return AudioTranscript(
        segments=transcript_segments,
        language=info.language,
        duration=duration
    )
