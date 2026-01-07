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
    Analyzes code structure and complexity metrics in a single pass.
    
    Args:
        code_content: The code to analyze.
        
    Returns:
        Dictionary with quality metrics.
    """
    lines = code_content.splitlines()
    num_lines = len(lines)
    
    num_functions = 0
    max_indent = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        if stripped.startswith("def ") or stripped.startswith("function "):
            num_functions += 1
            
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
         # Check for nested loops more robustly
         stripped = line.strip()
         if stripped.startswith("for ") or stripped.startswith("while "):
             indent_level = len(line) - len(line.lstrip())
             # Look ahead for immediate nested loop
             if i + 1 < len(lines):
                 next_line = lines[i+1]
                 next_stripped = next_line.strip()
                 next_indent = len(next_line) - len(next_line.lstrip())
                 if (next_stripped.startswith("for ") or next_stripped.startswith("while ")) and next_indent > indent_level:
                     suggestions.append(f"Potential nested loop detected around line {i+1}. Consider optimizing O(N^2) operations.")
    
    return suggestions


agent = Agent(
    name="reviewer_agent",
    model="gemini-2.0-flash",
    instruction="You are a Code Reviewer. Analyze the code for quality, best practices, and readability. Use your tools to gather metrics, but rely on your own knowledge for high-level advice.",
    tools=[analyze_code_quality, check_best_practices, suggest_optimizations]
)

app = to_a2a(agent, host="127.0.0.1", port=8003)
root_agent = agent

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)
