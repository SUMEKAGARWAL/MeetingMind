"""
Data models for MeetingMind using Pydantic.
"""
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# Audio Pipeline Models
class TranscriptSegment(BaseModel):
    """A single segment of transcribed audio with timestamps."""
    start: float  # seconds
    end: float    # seconds
    text: str


class AudioTranscript(BaseModel):
    """Complete audio transcript with metadata."""
    segments: List[TranscriptSegment]
    language: str
    duration: float


# Video Pipeline Models
class Keyframe(BaseModel):
    """A single extracted keyframe with metadata."""
    timestamp: float  # seconds
    frame_path: str
    phash: str  # perceptual hash


class DeduplicatedFrames(BaseModel):
    """Result of frame deduplication."""
    frames: List[Keyframe]
    original_count: int
    deduplicated_count: int


# Vision Describer Models
class FrameDescription(BaseModel):
    """Description of a single frame's visual content."""
    timestamp: float
    description: str
    frame_path: str


# Merged Document Models
class MergedSegment(BaseModel):
    """A single segment in the unified document."""
    timestamp: float
    content: str
    type: Literal["SPOKEN", "SCREEN"]


class UnifiedDocument(BaseModel):
    """Unified document combining transcript and visual descriptions."""
    meeting_id: str
    segments: List[MergedSegment]
    duration: float
    created_at: datetime


# Chat Models
class ChatMessage(BaseModel):
    """A single message in a conversation."""
    role: Literal["user", "assistant"]
    content: str
    sources: Optional[List[Dict]] = None


class ChatResponse(BaseModel):
    """Response from the chat system."""
    answer: str
    sources: List[Dict]
    conversation_id: str


# Manifest Models
class ProcessedRecording(BaseModel):
    """Record of a processed meeting recording."""
    meeting_id: str
    filename: str
    processed_at: datetime
    s3_uri: str
    duration: float


class Manifest(BaseModel):
    """Manifest tracking all processed recordings."""
    recordings: List[ProcessedRecording] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)
