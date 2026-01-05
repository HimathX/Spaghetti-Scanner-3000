# ADK Web UI Instructions

## Running the ADK Web UI

The ADK Web UI provides a graphical interface to interact with your agents.

### Steps:

1. **Start all agent services** (in separate terminals):
   ```bash
   # Terminal 1 - Repo Agent
   uv run uvicorn repo_agent.agent:app --port 8001 --reload
   
   # Terminal 2 - Security Agent
   uv run uvicorn security_agent.agent:app --port 8002 --reload
   
   # Terminal 3 - Reviewer Agent
   uv run uvicorn reviewer_agent.agent:app --port 8003 --reload
   ```

2. **Start the ADK Web UI** (in a 4th terminal):
   ```bash
   uv run adk web --port 9000
   ```
   
   Note: We use port 9000 to avoid conflicts with the agent services.

3. **Access the Web UI**:
   - Open your browser to: `http://localhost:9000`
   - Select the `dev_manager_agent` from the dropdown
   - Start chatting with the agent!

### Alternative: Use the provided script

Run the batch file that starts everything:
```bash
.\start_services.bat
```

Then in a separate terminal:
```bash
uv run adk web --port 9000
```
