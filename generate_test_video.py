#!/usr/bin/env python3
"""
Generate a synthetic test meeting video for MeetingMind.

Creates a 60-second video with:
- Spoken narration (text-to-speech)
- Screen content (slides with charts and text)
- Realistic meeting scenario

Requirements:
    pip install gtts pillow moviepy numpy
"""
import os
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
import tempfile


def create_slide(text, title, width=1920, height=1080, bg_color=(255, 255, 255)):
    """Create a slide image with title and text."""
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fall back to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
        text_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 50)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Draw title
    draw.text((100, 100), title, fill=(0, 0, 0), font=title_font)
    
    # Draw text content
    y_offset = 300
    for line in text.split('\n'):
        draw.text((100, y_offset), line, fill=(50, 50, 50), font=text_font)
        y_offset += 80
    
    # Draw a simple chart (bar chart)
    chart_x = 1200
    chart_y = 400
    bars = [300, 450, 350, 500]
    bar_width = 80
    colors = [(52, 152, 219), (46, 204, 113), (241, 196, 15), (231, 76, 60)]
    
    for i, (height_val, color) in enumerate(zip(bars, colors)):
        x = chart_x + i * (bar_width + 20)
        draw.rectangle(
            [x, chart_y + (500 - height_val), x + bar_width, chart_y + 500],
            fill=color
        )
    
    return np.array(img)


def generate_test_meeting():
    """Generate a complete test meeting video."""
    print("Generating test meeting video...")
    
    # Meeting script with timestamps
    scenes = [
        {
            "duration": 15,
            "title": "Q4 Revenue Analysis",
            "text": "Revenue Growth\n• Q1: $2.3M\n• Q2: $3.1M\n• Q3: $2.8M\n• Q4: $4.2M",
            "narration": "Good morning everyone. Let's review our Q4 revenue performance. As you can see on the chart, we had strong growth in Q4, reaching 4.2 million dollars, which is a 35% increase from Q3."
        },
        {
            "duration": 15,
            "title": "Customer Metrics",
            "text": "Key Metrics\n• Active Users: 45,000\n• Churn Rate: 3.2%\n• NPS Score: 72\n• Avg Revenue: $93",
            "narration": "Our customer metrics are looking healthy. We now have 45,000 active users with a churn rate of only 3.2%. Our Net Promoter Score improved to 72, which is excellent."
        },
        {
            "duration": 15,
            "title": "Product Roadmap",
            "text": "Q1 2026 Priorities\n• Mobile App Launch\n• API v2 Release\n• Enterprise Features\n• Performance Optimization",
            "narration": "Looking ahead to Q1 2026, our main priorities are launching the mobile app, releasing API version 2, adding enterprise features, and optimizing performance across the platform."
        },
        {
            "duration": 15,
            "title": "Action Items",
            "text": "Next Steps\n• Marketing: Launch campaign\n• Engineering: API testing\n• Sales: Enterprise outreach\n• Support: Training update",
            "narration": "To wrap up, here are our action items. Marketing will launch the new campaign next week. Engineering needs to complete API testing by month end. Sales team will focus on enterprise outreach, and support will update training materials."
        }
    ]
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    print(f"Using temp directory: {temp_dir}")
    
    # Generate audio and video clips
    video_clips = []
    audio_clips = []
    current_time = 0
    
    for i, scene in enumerate(scenes):
        print(f"Creating scene {i+1}/4: {scene['title']}")
        
        # Generate slide image
        slide_img = create_slide(scene['text'], scene['title'])
        
        # Generate narration audio
        audio_path = os.path.join(temp_dir, f"narration_{i}.mp3")
        tts = gTTS(text=scene['narration'], lang='en', slow=False)
        tts.save(audio_path)
        
        # Create video clip
        video_clip = ImageClip(slide_img).set_duration(scene['duration'])
        video_clip = video_clip.set_start(current_time)
        
        # Create audio clip
        audio_clip = AudioFileClip(audio_path)
        audio_clip = audio_clip.set_start(current_time)
        
        video_clips.append(video_clip)
        audio_clips.append(audio_clip)
        
        current_time += scene['duration']
    
    print("Compositing final video...")
    
    # Combine all clips
    final_video = concatenate_videoclips(video_clips, method="compose")
    final_audio = CompositeAudioClip(audio_clips)
    final_video = final_video.set_audio(final_audio)
    
    # Export
    output_path = "recordings/test_meeting.mp4"
    os.makedirs("recordings", exist_ok=True)
    
    print(f"Exporting to {output_path}...")
    final_video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile=os.path.join(temp_dir, 'temp-audio.m4a'),
        remove_temp=True
    )
    
    print(f"\n✓ Test meeting video created: {output_path}")
    print(f"Duration: 60 seconds")
    print(f"Content: 4 slides with narration about Q4 business review")
    print(f"\nYou can now process it with: python3 ingest.py")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


if __name__ == "__main__":
    try:
        generate_test_meeting()
    except ImportError as e:
        print(f"\n❌ Missing required package: {e}")
        print("\nInstall required packages:")
        print("pip install gtts pillow moviepy numpy")
    except Exception as e:
        print(f"\n❌ Error generating video: {e}")
        import traceback
        traceback.print_exc()
