from typing import Any, Dict, Optional
import aiohttp
import os
from dataclasses import dataclass

@dataclass
class LettaConfig:
    """Configuration for Letta API connection"""
    base_url: str
    agent_id: str
    password: str

class LettaReporter:
    """Agent skill for reporting progress to Letta"""
    
    def __init__(self):
        self.config = LettaConfig(
            base_url=os.getenv("LETTA_BASE_URL", "https://letta2.oculair.ca"),
            agent_id=os.getenv("LETTA_AGENT_ID", ""),
            password=os.getenv("LETTA_PASSWORD", "")
        )
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            
    async def _close_session(self):
        """Close aiohttp session if it exists"""
        if self._session and not self._session.closed:
            await self._session.close()
            
    async def send_progress_report(self, 
                                 chat_id: str,
                                 message_id: str,
                                 content: str,
                                 progress: float = 0.0,
                                 status: str = "in_progress") -> Dict[str, Any]:
        """Send a progress report to Letta
        
        Args:
            chat_id: The chat ID
            message_id: The message ID
            content: The progress message content
            progress: Progress value between 0 and 1
            status: Status of the task ("in_progress", "completed", "failed")
            
        Returns:
            Dict containing the Letta API response
        """
        await self._ensure_session()
        
        headers = {
            "Content-Type": "application/json",
            "X-Agent-ID": self.config.agent_id,
            "X-Agent-Password": self.config.password
        }
        
        message = {
            "chat_id": chat_id,
            "message_id": message_id,
            "content": content,
            "metadata": {
                "progress": progress,
                "status": status
            }
        }
        
        try:
            async with self._session.post(
                f"{self.config.base_url}/api/v1/progress",
                headers=headers,
                json=message
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Error from Letta API: {error_text}")
                return await response.json()
        finally:
            await self._close_session()
            
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self._session and not self._session.closed:
            import asyncio
            asyncio.create_task(self._close_session())