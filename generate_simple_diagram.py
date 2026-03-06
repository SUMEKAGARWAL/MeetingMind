#!/usr/bin/env python3
"""
Generate MeetingMind Architecture Diagram using matplotlib
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import matplotlib.lines as mlines

# Create figure with dark background
fig, ax = plt.subplots(1, 1, figsize=(18, 14))
fig.patch.set_facecolor('#1a1a2e')
ax.set_xlim(0, 10)
ax.set_ylim(0, 14)
ax.axis('off')
ax.set_facecolor('#1a1a2e')

# Title
ax.text(5, 13.5, 'MeetingMind Financial AI - Architecture', 
        ha='center', va='top', fontsize=22, fontweight='bold', color='white')
ax.text(5, 13, 'Women in Financial AI Hackathon', 
        ha='center', va='top', fontsize=13, style='italic', color='#FF6B9D')

# Color scheme - AWS Orange and dark theme
color_user = '#4A5568'
color_frontend = '#2D3748'
color_backend = '#FF9900'  # AWS Orange
color_aws = '#232F3E'  # AWS Dark Blue
color_text = 'white'
color_arrow = '#FF9900'

# Helper function to create boxes with AWS style
def create_box(ax, x, y, width, height, text, color, fontsize=10, is_aws=False):
    if is_aws:
        # AWS service box style
        box = FancyBboxPatch((x, y), width, height,
                             boxstyle="round,pad=0.15", 
                             edgecolor='#FF9900', facecolor=color, linewidth=3)
    else:
        box = FancyBboxPatch((x, y), width, height,
                             boxstyle="round,pad=0.1", 
                             edgecolor='#4A5568', facecolor=color, linewidth=2)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text, 
           ha='center', va='center', fontsize=fontsize, fontweight='bold', 
           color=color_text)

# Helper function to create arrows
def create_arrow(ax, x1, y1, x2, y2, label=''):
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', mutation_scale=25, 
                           linewidth=2.5, color=color_arrow)
    ax.add_patch(arrow)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x + 0.3, mid_y, label, fontsize=9, color='white',
               bbox=dict(boxstyle='round', facecolor='#2D3748', alpha=0.9, 
                        edgecolor='#FF9900', linewidth=1.5))

# 1. User Layer
create_box(ax, 0.5, 11.5, 2, 0.8, '👩‍💼 Women in Finance\nProfessionals', color_user, 9)

# 2. Frontend Layer
create_box(ax, 0.5, 10, 2, 0.8, '🖥️ Streamlit Web UI\nUpload & Chat', color_frontend, 9)

# 3. Backend Processing Layer
# Video Processing
create_box(ax, 3.5, 11, 1.8, 0.6, '📹 Video Pipeline\nFFmpeg', color_backend, 8)
create_box(ax, 3.5, 10, 1.8, 0.6, '🎵 Audio Extract\nWhisper', color_backend, 8)
create_box(ax, 5.5, 11, 1.8, 0.6, '🎬 Frame Extract\nKeyframes', color_backend, 8)

# AI Processing
create_box(ax, 5.5, 9.5, 1.8, 0.8, '🤖 AWS Bedrock\nNova Pro Vision\nDescribe Frames', color_aws, 8)

# Data Processing
create_box(ax, 3.5, 8.5, 1.8, 0.6, '📊 Content Merger\nAudio + Visual', color_backend, 8)
create_box(ax, 5.5, 8.5, 1.8, 0.6, '📝 Manifest\nManager', color_backend, 8)

# 4. AWS Cloud Services Layer
# Background box for AWS services
aws_bg = FancyBboxPatch((0.3, 5.5), 9.4, 2.5,
                        boxstyle="round,pad=0.2", 
                        edgecolor='#FF9900', facecolor='#16202c', 
                        linewidth=4, linestyle='-', alpha=0.8)
ax.add_patch(aws_bg)
ax.text(5, 7.8, 'AWS Cloud Services', ha='center', fontsize=12, fontweight='bold',
       color='white', bbox=dict(boxstyle='round', facecolor='#FF9900', 
                                edgecolor='white', linewidth=2))

create_box(ax, 1, 6.5, 2, 0.8, 'Amazon S3\nmeetingmind-s3\nJSON Storage', color_aws, 8, is_aws=True)
create_box(ax, 4, 6.5, 2, 0.8, 'Amazon Bedrock\nKnowledge Base\nVector Search', color_aws, 8, is_aws=True)
create_box(ax, 7, 6.5, 2, 0.8, 'Amazon Bedrock\nAgent\nQ&A Assistant', color_aws, 8, is_aws=True)

# 5. Response back to user
create_box(ax, 0.5, 4.5, 2, 0.8, '💡 Financial Insights\nto User', color_user, 9)

# Arrows - Flow
# User to Frontend
create_arrow(ax, 1.5, 11.5, 1.5, 10.8, 'Upload .mp4')

# Frontend to Backend
create_arrow(ax, 2.5, 10.4, 3.5, 11.3, 'Process')
create_arrow(ax, 2.5, 10.2, 3.5, 10.3, '')

# Backend processing flow
create_arrow(ax, 4.4, 10.6, 4.4, 10.3, 'Audio')
create_arrow(ax, 5.3, 11.3, 6.4, 11.3, 'Frames')
create_arrow(ax, 6.4, 10.6, 6.4, 10.3, 'Frames')

# To merger
create_arrow(ax, 4.4, 10, 4.4, 9.1, 'Transcript')
create_arrow(ax, 6.4, 9.5, 5.3, 9, 'Descriptions')

# To S3
create_arrow(ax, 4.4, 8.5, 2, 7.3, 'JSON Doc')
create_arrow(ax, 5.5, 8.7, 6.5, 8.7, 'Update')

# S3 to KB
create_arrow(ax, 3, 6.9, 4, 6.9, 'Sync')

# KB to Agent
create_arrow(ax, 6, 6.9, 7, 6.9, 'RAG Context')

# User query path
create_arrow(ax, 1.5, 10, 1.5, 8, '')
create_arrow(ax, 1.5, 8, 8, 8, 'User Query')
create_arrow(ax, 8, 8, 8, 7.3, '')

# Response path
create_arrow(ax, 8, 6.5, 8, 5.5, 'Response')
create_arrow(ax, 8, 5.5, 2.5, 5.5, '')
create_arrow(ax, 2.5, 5.5, 2.5, 5.3, '')
create_arrow(ax, 1.5, 4.5, 1.5, 3.5, 'Insights')

# Legend
legend_elements = [
    mpatches.Patch(facecolor=color_user, edgecolor='#4A5568', label='User Interface'),
    mpatches.Patch(facecolor=color_frontend, edgecolor='#4A5568', label='Frontend'),
    mpatches.Patch(facecolor=color_backend, edgecolor='#FF9900', label='Backend Processing'),
    mpatches.Patch(facecolor=color_aws, edgecolor='#FF9900', label='AWS Services')
]
legend = ax.legend(handles=legend_elements, loc='lower center', ncol=4, fontsize=10, 
                  bbox_to_anchor=(0.5, -0.05), facecolor='#2D3748', edgecolor='#FF9900',
                  framealpha=0.9)
for text in legend.get_texts():
    text.set_color('white')

# Key features text
features_text = """Key Features:
• Audio transcription with Whisper
• Visual content with Bedrock Nova Pro
• RAG-based Q&A with Knowledge Base
• Professional UI for women in finance"""
ax.text(0.5, 3, features_text, fontsize=9, verticalalignment='top', color='white',
       bbox=dict(boxstyle='round', facecolor='#2D3748', alpha=0.9, 
                edgecolor='#FF9900', linewidth=2))

# Tech stack text
tech_text = """Technology Stack:
• Frontend: Streamlit (Python)
• Backend: Python, FFmpeg, OpenCV
• AI/ML: AWS Bedrock (Nova Pro)
• Storage: Amazon S3
• Region: us-west-2"""
ax.text(5.5, 3, tech_text, fontsize=9, verticalalignment='top', color='white',
       bbox=dict(boxstyle='round', facecolor='#2D3748', alpha=0.9,
                edgecolor='#FF9900', linewidth=2))

plt.tight_layout()
plt.savefig('MeetingMind_Architecture.png', dpi=300, bbox_inches='tight', 
           facecolor='#1a1a2e', edgecolor='none')
print("✅ Architecture diagram generated: MeetingMind_Architecture.png")
print("   Dark theme with AWS colors - ready for your PowerPoint presentation!")
