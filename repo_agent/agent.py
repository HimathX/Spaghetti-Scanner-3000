import os
import logging
from typing import List, Dict, Any, Optional

from fastapi import FastAPI
from github import Github, GithubException
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Define tools as standalone functions
def fetch_recent_commits(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetches the recent commits from the repository.

    Args:
        limit: The number of commits to fetch.

    Returns:
        A list of dictionaries containing commit information (sha, author, message, date).
    """
    github_token = os.getenv("GITHUB_TOKEN")
    repo_url = os.getenv("GITHUB_REPO_URL")
    
    if not github_token or not repo_url:
        return [{"error": "GITHUB_TOKEN or GITHUB_REPO_URL not configured"}]
    
    try:
        github_client = Github(github_token)
        if "github.com/" in repo_url:
            repo_name = repo_url.split("github.com/")[1].removesuffix(".git")
        else:
            repo_name = repo_url
        
        repo = github_client.get_repo(repo_name)
        commits = list(repo.get_commits()[:limit])
        result = []
        for commit in commits:
            result.append({
                "sha": commit.sha,
                "author": commit.commit.author.name,
                "date": commit.commit.author.date.isoformat(),
                "message": commit.commit.message
            })
        return result
    except Exception as e:
        return [{"error": f"Error fetching commits: {e}"}]

def analyze_code_changes(commit_sha: str) -> Dict[str, Any]:
    """
    Analyzes the changes in a specific commit.

    Args:
        commit_sha: The SHA of the commit to analyze.

    Returns:
        A dictionary containing the files changed, additions, deletions, and the patch.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    repo_url = os.getenv("GITHUB_REPO_URL")
    
    if not github_token or not repo_url:
        return {"error": "GITHUB_TOKEN or GITHUB_REPO_URL not configured"}
    
    try:
        github_client = Github(github_token)
        if "github.com/" in repo_url:
            repo_name = repo_url.split("github.com/")[1].removesuffix(".git")
        else:
            repo_name = repo_url
        
        repo = github_client.get_repo(repo_name)
        commit = repo.get_commit(commit_sha)
        files_changed = []
        for file in commit.files:
            files_changed.append({
                "filename": file.filename,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "patch": file.patch if file.patch else ""
            })
        
        return {
            "sha": commit_sha,
            "message": commit.commit.message,
            "stats": commit.stats.raw_data,
            "files": files_changed
        }
    except Exception as e:
        return {"error": f"Error analyzing commit: {e}"}

def get_file_content(file_path: str, ref: Optional[str] = None) -> str:
    """
    Retrieves the content of a specific file.

    Args:
       file_path: The path to the file in the repository.
       ref: The commit SHA or branch name (optional, defaults to default branch).

    Returns:
        The content of the file as a string.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    repo_url = os.getenv("GITHUB_REPO_URL")
    
    if not github_token or not repo_url:
        return "Error: GITHUB_TOKEN or GITHUB_REPO_URL not configured"
    
    try:
        github_client = Github(github_token)
        if "github.com/" in repo_url:
            repo_name = repo_url.split("github.com/")[1].removesuffix(".git")
        else:
            repo_name = repo_url
        
        repo = github_client.get_repo(repo_name)
        if ref:
            content_file = repo.get_contents(file_path, ref=ref)
        else:
            content_file = repo.get_contents(file_path)
        
        return content_file.decoded_content.decode("utf-8")
    except Exception as e:
         return f"Error fetching file content: {e}"


# Initialize the agent
agent = Agent(
    name="repo_agent",
    model="gemini-2.0-flash-exp",
    instruction="You are a Repository Agent. Your job is to fetch data from GitHub repositories. You have access to tools to fetch commits, file contents, and analyze changes. Use them to answer queries about the codebase history and content.",
    tools=[fetch_recent_commits, analyze_code_changes, get_file_content]
)

# Expose as FastAPI app via A2A with correct host/port for agent card
app = to_a2a(agent, host="127.0.0.1", port=8001)

# For ADK Web UI discovery
root_agent = agent

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
