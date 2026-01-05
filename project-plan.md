# Project Plan - Developer Productivity Suite

This document outlines the step-by-step implementation plan for the Developer Productivity Suite. Following these steps results in a fully functional multi-agent system with four specialized agents communicating via the generic Agent-to-Agent (A2A) protocol to automate code review, security scanning, and developer support.

### 1. Environment Setup

- **Install Tools**: Ensure **Python 3.13+** and **uv** (package manager) are installed.
- **Initialize Project**: Run `uv init` to create the project structure.
- **Install Dependencies**: Add `google-adk[a2a]`, `uvicorn`, `fastapi`, `python-dotenv`, and `PyGithub` (for repository access).
- **Configure Authentication**: Create a `.env` file containing:
  - `GOOGLE_API_KEY` (obtained from Google AI Studio)
  - `GITHUB_TOKEN` (for repository access)
  - `GITHUB_REPO_URL` (target repository URL)

### 2. Project Structure

- **Create Directories**: Set up folders for:
  - `dev_manager_agent` (orchestrator)
  - `repo_agent` (code repository scanner)
  - `reviewer_agent` (code review specialist)
  - `security_agent` (security guardian)
- **Verify Config**: Ensure `pyproject.toml` reflects all installed dependencies and `.env` is properly formatted.

### 3. Implement Repository Agent (The Service)

- **Create Agent Logic**: In `repo_agent/agent.py`, define the `RepositoryAgent`.
- **Implement Tools**:
  - `fetch_recent_commits()` - retrieve latest commits from GitHub
  - `analyze_code_changes()` - parse diff and extract changed files
  - `get_file_content()` - retrieve full file contents for analysis
- **Expose via A2A**: Use `to_a2a` to wrap the agent as a FastAPI application.
- **Web UI Support**: Assign the agent to a `root_agent` variable for ADK Web UI discoverability.
- **Configuration**: Set the agent to run on **port 8001** by default.

### 4. Implement Security Guardian Agent (The Service)

- **Create Agent Logic**: In `security_agent/agent.py`, define the `SecurityGuardian` agent.
- **Implement Tools**:
  - `scan_for_secrets()` - detect hardcoded API keys, passwords, tokens
  - `check_sql_injection_risks()` - identify unsafe SQL patterns
  - `compare_cve_database()` - check dependencies against known vulnerabilities
  - `flag_insecure_patterns()` - detect common security anti-patterns
- **Expose via A2A**: Use `to_a2a` to wrap the agent as a FastAPI application.
- **Web UI Support**: Assign the agent to a `root_agent` variable.
- **Configuration**: Set the agent to run on **port 8002** by default.

### 5. Implement Code Reviewer Agent (The Service)

- **Create Agent Logic**: In `reviewer_agent/agent.py`, define the `CodeReviewer` agent.
- **Implement Tools**:
  - `analyze_code_quality()` - evaluate code structure, readability, maintainability
  - `check_best_practices()` - verify adherence to language-specific standards
  - `suggest_optimizations()` - propose performance improvements
  - `generate_review_comments()` - create actionable feedback
- **Expose via A2A**: Use `to_a2a` to wrap the agent as a FastAPI application.
- **Web UI Support**: Assign the agent to a `root_agent` variable.
- **Configuration**: Set the agent to run on **port 8003** by default.

### 6. Implement Dev Manager Agent (The Orchestrator)

- **Create Agent Logic**: In `dev_manager_agent/agent.py`, define the `DevManager` agent.
- **Connect to Remote Agents**: Configure `RemoteA2aAgent` instances for:
  - `repo_service` pointing to `http://127.0.0.1:8001`
  - `security_service` pointing to `http://127.0.0.1:8002`
  - `reviewer_service` pointing to `http://127.0.0.1:8003`
- **System Prompt**: Instruct DevManager to:
  - Request recent commits from `repo_service`
  - Pass code changes to `security_service` for vulnerability scanning
  - Send code to `reviewer_service` for quality review
  - Aggregate findings and generate summary reports
- **Web UI Support**: Expose `root_agent` in `dev_manager_agent/agent.py`.
- **CLI Runner**: Create `main_agent.py` in the root directory to run DevManager in the terminal.

### 7. Execution & Verification

This system supports two running modes.

**Option A: Command Line Interface (CLI)**

1.  **Start Services**: Run each agent service on its designated port:
    - `uvicorn repo_agent.agent:app --port 8001`
    - `uvicorn security_agent.agent:app --port 8002`
    - `uvicorn reviewer_agent.agent:app --port 8003`
2.  **Run Orchestrator**: Execute `main_agent.py` to trigger DevManager and see A2A interactions in the console.
3.  **Verify Output**: Check terminal for aggregated security and review reports.

**Option B: ADK Web UI**

1.  **Start Services**: Run all three service agents on ports 8001-8003 (see Option A).
2.  **Start UI**: Run `adk web` on **port 9000** (to avoid port conflicts).
3.  **Interact**: Open browser at `http://localhost:9000`, select `dev_manager_agent`, and trigger code analysis workflows.

### 8. Integration with GitHub (Optional)

- **Setup Webhooks**: Configure GitHub repository to send push events to your local service.
- **Auto-Trigger**: DevManager automatically runs analysis on new commits.
- **Post Results**: Generate GitHub PR comments with security and review findings.

### 9. Testing & Validation

- **Unit Tests**: Create tests for each agent's tools (mocking GitHub API calls).
- **Integration Tests**: Verify A2A communication between all agents.
- **Sample Data**: Use test repository with intentional security issues for validation.
