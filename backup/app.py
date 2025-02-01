from fastapi import FastAPI
from openhands.runtime.plugins.agent_skills.letta_tool.letta_tool import LettaTool
import uvicorn

app = FastAPI()
letta_tool = None

@app.on_event("startup")
async def startup_event():
    global letta_tool
    print("Initializing OpenHands API")
    letta_tool = LettaTool()
    print("Letta Tool initialized")

@app.get("/")
async def root():
    return {"message": "Welcome to OpenHands API"}

@app.get("/letta")
async def letta_info():
    return {"message": "Letta Tool is ready", "status": "initialized" if letta_tool else "not initialized"}

if __name__ == "__main__":
    uvicorn.run("openhands.server.app:app", host="0.0.0.0", port=3000, reload=True)