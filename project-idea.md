# Developer Productivity Suite

> **Important:** A Google API Key from Google AI Studio and a GitHub Personal Access Token with repo scopes are required.

## 🌟 Overview

This project demonstrates a multi-agent orchestration system designed to automate technical project management. A "Manager" agent coordinates "Worker" agents that synthesize live repository data into actionable reports. It is built using:

- **Google ADK (Agent Development Kit):** To define specialized roles and capabilities.
- **A2A (Agent-to-Agent) Protocol:** To facilitate data transfer between the Repo, Reviewer, and Security Guardian agents.

## 🤖 The Agents (The Development Squad)

The system has four agents that work together to streamline the development workflow:

### 1. Dev Manager (The Orchestrator)

- **Role:** The project lead and report architect.
- **Job:** Receives a command to generate a "Sprint Status Report" and delegates tasks to sub-agents.
- **Superpower:** Synthesizes raw data (commits, code quality, bugs) into a high-level summary.

### 2. Repo Agent (The Data Fetcher)

- **Role:** The GitHub interface.
- **Job:** Connects to repositories to pull recent commit history and metadata.
- **Tool:** Uses `fetch_recent_commits` via the GitHub REST API.

### 3. Reviewer Agent (The Quality Auditor)

- **Role:** The technical critic.
- **Job:** Analyzes commit messages and diffs for clarity, adherence to "Conventional Commits" standards, and potential technical debt.
- **Superpower:** Identifies "risky" commits that lack documentation or contain vague descriptions.

### 4. Security Guardian (The Security Specialist)

- **Role:** The vulnerability gatekeeper.
- **Job:** Scans recent commits for hardcoded secrets (API keys, passwords) and insecure coding patterns (e.g., SQL injection risks).
- **Superpower:** Compares new code against the latest CVE (Common Vulnerabilities and Exposures) databases to flag risky dependencies before they are merged.

## 🔄 How It Works

1. **User Trigger:** "Generate a status report for the main branch of the frontend-app repo."
2. **Manager Delegation:** The Dev Manager asks the Repo Agent for the last 10 commits.
3. **Data Retrieval:** The Repo Agent fetches the commit SHA, author, and messages.
4. **Parallel Analysis:**
   - The Reviewer Agent flags 2 commits for being "Too brief (e.g., 'fixed stuff')".
   - The Security Guardian scans the commits and flags a hardcoded API key in `config.ts` that must be removed before merge.
5. **A2A Consolidation:** All agents send their findings back to the Dev Manager via the A2A protocol.
6. **Final Report:** The Dev Manager outputs a "Sprint Status Report" highlighting progress, quality scores, and urgent bug correlations.

## 🏗️ Why This Architecture?

- **Modular Intelligence:** The "Reviewer Agent" can be upgraded to use a more powerful LLM (like Gemini 2.0 Flash) for deep code analysis without breaking the "Repo Agent."
- **Reduced Context Bloat:** Instead of sending an entire codebase to one LLM, the Manager only receives summarized insights from the specialists.
- **Automated Oversight:** This removes the manual labor of cross-referencing commit logs with Jira or GitHub Issues.

## 🚀 Key Technologies

- **ADK & FastAPI:** To host the agents as microservices.
- **Gemini 1.5/2.0:** For reasoning, sentiment analysis of commit messages, and report generation.
- **GitHub API:** The primary data source for the Repo and Security Guardian agents.
- **Pydantic:** To ensure structured data exchange between agents during the A2A handshake.
