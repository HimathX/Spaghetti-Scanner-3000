import re
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
def scan_for_secrets(code_content: str) -> List[str]:
    """
    Scans the provided code for potential hardcoded secrets (API keys, tokens).
    
    Args:
        code_content: The code to scan.
        
    Returns:
        A list of findings.
    """
    findings = []
    patterns = {
        "Generic API Key": r"(?i)(api_key|apikey|secret_key|access_token)\s*[:=]\s*['\"][a-zA-Z0-9_\-]{20,}['\"]",
        "AWS Access Key": r"AKIA[0-9A-Z]{16}",
        "Private Key": r"-----BEGIN PRIVATE KEY-----"
    }

    for name, pattern in patterns.items():
        if re.search(pattern, code_content):
            findings.append(f"Potential {name} found.")
    
    return findings

def check_sql_injection_risks(code_content: str) -> List[str]:
    """
    Checks for potential SQL injection vulnerabilities.

    Args:
        code_content: The code to scan.

    Returns:
        A list of warnings.
    """
    findings = []
    if re.search(r"(?i)(SELECT|INSERT|UPDATE|DELETE).*(\+|%s|\{\})", code_content):
         findings.append("Potential SQL injection risk: Detected SQL query construction using string concatenation or formatting. Use parameterized queries instead.")
    
    return findings

def compare_cve_database(dependencies: List[str]) -> List[str]:
    """
    Checks a list of dependencies against a mock CVE database.

    Args:
        dependencies: List of dependency strings (e.g., "requests==2.20.0").

    Returns:
         A list of known vulnerabilities.
    """
    known_vulnerabilities = {
        "requests==2.20.0": "CVE-2018-18074: Redirect vulnerability",
        "django==2.0": "CVE-2019-14234: SQL Injection",
        "lodash@4.17.15": "CVE-2020-8203: Prototype Pollution"
    }
    
    findings = []
    for dep in dependencies:
        if dep in known_vulnerabilities:
            findings.append(f"Vulnerability found in {dep}: {known_vulnerabilities[dep]}")
    
    return findings

def flag_insecure_patterns(code_content: str) -> List[str]:
    """
    Flags general insecure coding patterns.
    """
    findings = []
    if "eval(" in code_content:
        findings.append("Avoid using 'eval()'. It is a security risk.")
    if "pickle.load(" in code_content:
        findings.append("Unpickling untrusted data is dangerous.")
    
    return findings


agent = Agent(
    name="security_agent",
    model="gemini-2.0-flash-exp",
    instruction="You are a Security Guardian. Your job is to scan code for vulnerabilities, secrets, and insecure patterns. You are strict and detail-oriented.",
    tools=[scan_for_secrets, check_sql_injection_risks, compare_cve_database, flag_insecure_patterns]
)

app = to_a2a(agent, host="127.0.0.1", port=8002)
root_agent = agent

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
