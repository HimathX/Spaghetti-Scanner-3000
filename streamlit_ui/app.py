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
    page_title="Spaghetti Scanner 3000",
    page_icon="🍝",
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
st.title("🍝 Spaghetti Scanner 3000")
st.caption("Your AI-Powered Dev Manager")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# ============ CHAT INTERFACE ============
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
    
    # Display chat history
    for msg in st.session_state.messages:
        if msg["type"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        elif msg["type"] == "assistant":
            with st.chat_message("assistant"):
                st.write(msg["content"])
        elif msg["type"] == "tool_call":
            st.markdown(f'<div class="tool-call">🔧 <b>Tool Called:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        elif msg["type"] == "tool_response":
            st.markdown(f'<div class="tool-response">📥 <b>Tool Response:</b> {msg["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Ask the Dev Manager..."):
        # Add user message
        st.session_state.messages.append({"type": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
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
                        st.markdown(f'<div class="tool-call">🔧 <b>Tool Called:</b> {tool_msg}</div>', unsafe_allow_html=True)
                    
                    # Function Response
                    if hasattr(part, 'function_response') and part.function_response:
                        fr = part.function_response
                        response_str = str(fr.response) if hasattr(fr, 'response') else str(fr)
                        st.session_state.messages.append({"type": "tool_response", "content": response_str})
                        st.markdown(f'<div class="tool-response">📥 <b>Tool Response:</b> {response_str}</div>', unsafe_allow_html=True)
            
            # Final response
            if event.is_final_response() and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        st.session_state.messages.append({"type": "assistant", "content": part.text})
                        with st.chat_message("assistant"):
                            st.write(part.text)
