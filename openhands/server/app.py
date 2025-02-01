import warnings
from contextlib import asynccontextmanager

with warnings.catch_warnings():
    warnings.simplefilter('ignore')

from fastapi import (
    FastAPI,
)
from pydantic import BaseModel

import openhands.agenthub  # noqa F401 (we import this to get the agents registered)
from openhands import __version__
from openhands.server.routes.conversation import app as conversation_api_router
from openhands.server.routes.feedback import app as feedback_api_router
from openhands.server.routes.files import app as files_api_router
from openhands.server.routes.github import app as github_api_router
from openhands.server.routes.manage_conversations import (
    app as manage_conversation_api_router,
)
from openhands.server.routes.public import app as public_api_router
from openhands.server.routes.security import app as security_api_router
from openhands.server.routes.settings import app as settings_router
from openhands.server.routes.trajectory import app as trajectory_router
from openhands.server.shared import conversation_manager
from openhands.runtime.plugins.agent_skills.letta_tool.letta_tool import LettaTool

class LettaRequest(BaseModel):
    text: str
    target_language: str = "en"

letta_tool = LettaTool()

@asynccontextmanager
async def _lifespan(app: FastAPI):
    async with conversation_manager:
        yield


app = FastAPI(
    title='OpenHands',
    description='OpenHands: Code Less, Make More',
    version=__version__,
    lifespan=_lifespan,
)


@app.get('/health')
async def health():
    return 'OK'

@app.post('/api/letta')
async def letta_endpoint(request: LettaRequest):
    result = letta_tool.execute(request.text, request.target_language)
    return result

app.include_router(public_api_router)
app.include_router(files_api_router)
app.include_router(security_api_router)
app.include_router(feedback_api_router)
app.include_router(conversation_api_router)
app.include_router(manage_conversation_api_router)
app.include_router(settings_router)
app.include_router(github_api_router)
app.include_router(trajectory_router)
