import asyncio
import os
from dotenv import load_dotenv
from openhands.runtime.plugins.agent_skills.letta_reporter import LettaReporter

async def simulate_long_task():
    """Simulate a long-running task with progress updates"""
    reporter = LettaReporter()
    chat_id = "example-chat-123"
    message_id = "example-msg-456"
    
    try:
        # Start task
        await reporter.send_progress_report(
            chat_id=chat_id,
            message_id=message_id,
            content="Starting task analysis...",
            progress=0.0,
            status="in_progress"
        )
        
        # Simulate work with progress updates
        steps = ["Analyzing code", "Running tests", "Generating documentation", 
                "Checking dependencies", "Finalizing changes"]
        
        for i, step in enumerate(steps):
            # Calculate progress
            progress = (i + 1) / len(steps)
            
            # Send progress update
            await reporter.send_progress_report(
                chat_id=chat_id,
                message_id=message_id,
                content=f"{step}...",
                progress=progress,
                status="in_progress"
            )
            
            # Simulate work
            await asyncio.sleep(2)
        
        # Task completed
        await reporter.send_progress_report(
            chat_id=chat_id,
            message_id=message_id,
            content="Task completed successfully!",
            progress=1.0,
            status="completed"
        )
        
    except Exception as e:
        # Report failure
        await reporter.send_progress_report(
            chat_id=chat_id,
            message_id=message_id,
            content=f"Task failed: {str(e)}",
            progress=0.0,
            status="failed"
        )
        raise

async def main():
    # Load environment variables
    load_dotenv()
    
    print("Starting example task with progress reporting...")
    await simulate_long_task()
    print("Task completed!")

if __name__ == "__main__":
    asyncio.run(main())