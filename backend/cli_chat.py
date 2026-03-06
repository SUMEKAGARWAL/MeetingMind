"""
CLI chat interface for asking questions about meetings.
"""
from typing import List
from backend.models import ChatMessage
from backend.chat import retrieve_and_generate


def format_timestamp(seconds: float) -> str:
    """Format timestamp as MM:SS."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def run_cli_chat(bedrock_agent_client, agent_id: str = None) -> None:
    """
    Run interactive CLI chat loop.
    
    Args:
        bedrock_agent_client: Boto3 Bedrock Agent Runtime client
        agent_id: Bedrock Agent ID (uses config if not provided)
    """
    print("=" * 60)
    print("MeetingMind Chat")
    print("=" * 60)
    print("Ask questions about your meetings. Type 'exit' to quit.\n")
    
    conversation_history: List[ChatMessage] = []
    
    while True:
        # Get user input
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not question:
            continue
        
        if question.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
        
        # Add user message to history
        user_message = ChatMessage(role="user", content=question)
        conversation_history.append(user_message)
        
        # Get response from agent
        print("\nAssistant: ", end="", flush=True)
        
        try:
            response = retrieve_and_generate(
                question=question,
                conversation_history=conversation_history[:-1],  # Exclude current question
                bedrock_agent_client=bedrock_agent_client,
                agent_id=agent_id
            )
            
            print(response.answer)
            
            # Show sources if available
            if response.sources:
                print("\nSources:")
                for i, source in enumerate(response.sources, 1):
                    meeting_id = source.get('meeting_id', 'unknown')
                    timestamp = source.get('timestamp', 0)
                    source_type = source.get('type', 'unknown')
                    timestamp_str = format_timestamp(timestamp)
                    print(f"  [{i}] {meeting_id} at {timestamp_str} ({source_type})")
            
            # Add assistant message to history
            assistant_message = ChatMessage(
                role="assistant",
                content=response.answer,
                sources=response.sources
            )
            conversation_history.append(assistant_message)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            # Remove failed user message from history
            conversation_history.pop()
