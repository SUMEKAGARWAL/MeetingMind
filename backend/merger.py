"""
Merge audio transcript and visual descriptions into unified document.
"""
from datetime import datetime
from typing import List
from backend.models import AudioTranscript, FrameDescription, UnifiedDocument, MergedSegment


def merge_transcript_and_descriptions(
    transcript: AudioTranscript,
    descriptions: List[FrameDescription],
    meeting_id: str
) -> UnifiedDocument:
    """
    Merge audio transcript and visual descriptions maintaining temporal order.
    
    Args:
        transcript: AudioTranscript with timestamped segments
        descriptions: List of FrameDescription objects
        meeting_id: Unique identifier for the meeting
        
    Returns:
        UnifiedDocument with interleaved segments sorted by timestamp
    """
    merged_segments = []
    
    # Convert transcript segments to MergedSegment
    for seg in transcript.segments:
        merged_segments.append(
            MergedSegment(
                timestamp=seg.start,
                content=f"[SPOKEN] {seg.text}",
                type="SPOKEN"
            )
        )
    
    # Convert descriptions to MergedSegment
    for desc in descriptions:
        merged_segments.append(
            MergedSegment(
                timestamp=desc.timestamp,
                content=f"[SCREEN] {desc.description}",
                type="SCREEN"
            )
        )
    
    # Sort by timestamp (stable sort maintains order for equal timestamps)
    merged_segments.sort(key=lambda x: x.timestamp)
    
    return UnifiedDocument(
        meeting_id=meeting_id,
        segments=merged_segments,
        duration=transcript.duration,
        created_at=datetime.now()
    )
