import os
import logging
from typing import Dict, Any

from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define remote agent connections
repo_service = RemoteA2aAgent(
    name="repo_agent",
    description="Agent for fetching repository data (commits, files).",
    agent_card=f"http://127.0.0.1:8001{AGENT_CARD_WELL_KNOWN_PATH}"
)

security_service = RemoteA2aAgent(
    name="security_agent",
    description="Agent for security scanning (secrets, sql injection).",
    agent_card=f"http://127.0.0.1:8002{AGENT_CARD_WELL_KNOWN_PATH}"
)

reviewer_service = RemoteA2aAgent(
    name="reviewer_agent",
    description="Agent for code reviews and quality checks.",
    agent_card=f"http://127.0.0.1:8003{AGENT_CARD_WELL_KNOWN_PATH}"
)

# Initialize the agent
agent = Agent(
    name="dev_manager",
    model="gemini-2.0-flash",
    instruction="""You are the Dev Manager, an AI assistant for software development.
    
    Your capabilities:
    1. **Activity Summary**: Generate a comprehensive report on recent changes (commits), analyzing them for security and quality.
    2. **Interactive Assistance**: Answer questions about the codebase, specific commits, or file contents.
    
    You have a team of sub-agents:
    - 'repo_agent': Fetches commits, file contents, and diffs.
    - 'security_agent': Scans code for vulnerabilities.
    - 'reviewer_agent': Reviews code for quality and best practices.
    
    **Workflows:**
    
    **1. Activity Summary (Trigger: "What's new?", "Summarize recent changes", "Report"):**
       - **STEP 1**: Call 'repo_agent' to get the list of recent commits.
       - **STEP 2**: For each interesting commit in that list, call 'repo_agent' AGAIN to get the diff/changes.
       - **STEP 3**: ONLY ONCE YOU HAVE THE CODE CONTENT, send that content to 'security_agent' and 'reviewer_agent' for analysis.
       - **STEP 4**: Consolidate into a summary.

    **2. Code Review / Interactive Queries:**
       - **STEP 1**: If the user asks for a review of a specific commit or "the last commit", YOU MUST FIRST call 'repo_agent' to get the diff/content of that commit.
       - **STEP 2**: WAIT for the code content to be returned by 'repo_agent'.
       - **STEP 3**: Send the *actual code content* you received to 'reviewer_agent' and 'security_agent'. **DO NOT** call them empty-handed.
       - **STEP 4**: Present the results clearly.
       
    **Important:**
    - If a user asks "Give me a code review" without context, assume they mean the *last commit* or ask for clarification, but PREFER to assume last commit if you recently discussed it.
    - Always output text based on the tools' responses. Do not return empty responses.
    """,
    sub_agents=[repo_service, security_service, reviewer_service],
    tools=[]
)

app = to_a2a(agent)
root_agent = agent

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
