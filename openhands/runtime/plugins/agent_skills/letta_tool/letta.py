"""
Letta Tool - OpenHands Integration with Letta AI

This module provides integration between OpenHands and the Letta AI agent,
enabling natural language interactions with streaming responses, usage tracking,
and conversation history support.
"""

import os
import json
import aiohttp
import asyncio
import logging
from typing import List, Dict, Optional, Any, Callable, Awaitable, Union
from pydantic import BaseModel
from dataclasses import dataclass
from datetime import datetime

# Setup logging
logger = logging.getLogger("Letta AI")
if not logger.handlers:
    logger.setLevel(logging.DEBUG)  # Set to DEBUG for more detailed logging
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False

@dataclass
class StreamingResponse:
    """
    Represents a streaming response from the Letta API.

    This class encapsulates the different types of information that can be
    received during a streaming response session with the Letta API.

    Attributes:
        content: The current accumulated response text
        usage_stats: Optional dictionary containing token usage statistics
        reasoning: Optional string containing model's reasoning steps
    """
    content: str
    usage_stats: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None

__all__ = ['ask_letta', 'ask_letta_async', 'StreamingResponse']

class LettaConfig(BaseModel):
    """
    Configuration settings for the Letta API client.

    This class manages the configuration settings for connecting to and
    interacting with the Letta API. Settings can be configured through
    environment variables.
    """
    LETTA_BASE_URL: str = os.getenv("LETTA_BASE_URL", "https://letta2.oculair.ca")
    LETTA_AGENT_ID: str = os.getenv("LETTA_AGENT_ID", "agent-b18bce75-2e73-4470-bf17-381170888a2b")
    LETTA_PASSWORD: str = os.getenv("LETTA_PASSWORD", "lettaSecurePass123")
    SHOW_REASONING: bool = os.getenv("LETTA_SHOW_REASONING", "true").lower() == "true"
    SHOW_USAGE_STATS: bool = os.getenv("LETTA_SHOW_USAGE_STATS", "true").lower() == "true"

async def _get_letta_response(
    messages: List[Dict[str, str]], 
    config: LettaConfig,
    callback: Optional[Callable[[StreamingResponse], Awaitable[None]]] = None
) -> str:
    """
    Send messages to the Letta agent and get its response.

    This function handles the low-level communication with the Letta API,
    including streaming responses, usage statistics, and reasoning messages.

    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        config: LettaConfig instance with API credentials and settings
        callback: Optional async callback function for streaming updates

    Returns:
        The final response content as a string
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "X-BARE-PASSWORD": f"password {config.LETTA_PASSWORD}"
    }

    # Format messages for Letta API
    formatted_messages = [{
        "role": "user" if msg["role"] != "system" else "system",
        "content": msg.get("content", "")
    } for msg in messages if msg.get("role") in ["user", "system", "assistant"]]

    if not formatted_messages:
        formatted_messages.append({"role": "user", "content": "Hello"})

    payload = {
        "messages": [formatted_messages[-1]],  # Send only the last message
        "stream_steps": True,
        "stream_tokens": True,
    }

    url = f"{config.LETTA_BASE_URL}/api/v1/agents/{config.LETTA_AGENT_ID}/messages/stream"
    
    logger.debug(f"Sending request to {url}")
    logger.debug(f"Request headers: {headers}")
    logger.debug(f"Request data: {json.dumps(payload, indent=2)}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 422:
                    error_text = await response.text()
                    raise ValueError(f"API Validation Error: {error_text}")

                response.raise_for_status()
                
                # Process the streaming response
                response_content = []
                current_response = StreamingResponse(content="")
                
                async for line in response.content:
                    decoded_line = line.decode('utf-8')
                    logger.debug(f"Raw line: {decoded_line}")
                    
                    if not decoded_line.strip():
                        logger.debug("Skipping empty line")
                        continue
                        
                    if not decoded_line.startswith('data: '):
                        logger.debug(f"Skipping non-data line: {decoded_line}")
                        continue

                    if decoded_line == 'data: [DONE]':
                        logger.debug("Received DONE marker")
                        break

                    try:
                        json_str = decoded_line[6:]
                        logger.debug(f"Parsing JSON: {json_str}")
                        chunk_data = json.loads(json_str)
                        message_type = chunk_data.get("message_type")
                        logger.debug(f"Message type: {message_type}")

                        if message_type == "assistant_message":
                            content = chunk_data.get("content", "")
                            if content:
                                response_content.append(content)
                                current_response.content = "\n".join(response_content)
                                if callback:
                                    await callback(current_response)
                                logger.debug(f"Assistant message: {content}")

                        elif message_type == "usage_statistics" and config.SHOW_USAGE_STATS:
                            current_response.usage_stats = chunk_data
                            if callback:
                                await callback(current_response)
                            logger.debug(f"Usage statistics: {chunk_data}")

                        elif message_type == "reasoning_message" and config.SHOW_REASONING:
                            message = chunk_data.get("message", "")
                            if message:
                                current_response.reasoning = message
                                if callback:
                                    await callback(current_response)
                                logger.debug(f"Reasoning message: {message}")

                    except json.JSONDecodeError as e:
                        logger.error(f"JSON Parse Error: {str(e)}")
                        logger.error(f"Problem chunk: {decoded_line}")
                        continue

        return current_response.content

    except aiohttp.ClientError as e:
        raise RuntimeError(f"Error communicating with Letta agent: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")

async def ask_letta_async(
    message: str,
    system_prompt: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None,
    callback: Optional[Callable[[StreamingResponse], Awaitable[None]]] = None
) -> str:
    """
    Async version of ask_letta that supports streaming responses.
    See ask_letta for parameter documentation.
    """
    config = LettaConfig()
    
    if not config.LETTA_AGENT_ID or not config.LETTA_PASSWORD:
        raise ValueError("LETTA_AGENT_ID and LETTA_PASSWORD environment variables must be set")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    if history:
        messages.extend(history)
    
    messages.append({"role": "user", "content": message})

    return await _get_letta_response(messages, config, callback)

def ask_letta(
    message: str,
    system_prompt: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None,
    stream_handler: Optional[Callable[[StreamingResponse], None]] = None
) -> str:
    """
    Send a message to Letta AI and get its response.

    Args:
        message: The message to send to Letta
        system_prompt: Optional system prompt to set context
        history: Optional chat history as list of message dicts
        stream_handler: Optional callback for streaming responses

    Returns:
        Letta's response as a string

    Example:
        >>> ask_letta("What is the capital of France?")
        "The capital of France is Paris."

        >>> def handle_stream(response):
        ...     print(f"Content: {response.content}")
        ...     if response.reasoning:
        ...         print(f"Reasoning: {response.reasoning}")
        ...     if response.usage_stats:
        ...         print(f"Usage: {response.usage_stats}")
        
        >>> ask_letta(
        ...     "Tell me more about Paris.",
        ...     system_prompt="You are a travel expert.",
        ...     history=[
        ...         {"role": "user", "content": "What is the capital of France?"},
        ...         {"role": "assistant", "content": "The capital of France is Paris."}
        ...     ],
        ...     stream_handler=handle_stream
        ... )
    """
    async def sync_to_async_handler(response: StreamingResponse) -> None:
        if stream_handler:
            stream_handler(response)

    return asyncio.run(ask_letta_async(
        message=message,
        system_prompt=system_prompt,
        history=history,
        callback=sync_to_async_handler if stream_handler else None
    ))