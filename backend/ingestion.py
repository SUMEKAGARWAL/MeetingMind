"""
Main ingestion orchestrator - coordinates the complete processing pipeline.
"""
import os
import hashlib
from datetime import datetime
from backend.config import config
from backend.models import ProcessedRecording
from backend.audio_pipeline import extract_audio, transcribe_audio
from backend.video_pipeline import extract_keyframes, deduplicate_frames
from backend.screenshare_detector import detect_screen_share
from backend.vision_describer import describe_all_frames
from backend.merger import merge_transcript_and_descriptions
from backend.s3_uploader import upload_to_s3
from backend.kb_sync import sync_knowledge_base
from backend.cleanup import cleanup_temp_files
from backend.manifest import update_manifest


def generate_meeting_id(filename: str) -> str:
    """Generate unique meeting ID from filename and timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Use first 8 chars of filename (without extension)
    name_part = os.path.splitext(filename)[0][:8]
    return f"meeting_{timestamp}_{name_part}"


def ingest_meeting(
    video_path: str,
    meeting_id: str,
    manifest_path: str,
    s3_client,
    bedrock_runtime_client,
    bedrock_agent_client
) -> bool:
    """
    Main ingestion pipeline orchestrator.
    
    Processes a meeting recording through the complete pipeline:
    1. Extract and transcribe audio
    2. Extract and deduplicate keyframes
    3. Detect screen-share frames
    4. Describe frames with Claude Vision
    5. Merge transcript and descriptions
    6. Upload to S3
    7. Sync Knowledge Base
    8. Update manifest
    9. Cleanup temp files
    
    Args:
        video_path: Path to .mp4 video file
        meeting_id: Unique identifier for this meeting
        manifest_path: Path to manifest.json
        s3_client: Boto3 S3 client
        bedrock_runtime_client: Boto3 Bedrock Runtime client
        bedrock_agent_client: Boto3 Bedrock Agent client
        
    Returns:
        True on success, False on failure
    """
    print(f"\n[{meeting_id}] Starting ingestion...")
    
    try:
        # Step 1: Audio Pipeline
        print(f"[{meeting_id}] Extracting audio...")
        audio_path = os.path.join(config.AUDIO_DIR, f"{meeting_id}.wav")
        audio_file = extract_audio(video_path, audio_path)
        
        # Handle videos without audio
        if audio_file is None:
            print(f"[{meeting_id}] No audio stream found - creating empty transcript")
            from backend.models import AudioTranscript
            transcript = AudioTranscript(
                segments=[],
                language="unknown",
                duration=0.0
            )
        else:
            print(f"[{meeting_id}] Transcribing audio...")
            transcript = transcribe_audio(audio_file, model_size=config.WHISPER_MODEL_SIZE)
            print(f"[{meeting_id}] Transcribed {len(transcript.segments)} segments ({transcript.language})")
        
        # Step 2: Video Pipeline
        print(f"[{meeting_id}] Extracting keyframes...")
        frames_dir = os.path.join(config.FRAMES_DIR, meeting_id)
        keyframes = extract_keyframes(
            video_path,
            frames_dir,
            interval_seconds=config.KEYFRAME_INTERVAL_SECONDS
        )
        print(f"[{meeting_id}] Extracted {len(keyframes)} keyframes")
        
        print(f"[{meeting_id}] Deduplicating frames...")
        deduplicated = deduplicate_frames(keyframes, threshold=config.PHASH_THRESHOLD)
        print(f"[{meeting_id}] Kept {deduplicated.deduplicated_count}/{deduplicated.original_count} frames after deduplication")
        
        # Step 3: Screen-Share Detection
        screenshare_frames = deduplicated.frames
        
        if config.SCREENSHARE_ENABLED:
            print(f"[{meeting_id}] Detecting screen-share...")
            screenshare_frames = []
            threshold = {
                'edge_density_min': config.SCREENSHARE_EDGE_DENSITY_MIN,
                'text_region_min': config.SCREENSHARE_TEXT_REGION_MIN
            }
            
            for frame in deduplicated.frames:
                try:
                    is_screenshare = detect_screen_share(frame.frame_path, threshold)
                    if is_screenshare:
                        screenshare_frames.append(frame)
                except Exception as e:
                    print(f"[{meeting_id}]    ⚠️  Screen-share detection failed for frame at {frame.timestamp}s: {e}")
                    # Include frame anyway if detection fails
                    screenshare_frames.append(frame)
            
            print(f"[{meeting_id}] Screen-share detection: {len(screenshare_frames)}/{len(deduplicated.frames)} frames kept")
        
        # Step 4: Vision Description
        descriptions = []
        if screenshare_frames:
            print(f"[{meeting_id}] Describing {len(screenshare_frames)} frames with Claude Vision...")
            descriptions = describe_all_frames(screenshare_frames, bedrock_runtime_client)
            print(f"[{meeting_id}] Generated {len(descriptions)} descriptions")
        else:
            print(f"[{meeting_id}] No screen-share frames to describe")
        
        # Step 5: Merge
        print(f"[{meeting_id}] Merging transcript and descriptions...")
        unified_doc = merge_transcript_and_descriptions(
            transcript,
            descriptions,
            meeting_id
        )
        print(f"[{meeting_id}] Created unified document with {len(unified_doc.segments)} segments")
        
        # Step 6: Upload to S3
        print(f"[{meeting_id}] Uploading to S3...")
        s3_uri = upload_to_s3(unified_doc, s3_client)
        print(f"[{meeting_id}] Uploaded to {s3_uri}")
        
        # Step 7: Sync Knowledge Base
        print(f"[{meeting_id}] Syncing Knowledge Base...")
        sync_success = sync_knowledge_base(bedrock_agent_client)
        
        if not sync_success:
            print(f"[{meeting_id}]    ⚠️  KB sync skipped (not configured)")
        
        # Step 8: Update Manifest
        print(f"[{meeting_id}] Updating manifest...")
        recording = ProcessedRecording(
            meeting_id=meeting_id,
            filename=os.path.basename(video_path),
            processed_at=datetime.now(),
            s3_uri=s3_uri,
            duration=transcript.duration
        )
        update_manifest(manifest_path, recording)
        
        # Step 9: Cleanup
        print(f"[{meeting_id}] Cleaning up temporary files...")
        cleanup_temp_files(audio_path, frames_dir)
        
        print(f"[{meeting_id}] ✓ Ingestion completed successfully\n")
        return True
        
    except Exception as e:
        print(f"[{meeting_id}] ✗ Ingestion failed: {str(e)}\n")
        return False
