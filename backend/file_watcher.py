"""
File watcher for automatic processing of new recordings.
"""
import os
import time
from typing import List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from backend.manifest import load_manifest, is_already_processed
from backend.ingestion import ingest_meeting, generate_meeting_id


def scan_and_process_folder(
    folder_path: str,
    manifest_path: str,
    s3_client,
    bedrock_runtime_client,
    bedrock_agent_client
) -> List[str]:
    """
    Scan folder for unprocessed recordings and process them on startup.
    
    Args:
        folder_path: Path to recordings folder
        manifest_path: Path to manifest.json
        s3_client: Boto3 S3 client
        bedrock_runtime_client: Boto3 Bedrock Runtime client
        bedrock_agent_client: Boto3 Bedrock Agent client
        
    Returns:
        List of processed meeting IDs
    """
    print(f"Scanning {folder_path} for recordings...")
    
    # Load manifest
    manifest = load_manifest(manifest_path)
    
    # Find all .mp4 files
    if not os.path.exists(folder_path):
        print(f"⚠️  Recordings folder not found: {folder_path}")
        return []
    
    video_files = [
        f for f in os.listdir(folder_path)
        if f.endswith('.mp4')
    ]
    
    print(f"Found {len(video_files)} video files")
    
    # Filter out already processed
    unprocessed = [
        f for f in video_files
        if not is_already_processed(f, manifest)
    ]
    
    print(f"{len(unprocessed)} files need processing")
    
    processed_ids = []
    
    # Process each unprocessed file
    for filename in unprocessed:
        video_path = os.path.join(folder_path, filename)
        meeting_id = generate_meeting_id(filename)
        
        success = ingest_meeting(
            video_path,
            meeting_id,
            manifest_path,
            s3_client,
            bedrock_runtime_client,
            bedrock_agent_client
        )
        
        if success:
            processed_ids.append(meeting_id)
    
    print(f"Batch processing complete: {len(processed_ids)}/{len(unprocessed)} succeeded\n")
    
    return processed_ids


def watch_recordings_folder(
    folder_path: str,
    manifest_path: str,
    s3_client,
    bedrock_runtime_client,
    bedrock_agent_client
) -> None:
    """
    Watch folder for new .mp4 files and auto-process them.
    
    Args:
        folder_path: Path to recordings folder
        manifest_path: Path to manifest.json
        s3_client: Boto3 S3 client
        bedrock_runtime_client: Boto3 Bedrock Runtime client
        bedrock_agent_client: Boto3 Bedrock Agent client
    """
    
    class RecordingHandler(FileSystemEventHandler):
        def on_created(self, event):
            if event.is_directory:
                return
            
            if not event.src_path.endswith('.mp4'):
                return
            
            # Wait for file to be fully written
            time.sleep(2)
            
            filename = os.path.basename(event.src_path)
            
            # Check if already processed
            manifest = load_manifest(manifest_path)
            if is_already_processed(filename, manifest):
                print(f"Skipping {filename} (already processed)")
                return
            
            # Process the new file
            meeting_id = generate_meeting_id(filename)
            print(f"\nNew recording detected: {filename}")
            ingest_meeting(
                event.src_path,
                meeting_id,
                manifest_path,
                s3_client,
                bedrock_runtime_client,
                bedrock_agent_client
            )
    
    # Set up watcher
    event_handler = RecordingHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    
    print(f"Watching {folder_path} for new recordings...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped watching")
    
    observer.join()
