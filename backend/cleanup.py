"""
Temporary file cleanup.
"""
import os
import shutil


def cleanup_temp_files(audio_path: str, frames_dir: str) -> None:
    """
    Clean up temporary files after processing.
    
    Args:
        audio_path: Path to extracted audio file
        frames_dir: Directory containing extracted frames
    """
    # Delete audio file
    try:
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except Exception as e:
        print(f"   ⚠️  Warning: Failed to delete audio file: {e}")
    
    # Delete frames directory
    try:
        if os.path.exists(frames_dir):
            shutil.rmtree(frames_dir)
    except Exception as e:
        print(f"   ⚠️  Warning: Failed to delete frames directory: {e}")
