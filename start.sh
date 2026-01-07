#!/bin/bash

# Start all agent services in background
uv run uvicorn repo_agent.agent:app --host 0.0.0.0 --port 8001 &
sleep 2
uv run uvicorn security_agent.agent:app --host 0.0.0.0 --port 8002 &
sleep 2
uv run uvicorn reviewer_agent.agent:app --host 0.0.0.0 --port 8003 &
sleep 2

# Start Streamlit UI (foreground)
uv run streamlit run streamlit_ui/app.py --server.port 8501 --server.address 0.0.0.0
