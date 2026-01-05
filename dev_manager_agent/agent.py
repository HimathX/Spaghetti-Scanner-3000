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

# Define local tools
def deploy_application(github_token: str, repo_url: str, google_api_key: str) -> str:
    """
    Simulates deploying the application to the cloud.
    
    Args:
        github_token: The user's GitHub Personal Access Token.
        repo_url: The full URL of the repository to deploy.
        google_api_key: The user's Google API Key.
        
    Returns:
        A status message confirming deployment.
    """
    # In a real app, this would use the secrets to trigger a build/deploy pipeline
    
    # Mask secrets for logging/output
    masked_token = f"{github_token[:4]}...{github_token[-4:]}" if len(github_token) > 8 else "***"
    masked_key = f"{google_api_key[:4]}...{google_api_key[-4:]}" if len(google_api_key) > 8 else "***"
    
    log_msg = (
        f"Starting deployment for {repo_url}\n"
        f"Using GitHub Token: {masked_token}\n"
        f"Using Google API Key: {masked_key}"
    )
    logger.info(log_msg)
    
    return f"Deployment started successfully for {repo_url}! (Simulation)"

# Initialize the agent
agent = Agent(
    name="dev_manager",
    model="gemini-2.0-flash-exp",
    instruction="""You are the Dev Manager. Your goal is to generate a 'Sprint Status Report' OR help deploy the application.
    
    You have access to a team of agents:
    1. 'repo_agent': Fetches commits and code.
    2. 'security_agent': Scans for vulnerabilities.
    3. 'reviewer_agent': Reviews code quality.
    
    Workflow for Status Reports:
    1. Ask 'repo_agent' for the last few commits (e.g., 5).
    2. For each commit, get the analysis from 'security_agent' and 'reviewer_agent'.
    3. Consolidate all findings into a Markdown report.
    
    Workflow for Deployment:
    1. If the user asks to "deploy", you MUST collect the following secrets from them via chat if not provided:
       - GitHub Token
       - Repository URL
       - Google API Key
    2. Ask for them one by one. Explain why you need them.
    3. Once you have ALL three, call the `deploy_application` tool.
    
    Always verify you have the data before reporting or deploying.
    """,
    sub_agents=[repo_service, security_service, reviewer_service],
    tools=[deploy_application]
)

app = to_a2a(agent)
root_agent = agent

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
