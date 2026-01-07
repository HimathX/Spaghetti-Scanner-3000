import streamlit as st
import asyncio
import sys
import os
import logging
from typing import List, Dict, Any
from pathlib import Path

# Fix for "Event loop is closed" error in Streamlit
import nest_asyncio
nest_asyncio.apply()

# Add parent directory to path for imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page Config
st.set_page_config(
    page_title="Codebase Intelligence Agent",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .tool-call {
        background-color: #1e1e1e;
        border-left: 3px solid #4CAF50;
        padding: 0.5rem;
        margin: 0.5rem 0;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .tool-response {
        background-color: #1e1e1e;
        border-left: 3px solid #2196F3;
        padding: 0.5rem;
        margin: 0.5rem 0;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ============ SIDEBAR: CONFIGURATION ============
with st.sidebar:
    st.header("🔐 Configuration")
    
    # API Key input
    api_key = st.text_input(
        "Google API Key",
        type="password",
        help="Your Gemini API Key",
        key="google_api_key_input"
    )
    
    # GitHub Token input
    github_token = st.text_input(
        "GitHub Token",
        type="password",
        help="Your GitHub Personal Access Token",
        key="github_token_input"
    )
    
    # Repository URL input
    repo_url = st.text_input(
        "Repository URL",
        placeholder="https://github.com/username/repo",
        help="The GitHub repository to analyze",
        key="repo_url_input"
    )
    
    st.markdown("---")
    
    # Validation
    all_configured = api_key and github_token and repo_url
    
    if all_configured:
        st.success("✅ All credentials configured!")
    else:
        missing = []
        if not api_key:
            missing.append("Google API Key")
        if not github_token:
            missing.append("GitHub Token")
        if not repo_url:
            missing.append("Repository URL")
        st.warning(f"⚠️ Missing: {', '.join(missing)}")
    
    st.caption("Your credentials are only used for this session and are not stored.")

# ============ SET ENVIRONMENT VARIABLES BEFORE IMPORTS ============
if all_configured:
    os.environ["GOOGLE_API_KEY"] = api_key
    os.environ["GITHUB_TOKEN"] = github_token
    os.environ["GITHUB_REPO_URL"] = repo_url

# ============ MAIN APP ============
st.title("⚡ Codebase Intelligence Agent")
st.caption("Enterprise-Grade Multi-Agent Code Analysis & Refactoring System")

# Create Tabs
tab1, tab2 = st.tabs(["💬 Chat", "📚 User Guide"])

# ============ TAB 1: CHAT INTERFACE ============
with tab1:
    # Initialize Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.subheader("🤖 Chat with Dev Manager")

    if not all_configured:
        st.info("👈 Please enter all credentials in the sidebar to start chatting.")
    else:
        # Lazy import ADK modules only after credentials are set
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        
        # Initialize agent only once per session
        if "agent_initialized" not in st.session_state or not st.session_state.agent_initialized:
            try:
                from dev_manager_agent.agent import agent as dev_manager
                
                st.session_state.session_service = InMemorySessionService()
                
                async def create_session():
                    await st.session_state.session_service.create_session(
                        app_name="streamlit_app",
                        user_id="streamlit_user",
                        session_id="main_session"
                    )
                asyncio.run(create_session())
                
                st.session_state.runner = Runner(
                    agent=dev_manager,
                    app_name="streamlit_app",
                    session_service=st.session_state.session_service
                )
                st.session_state.agent_initialized = True
                st.session_state.types = types
            except Exception as e:
                st.error(f"Failed to initialize agent: {e}")
                st.stop()
        
        # 1. Create a scrollable container for messages
        chat_container = st.container(height=500)
        
        # 2. Render history inside the scrollable container
        with chat_container:
            for msg in st.session_state.messages:
                if msg["type"] == "user":
                    with st.chat_message("user"):
                        st.write(msg["content"])
                elif msg["type"] == "assistant":
                    with st.chat_message("assistant"):
                        st.markdown(msg["content"])
                elif msg["type"] == "tool_call":
                    st.markdown(f'<div class="tool-call">🔧 <b>Tool Called:</b> {msg["content"]}</div>', unsafe_allow_html=True)
                elif msg["type"] == "tool_response":
                    st.markdown(f'<div class="tool-response">📥 <b>Tool Response:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        
        # 3. Keep the input at the bottom of the tab
        if prompt := st.chat_input("Ask the Dev Manager..."):
            # Add user message
            st.session_state.messages.append({"type": "user", "content": prompt})
            
            # Run agent
            async def run_agent(user_prompt: str) -> List[Dict[str, Any]]:
                events = []
                types_module = st.session_state.types
                user_content = types_module.Content(role='user', parts=[types_module.Part(text=user_prompt)])
                
                async for event in st.session_state.runner.run_async(
                    user_id="streamlit_user",
                    session_id="main_session",
                    new_message=user_content
                ):
                    events.append(event)
                return events
            
            with st.spinner("Thinking..."):
                events = asyncio.run(run_agent(prompt))
            
            # Process events
            for event in events:
                # Check for tool calls
                if hasattr(event, 'content') and event.content:
                    for part in event.content.parts:
                        # Function Call
                        if hasattr(part, 'function_call') and part.function_call:
                            fc = part.function_call
                            args_str = ", ".join([f"{k}={v}" for k, v in fc.args.items()]) if fc.args else ""
                            tool_msg = f"{fc.name}({args_str})"
                            st.session_state.messages.append({"type": "tool_call", "content": tool_msg})
                        
                        # Function Response
                        if hasattr(part, 'function_response') and part.function_response:
                            fr = part.function_response
                            response_str = str(fr.response) if hasattr(fr, 'response') else str(fr)
                            st.session_state.messages.append({"type": "tool_response", "content": response_str})
                
                # Final response
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            st.session_state.messages.append({"type": "assistant", "content": part.text})
            
            # Rerun to refresh the chat container with new messages
            st.rerun()

# ============ TAB 2: USER GUIDE ============
with tab2:
    st.header("📖 User Guide")
    
    st.markdown("""
    ### ⚡ How does this work?
    The Codebase Intelligence Agent is a professional multi-agent system designed to help you analyze and refactor codebases.
    
    1.  **Configure**: Enter your credentials in the sidebar.
    2.  **Chat**: Ask the Dev Manager to analyze your repo, find bugs, or suggest improvements.
    3.  **Agents**: The system uses multiple specialized agents (Repo Agent, Reviewer Agent, etc.) to perform tasks.
    
    ---
    
    ### 🔑 How to get Tokens & Keys
    
    #### 1. Google API Key (Gemini)
    You need a Google API Key to power the agents' intelligence.
    *   Go to [Google AI Studio](https://aistudio.google.com/).
    *   Click on **"Get API key"**.
    *   Create a new key or use an existing one.
    
    #### 2. GitHub Personal Access Token
    Required for the agents to read your repository code.
    *   Go to GitHub [Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens).
    *   Select **"Tokens (classic)"** (recommended for simplicity) or Fine-grained tokens.
    *   Click **"Generate new token"**.
    *   **Scopes**: Ensure you select `repo` (Full control of private repositories) or at least `public_repo` for public ones.
    
    ---
    
    ### 🔗 Repository URL
    This is the web URL of the GitHub repository you want to analyze.
    *   Example: `https://github.com/username/my-awesome-project`
    *   Make sure the token you provide has access to this repository.
    """)
