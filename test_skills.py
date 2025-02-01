import sys
from openhands.runtime.plugins.agent_skills.agentskills import __all__ as skills

print("Available skills:")
for skill in skills:
    print(f"- {skill}")

print("\nTesting Letta skills:")
try:
    from openhands.runtime.plugins.agent_skills.letta_tool.letta import ask_letta, ask_letta_async, StreamingResponse
    print("Letta skills imported successfully")
except ImportError as e:
    print(f"Error importing Letta skills: {e}")

print("\nPython path:")
for path in sys.path:
    print(path)