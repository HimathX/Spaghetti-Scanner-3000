@echo off
echo Starting Repo Agent on port 8001...
start "Repo Agent" uv run uvicorn repo_agent.agent:app --port 8001 --reload

echo Starting Security Agent on port 8002...
start "Security Agent" uv run uvicorn security_agent.agent:app --port 8002 --reload

echo Starting Reviewer Agent on port 8003...
start "Reviewer Agent" uv run uvicorn reviewer_agent.agent:app --port 8003 --reload

echo Waiting for services to initialize...
timeout /t 5

echo Starting Dev Manager CLI...
uv run python main_agent.py

pause
