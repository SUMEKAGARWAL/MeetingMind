"""
Manifest management for tracking processed recordings.
"""
import json
import os
from datetime import datetime
from typing import Optional
from backend.models import Manifest, ProcessedRecording


def load_manifest(manifest_path: str) -> Manifest:
    """
    Load processing manifest from disk.
    
    Args:
        manifest_path: Path to manifest.json file
        
    Returns:
        Manifest object (empty if file doesn't exist)
    """
    if not os.path.exists(manifest_path):
        return Manifest(recordings=[], last_updated=datetime.now())
    
    try:
        with open(manifest_path, 'r') as f:
            data = json.load(f)
            return Manifest(**data)
    except Exception as e:
        print(f"⚠️  Warning: Failed to load manifest: {e}")
        print("   Creating new empty manifest")
        return Manifest(recordings=[], last_updated=datetime.now())


def is_already_processed(filename: str, manifest: Manifest) -> bool:
    """
    Check if a recording has already been processed.
    
    Args:
        filename: Name of the video file
        manifest: Current manifest
        
    Returns:
        True if file is in manifest, False otherwise
    """
    return any(r.filename == filename for r in manifest.recordings)


def update_manifest(manifest_path: str, recording: ProcessedRecording) -> None:
    """
    Add processed recording to manifest and save atomically.
    
    Args:
        manifest_path: Path to manifest.json file
        recording: ProcessedRecording to add
    """
    # Load current manifest
    manifest = load_manifest(manifest_path)
    
    # Add new recording
    manifest.recordings.append(recording)
    manifest.last_updated = datetime.now()
    
    # Atomic write: write to temp file, then rename
    temp_path = manifest_path + ".tmp"
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
        
        # Write to temp file
        with open(temp_path, 'w') as f:
            json.dump(manifest.model_dump(), f, indent=2, default=str)
        
        # Atomic rename
        os.replace(temp_path, manifest_path)
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise Exception(f"Failed to update manifest: {e}")


def get_manifest_summary(manifest_path: str) -> dict:
    """
    Get summary statistics from manifest.
    
    Args:
        manifest_path: Path to manifest.json file
        
    Returns:
        Dictionary with summary stats
    """
    manifest = load_manifest(manifest_path)
    
    return {
        "total_recordings": len(manifest.recordings),
        "last_updated": manifest.last_updated,
        "recordings": [
            {
                "meeting_id": r.meeting_id,
                "filename": r.filename,
                "processed_at": r.processed_at,
                "duration": r.duration
            }
            for r in manifest.recordings
        ]
    }
