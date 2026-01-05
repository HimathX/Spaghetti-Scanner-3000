# 🍝 Spaghetti Scanner 3000

A multi-agent AI system powered by Google's Agent Development Kit (ADK) for automated code analysis, security scanning, and sprint status report generation.

## Features

- 🤖 **AI-Powered Dev Manager**: Chat with an intelligent orchestrator that coordinates multiple specialized agents
- 📊 **Sprint Status Reports**: Automatically generate reports from recent commits
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

### 1. Install Dependencies
```bash
uv sync
```

### 2. Start Backend Agents
```bash
.\start_all.bat
```
Or manually:
```bash
uv run uvicorn repo_agent.agent:app --port 8001 --reload
uv run uvicorn security_agent.agent:app --port 8002 --reload
uv run uvicorn reviewer_agent.agent:app --port 8003 --reload
```

### 3. Launch Streamlit UI
```bash
uv run streamlit run streamlit_ui/app.py
```

### 4. Configure Credentials
In the sidebar, enter:
- **Google API Key**: Your Gemini API key
- **GitHub Token**: Personal Access Token with repo access
- **Repository URL**: The GitHub repo to analyze

## Usage Examples

**Generate a Sprint Report:**
> "Generate a status report for the last 5 commits"

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
