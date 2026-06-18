import httpx
import json
import sys

def test_question(question, db):
    print(f"\n[*] Testing: {question} (DB: {db})")
    url = "http://localhost:8003/answer"
    payload = {"question": question, "db": db}
    try:
        resp = httpx.post(url, json=payload, timeout=30.0)
        if resp.status_code != 200:
            print(f"[!] Error {resp.status_code}: {resp.text}")
            return
        
        data = resp.json()
        print(f"[+] Iterations: {data['iterations']}")
        print(f"[+] SQL: {data['sql']}")
        if data['ok']:
            print(f"[+] Rows: {len(data['rows'])} returned")
        else:
            print(f"[!] Error: {data['error']}")
        
        for i, step in enumerate(data['history']):
            print(f"    Step {i+1}: {step['node']} - {step.get('issue', 'no issue')}")
            
    except Exception as e:
        print(f"[!] Request failed: {e}")

if __name__ == "__main__":
    # Test cases from eval_set.jsonl
    test_cases = [
        ("What is the coordinates location of the circuits for Australian grand prix?", "formula_1"),
        ("List down Ajax's superpowers.", "superhero"),
        ("List the top five schools, by descending order, from the highest to the lowest, the most number of Enrollment (Ages 5-17). Please give their NCES school identification number.", "california_schools"),
    ]
    for q, db in test_cases:
        test_question(q, db)
