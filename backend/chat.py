"""
Chat functionality using Bedrock Agent for RAG.
"""
import json
import uuid
from typing import List
from backend.models import ChatMessage, ChatResponse
from backend.config import config


def retrieve_and_generate(
    question: str,
    conversation_history: List[ChatMessage],
    bedrock_agent_client,
    agent_id: str = None
) -> ChatResponse:
    """
    Retrieve context and generate answer using Bedrock Agent.
    
    Args:
        question: User's question
        conversation_history: Previous messages in conversation
        bedrock_agent_client: Boto3 Bedrock Agent Runtime client
        agent_id: Bedrock Agent ID (uses config if not provided)
        
    Returns:
        ChatResponse with answer and sources
    """
    if agent_id is None:
        agent_id = config.BEDROCK_AGENT_ID
    
    if not agent_id:
        raise ValueError("BEDROCK_AGENT_ID not configured")
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    try:
        # Call Bedrock Agent
        response = bedrock_agent_client.invoke_agent(
            agentId=agent_id,
            agentAliasId="TSTALIASID",  # Use test alias
            sessionId=session_id,
            inputText=question
        )
        
        # Parse streaming response
        answer_text = ""
        citations = []
        
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    answer_text += chunk['bytes'].decode('utf-8')
            
            if 'trace' in event:
                trace = event['trace']
                if 'orchestrationTrace' in trace:
                    orch_trace = trace['orchestrationTrace']
                    if 'observation' in orch_trace:
                        observation = orch_trace['observation']
                        if 'knowledgeBaseLookupOutput' in observation:
                            kb_output = observation['knowledgeBaseLookupOutput']
                            if 'retrievedReferences' in kb_output:
                                for ref in kb_output['retrievedReferences']:
                                    citations.append(ref)
        
        # Parse citations into sources
        sources = []
        for citation in citations:
            if 'content' in citation and 'text' in citation['content']:
                source = {
                    'meeting_id': citation.get('location', {}).get('s3Location', {}).get('uri', 'unknown'),
                    'timestamp': 0,  # Would need to parse from content
                    'type': 'SPOKEN',  # Would need to detect from content
                    'content': citation['content']['text'][:200]  # First 200 chars
                }
                sources.append(source)
        
        return ChatResponse(
            answer=answer_text.strip(),
            sources=sources,
            conversation_id=session_id
        )
        
    except Exception as e:
        raise Exception(f"Bedrock Agent call failed: {e}")
