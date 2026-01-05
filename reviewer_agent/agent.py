import logging
from typing import List, Dict, Any

from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Define tools as standalone functions
def analyze_code_quality(code_content: str) -> Dict[str, Any]:
    """
    Analyzes code structure and complexity metrics.
    
    Args:
        code_content: The code to analyze.
        
    Returns:
        Dictionary with quality metrics.
    """
    lines = code_content.splitlines()
    num_lines = len(lines)
    num_functions = sum(1 for line in lines if line.strip().startswith("def ") or line.strip().startswith("function "))
    
    max_indent = 0
    for line in lines:
        indent = len(line) - len(line.lstrip())
        max_indent = max(max_indent, indent)
        
    return {
        "loc": num_lines,
        "function_count": num_functions,
        "max_indentation_depth": max_indent,
        "rating": "Low" if max_indent > 20 else "Good"
    }

def check_best_practices(code_content: str) -> List[str]:
    """
    Checks for adherence to standard coding practices.
    """
    issues = []
    if "print(" in code_content:
        issues.append("Avoid 'print()' in production code; use logging instead.")
    
    if "TODO" in code_content:
        issues.append("Found TODO comments. Ensure these are tracked.")
        
    if "except Exception:" in code_content or "except:" in code_content:
         issues.append("Avoid bare except clauses or catching generic Exception.")

    return issues

def suggest_optimizations(code_content: str) -> List[str]:
    """
    Proposes potential performance optimizations.
    """
    suggestions = []
    lines = code_content.splitlines()
    for i, line in enumerate(lines):
         if "for " in line and any("for " in l for l in lines[i+1:i+3] if (len(l) - len(l.lstrip())) > (len(line) - len(line.lstrip()))):
             suggestions.append(f"Potential nested loop detected around line {i+1}. Consider optimizing O(N^2) operations.")
             break
    
    return suggestions


agent = Agent(
    name="reviewer_agent",
    model="gemini-2.0-flash-exp",
    instruction="You are a Code Reviewer. Analyze the code for quality, best practices, and readability. Use your tools to gather metrics, but rely on your own knowledge for high-level advice.",
    tools=[analyze_code_quality, check_best_practices, suggest_optimizations]
)

app = to_a2a(agent)
root_agent = agent

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)
