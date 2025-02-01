from openhands.runtime.plugins.agent_skills import agentskills

print("Available tools:")
for tool in agentskills.__all__:
    print(f"- {tool}")