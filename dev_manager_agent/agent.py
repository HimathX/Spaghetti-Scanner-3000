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
    model="gemini-2.0-flash-exp",
    instruction="""You are the Dev Manager. Your goal is to generate a 'Sprint Status Report'.
    You have access to a team of agents:
    1. 'repo_agent': Fetches commits and code.
    2. 'security_agent': Scans for vulnerabilities.
    3. 'reviewer_agent': Reviews code quality.
    
    Workflow:
    1. Ask 'repo_agent' for the last few commits (e.g., 5).
    2. For each commit, get the analysis from 'security_agent' and 'reviewer_agent' effectively.
       (Note: You might need to fetch the code content or diff first using repo_agent if the other agents need raw text, 
        OR ask the repo_agent to get the diff and pass it to them).
    3. Consolidate all findings into a Markdown report.
    
    Always verify you have the data before reporting.
    """,
    sub_agents=[repo_service, security_service, reviewer_service]
)

app = to_a2a(agent)
root_agent = agent

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
