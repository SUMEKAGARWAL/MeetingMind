"""
Video keyframe extraction and deduplication pipeline.
"""
import os
import subprocess
from typing import List
from PIL import Image
import imagehash
from backend.models import Keyframe, DeduplicatedFrames


def extract_keyframes(
    video_path: str,
    output_dir: str,
    interval_seconds: int = 20
) -> List[Keyframe]:
    """
    Extract keyframes from video at regular intervals.
    
    Args:
        video_path: Path to input video file
        output_dir: Directory for output frame images
        interval_seconds: Interval between frames in seconds
        
    Returns:
        List of Keyframe objects
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # ffmpeg command: extract 1 frame every N seconds
    # fps=1/N means 1 frame per N seconds
    output_pattern = os.path.join(output_dir, "frame_%04d.jpg")
    
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"fps=1/{interval_seconds}",  # 1 frame per interval
        "-q:v", "2",  # high quality
        "-s", "1280x720",  # 720p resolution
        "-y",  # overwrite
        output_pattern
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"ffmpeg keyframe extraction failed: {e.stderr}")
    
    # Collect extracted frames
    keyframes = []
    frame_files = sorted([f for f in os.listdir(output_dir) if f.startswith("frame_") and f.endswith(".jpg")])
    
    for idx, filename in enumerate(frame_files):
        frame_path = os.path.join(output_dir, filename)
        timestamp = idx * interval_seconds
        
        # Compute perceptual hash
        img = Image.open(frame_path)
        phash = str(imagehash.phash(img))
        
        keyframes.append(
            Keyframe(
                timestamp=float(timestamp),
                frame_path=frame_path,
                phash=phash
            )
        )
    
    return keyframes


def deduplicate_frames(frames: List[Keyframe], threshold: int = 8) -> DeduplicatedFrames:
    """
    Remove duplicate frames using perceptual hashing.
    
    Args:
        frames: List of keyframes
        threshold: Hamming distance threshold (frames with distance <= threshold are duplicates)
        
    Returns:
        DeduplicatedFrames with unique frames
    """
    if not frames:
        return DeduplicatedFrames(frames=[], original_count=0, deduplicated_count=0)
    
    kept_frames = []
    original_count = len(frames)
    
    # Always keep first frame
    kept_frames.append(frames[0])
    
    # Check each subsequent frame
    for current_frame in frames[1:]:
        is_unique = True
        current_hash = imagehash.hex_to_hash(current_frame.phash)
        
        # Compare with all kept frames
        for kept_frame in kept_frames:
            kept_hash = imagehash.hex_to_hash(kept_frame.phash)
            distance = current_hash - kept_hash  # Hamming distance
            
            if distance <= threshold:
                # Too similar to existing frame
                is_unique = False
                break
        
        if is_unique:
            kept_frames.append(current_frame)
    
    return DeduplicatedFrames(
        frames=kept_frames,
        original_count=original_count,
        deduplicated_count=len(kept_frames)
    )
