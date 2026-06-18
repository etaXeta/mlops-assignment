import httpx
import json
import time

def fire_queries():
    questions = [
        {"question": "How many circuits are there in the formula_1 database?", "db": "formula_1"},
        {"question": "What is the coordinates location of the circuits for Australian grand prix?", "db": "formula_1"},
        {"question": "List down Ajax's superpowers.", "db": "superhero"},
        {"question": "How many superheroes have 'Flight' as a superpower?", "db": "superhero"},
        {"question": "What is the NCES identification number for 'Golden Elementary'?", "db": "california_schools"},
        {"question": "Which schools have more than 1000 students enrolled?", "db": "california_schools"},
        {"question": "List the names of all players who played for Manchester United in 2010.", "db": "european_football_2"},
        {"question": "What was the score of the match between Real Madrid and Barcelona in 2015?", "db": "european_football_2"},
        {"question": "Show all card games that use a standard 52-card deck.", "db": "card_games"},
        {"question": "Who is the author of the 'Toxicology' database?", "db": "toxicology"},
    ]
    
    url = "http://localhost:8003/answer"
    
    for i, q in enumerate(questions):
        print(f"[*] Firing query {i+1}: {q['question']}")
        payload = {
            "question": q["question"],
            "db": q["db"],
            "tags": {
                "phase": "4",
                "env": "development",
                "test_run": "initial_langfuse_test",
                "query_index": str(i)
            }
        }
        try:
            # We don't care if it fails because of no real LLM/DB as long as it tries to trace
            resp = httpx.post(url, json=payload, timeout=30.0)
            print(f"    [+] Status: {resp.status_code}")
        except Exception as e:
            print(f"    [!] Error: {e}")
        
        time.sleep(1) # Be nice

if __name__ == "__main__":
    fire_queries()
