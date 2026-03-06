#!/usr/bin/env python3
"""
Generate MeetingMind Architecture Diagram
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.storage import S3
from diagrams.aws.ml import Bedrock
from diagrams.onprem.client import Users
from diagrams.programming.framework import React
from diagrams.programming.language import Python
from diagrams.custom import Custom
import os

# Set output format and direction
graph_attr = {
    "fontsize": "16",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.0"
}

node_attr = {
    "fontsize": "12",
    "height": "1.2",
    "width": "2.0"
}

edge_attr = {
    "fontsize": "10"
}

with Diagram(
    "MeetingMind Financial AI - Architecture",
    filename="MeetingMind_Architecture",
    direction="TB",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    show=False
):
    
    # User Interface
    user = Users("Women in Finance\nProfessionals")
    
    with Cluster("Frontend - Streamlit Web UI"):
        ui = Python("Streamlit App\n(Upload & Chat)")
    
    with Cluster("Backend Processing Pipeline"):
        with Cluster("Video Processing"):
            video_extract = Python("Video Pipeline\n(FFmpeg)")
            audio_extract = Python("Audio Extraction\n(Whisper Transcription)")
            frame_extract = Python("Frame Extraction\n(Keyframes)")
            vision_ai = Bedrock("AWS Bedrock\nNova Pro Vision\n(Describe Frames)")
        
        with Cluster("Data Processing"):
            merger = Python("Content Merger\n(Audio + Visual)")
            manifest = Python("Manifest Manager\n(Track Recordings)")
    
    with Cluster("AWS Cloud Services"):
        s3 = S3("S3 Bucket\n(meetingmind-s3)\nJSON Documents")
        kb = Bedrock("Bedrock Knowledge Base\n(Vector Search)")
        agent = Bedrock("Bedrock Agent\n(Q&A Assistant)")
    
    # Flow connections
    user >> Edge(label="Upload .mp4\nFinancial Meeting") >> ui
    
    ui >> Edge(label="Process Video") >> video_extract
    
    video_extract >> Edge(label="Extract Audio") >> audio_extract
    video_extract >> Edge(label="Extract Frames") >> frame_extract
    
    audio_extract >> Edge(label="Transcript") >> merger
    frame_extract >> Edge(label="Frames") >> vision_ai
    vision_ai >> Edge(label="Visual Descriptions") >> merger
    
    merger >> Edge(label="Unified JSON\nDocument") >> s3
    merger >> Edge(label="Update") >> manifest
    
    s3 >> Edge(label="Sync Data") >> kb
    
    kb >> Edge(label="RAG Context") >> agent
    
    ui >> Edge(label="User Query") >> agent
    agent >> Edge(label="AI Response") >> ui
    ui >> Edge(label="Financial Insights") >> user

print("✅ Architecture diagram generated: MeetingMind_Architecture.png")
