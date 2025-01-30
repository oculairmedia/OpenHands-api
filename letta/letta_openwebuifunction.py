import os
import json
import aiohttp
from typing import Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass

@dataclass
class LettaConfig:
    """Configuration for Letta API connection"""
    LETTA_BASE_URL: str = ""
    LETTA_AGENT_ID: str = ""
    LETTA_PASSWORD: str = ""

class Pipe:
    """Pipe class for handling communication with Letta"""
    
    def __init__(self):
        self.valves = LettaConfig()
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            
    async def _close_session(self):
        """Close aiohttp session if it exists"""
        if self._session and not self._session.closed:
            await self._session.close()
            
    async def send_to_letta(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to Letta API"""
        await self._ensure_session()
        
        headers = {
            "Content-Type": "application/json",
            "X-Agent-ID": self.valves.LETTA_AGENT_ID,
            "X-Agent-Password": self.valves.LETTA_PASSWORD
        }
        
        async with self._session.post(
            f"{self.valves.LETTA_BASE_URL}/api/v1/messages",
            headers=headers,
            json=message
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Error from Letta API: {error_text}")
            return await response.json()
            
    async def pipe(self, 
                  body: Dict[str, Any],
                  __user__: Dict[str, Any],
                  __request__: Any,
                  __event_emitter__: Any) -> AsyncGenerator[Dict[str, Any], None]:
        """Process messages through the pipe"""
        try:
            # Format message for Letta
            letta_message = {
                "chat_id": body.get("chat_id", ""),
                "message_id": body.get("message_id", ""),
                "content": body.get("messages", [{}])[-1].get("content", ""),
                "user": {
                    "id": __user__.get("id", ""),
                    "name": __user__.get("name", "")
                }
            }
            
            # Send to Letta
            response = await self.send_to_letta(letta_message)
            
            # Emit event if callback provided
            if __event_emitter__:
                await __event_emitter__({
                    "type": "message",
                    "data": response
                })
                
            # Return response
            yield response
            
        except Exception as e:
            # Emit error event
            if __event_emitter__:
                await __event_emitter__({
                    "type": "error",
                    "data": {"error": str(e)}
                })
            raise
            
        finally:
            await self._close_session()
            
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self._session and not self._session.closed:
            import asyncio
            asyncio.create_task(self._close_session())