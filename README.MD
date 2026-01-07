# 🍝 Spaghetti Scanner 3000

A multi-agent AI system powered by Google's Agent Development Kit (ADK) for automated code analysis, security scanning, and sprint status report generation.

## Features

- 🤖 **AI-Powered Dev Manager**: Chat with an intelligent orchestrator that coordinates multiple specialized agents
- 📂 **GitHub Integration**: Fetch and analyze code from any public or private repository
- 🔒 **Security Scanning**: Detect hardcoded secrets, SQL injection risks, and insecure patterns
- 📝 **Code Review**: Analyze code quality, best practices, and potential optimizations
- 🚀 **Streamlit UI**: Professional web interface with real-time tool call visibility

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│                   (streamlit_ui/app.py)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Dev Manager Agent                        │
│                   (Orchestrator - Port 8000)                 │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Repo Agent    │  │ Security Agent  │  │ Reviewer Agent  │
│   (Port 8001)   │  │   (Port 8002)   │  │   (Port 8003)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Start agents (or run start_all.bat)
uv run uvicorn repo_agent.agent:app --port 8001 --reload &
uv run uvicorn security_agent.agent:app --port 8002 --reload &
uv run uvicorn reviewer_agent.agent:app --port 8003 --reload

# 3. Launch Streamlit UI
uv run streamlit run streamlit_ui/app.py

# OR use ADK Web UI instead (optional)
uv run adk web --port 9000
```

Then configure your credentials in the sidebar:

- Google API Key (Gemini)
- GitHub Token
- Repository URL

## Usage Examples

**Analyze Specific Commit:**

> "What changes were made in the last commit?"

**Security Check:**

> "Scan the latest commit for security vulnerabilities"

## Project Structure

```
Spaghetti-Scanner-3000/
├── dev_manager_agent/     # Orchestrator agent
├── repo_agent/            # GitHub integration
├── security_agent/        # Security scanning
├── reviewer_agent/        # Code quality analysis
├── streamlit_ui/          # Web frontend
│   └── app.py
├── start_all.bat          # Launch script
└── pyproject.toml         # Dependencies
```

## Requirements

- Python 3.10+
- Google API Key (Gemini)
- GitHub Personal Access Token

## License

MIT
