"""
Screen-share detection using edge density and text region analysis.
"""
import cv2
import numpy as np
from typing import Dict


def detect_screen_share(frame_path: str, threshold: Dict[str, float]) -> bool:
    """
    Detect if frame shows screen sharing or just webcam.
    
    Uses edge density and text region detection to distinguish between:
    - Screen-share frames: Sharp edges, text regions, UI elements
    - Webcam frames: Smooth gradients, faces, minimal text
    
    Args:
        frame_path: Path to frame image
        threshold: Dict with 'edge_density_min' and 'text_region_min'
        
    Returns:
        True if screen-share detected, False if webcam-only
    """
    # Load image
    img = cv2.imread(frame_path)
    if img is None:
        raise ValueError(f"Cannot load image: {frame_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Step 1: Calculate edge density using Canny edge detection
    edges = cv2.Canny(gray, threshold1=50, threshold2=150)
    total_pixels = edges.shape[0] * edges.shape[1]
    edge_pixels = np.count_nonzero(edges)
    edge_density = edge_pixels / total_pixels
    
    # Step 2: Detect text regions using contour analysis
    # Apply binary threshold to enhance text regions
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Find contours (potential text regions)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by size (text regions are typically small-to-medium rectangles)
    text_regions = 0
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        aspect_ratio = w / h if h > 0 else 0
        
        # Text region heuristics:
        # - Area between 100 and 50000 pixels
        # - Aspect ratio between 0.1 and 10 (not too elongated)
        if 100 < area < 50000 and 0.1 < aspect_ratio < 10:
            text_regions += 1
    
    # Step 3: Decision logic
    is_screenshare = (
        edge_density >= threshold['edge_density_min'] and
        text_regions >= threshold['text_region_min']
    )
    
    return is_screenshare
