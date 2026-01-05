import urllib.request
import urllib.error
import time
import sys
import json

AGENT_PORTS = {
    "repo_agent": 8001,
    "security_agent": 8002,
    "reviewer_agent": 8003
}

def check_agent(name, port):
    url = f"http://127.0.0.1:{port}/.well-known/agent-card.json"
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            if response.status == 200:
                print(f"✅ {name} is ALIVE at {url}")
                return True
            else:
                print(f"❌ {name} returned status {response.status} at {url}")
                return False
    except urllib.error.URLError as e:
        print(f"❌ {name} is UNREACHABLE at {url}. Error: {e}")
        return False
    except Exception as e:
        print(f"❌ {name} failed with error: {e}")
        return False

def main():
    print("Starting Health Check...")
    results = []
    for name, port in AGENT_PORTS.items():
        results.append(check_agent(name, port))
    
    if all(results):
        print("\nAll agents are running correctly!")
        sys.exit(0)
    else:
        print("\nSome agents failed to respond. Please make sure they are started via start_services.bat")
        sys.exit(1)

if __name__ == "__main__":
    main()
