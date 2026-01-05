import asyncio
import logging
import sys
import os

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import the agent
from dev_manager_agent.agent import agent as dev_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

async def main():
    print("Initializing Dev Manager...")
    try:
        # Set up session management
        session_service = InMemorySessionService()
        APP_NAME = "dev_productivity_suite"
        USER_ID = "developer_1"
        SESSION_ID = "session_001"
        
        # Create session
        await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
        
        # Create runner
        runner = Runner(
            agent=dev_manager,
            app_name=APP_NAME,
            session_service=session_service
        )
        
        print("\n--- Dev Manager Ready ---")
        prompt = input("Enter command (default: 'Generate a status report for the last 5 commits'): ")
        if not prompt:
            prompt = "Generate a sprint status report based on the last 5 commits."

        print(f"\nProcessing request: '{prompt}'")
        print("Connecting to agents at ports 8001, 8002, 8003...")
        
        # Create user message
        user_content = types.Content(role='user', parts=[types.Part(text=prompt)])
        
        print("\n--- Final Report ---\n")
        
        # Run the agent and stream results
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=user_content):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
                print(final_response)
                
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
