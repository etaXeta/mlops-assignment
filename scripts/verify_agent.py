import os
import json
import httpx
import time
import subprocess
from pathlib import Path

# Configuration
AGENT_URL = "http://localhost:8001/answer"
MOCK_VLLM_URL = "http://localhost:8002/v1"
EVAL_SET = "evals/eval_set.jsonl"

def start_mock_vllm():
    print("[*] Starting mock vLLM server...")
    return subprocess.Popen(["python", "scripts/mock_vllm.py"])

def start_agent_server():
    print("[*] Starting agent server...")
    env = os.environ.copy()
    env["VLLM_BASE_URL"] = MOCK_VLLM_URL
    return subprocess.Popen(["python", "-m", "uvicorn", "agent.server:app", "--host", "0.0.0.0", "--port", "8001"], env=env)

def test_agent():
    # 1. Start servers
    vllm_proc = start_mock_vllm()
    agent_proc = start_agent_server()
    
    # Wait for servers to be ready
    print("[*] Waiting for servers to start...")
    time.sleep(5)
    
    questions_to_test = [
        # This one should just work
        {"question": "What is the coordinates location of the circuits for Australian grand prix?", "db": "formula_1"},
        # This one will trigger revision because of "force revision" keyword
        {"question": "force revision: what are the coordinates of circuits?", "db": "formula_1"}
    ]

    try:
        for req in questions_to_test:
            print(f"\n[*] Testing question: {req['question']}")
            try:
                # Use a specific question that triggers revision in mock_vllm.py
                # In mock_vllm.py: if "SELECT * FROM circuits" in last_user_msg -> ok: False
                # So we need to get generate_sql to produce "SELECT * FROM circuits"
                # But mock_vllm generate node doesn't produce it for these questions.
                
                # Let's try to find a way to trigger it.
                # If I send "SELECT * FROM circuits" as the question, maybe? No, that's the SQL.
                
                response = httpx.post(AGENT_URL, json=req, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    print(f"[+] Iterations: {data['iterations']}")
                    print(f"[+] SQL: {data['sql']}")
                    print(f"[+] History: {json.dumps(data['history'], indent=2)}")
                else:
                    print(f"[-] Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"[!] Request failed: {e}")

    finally:
        print("\n[*] Shutting down servers...")
        agent_proc.terminate()
        vllm_proc.terminate()

if __name__ == "__main__":
    test_agent()
