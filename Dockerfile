FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY dev_manager_agent/ ./dev_manager_agent/
COPY repo_agent/ ./repo_agent/
COPY security_agent/ ./security_agent/
COPY reviewer_agent/ ./reviewer_agent/
COPY streamlit_ui/ ./streamlit_ui/
COPY main_agent.py ./

# Install dependencies
RUN uv sync --frozen

# Expose ports
EXPOSE 8001 8002 8003 8501

# Start script will be used
COPY start.sh ./
RUN chmod +x start.sh

CMD ["./start.sh"]
