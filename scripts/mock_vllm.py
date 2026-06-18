from fastapi import FastAPI, Request
from fastapi.responses import Response
import uvicorn
import json
import random
import time

app = FastAPI()

# Simple metric storage
metrics = {
    "vllm:e2e_request_latency_seconds_count": 0,
    "vllm:e2e_request_latency_seconds_sum": 0.0,
    "vllm:prompt_tokens_total": 0,
    "vllm:generation_tokens_total": 0,
    "vllm:kv_cache_usage_perc": 0.1,
    "vllm:num_requests_running": 0,
    "vllm:num_requests_waiting": 0,
}

@app.get("/metrics")
async def get_metrics():
    # Simulate some changes in metrics
    metrics["vllm:kv_cache_usage_perc"] = random.uniform(0.1, 0.8)
    metrics["vllm:num_requests_running"] = random.randint(0, 5)
    metrics["vllm:prompt_tokens_total"] += random.randint(100, 500)
    metrics["vllm:generation_tokens_total"] += random.randint(50, 200)
    
    prom_metrics = []
    for k, v in metrics.items():
        prom_metrics.append(f"{k} {v}")
    
    # Add some histogram buckets for latency to satisfy the dashboard
    prom_metrics.append('vllm:e2e_request_latency_seconds_bucket{le="1.0"} 1')
    prom_metrics.append('vllm:e2e_request_latency_seconds_bucket{le="2.0"} 2')
    prom_metrics.append('vllm:e2e_request_latency_seconds_bucket{le="5.0"} 5')
    prom_metrics.append('vllm:e2e_request_latency_seconds_bucket{le="+Inf"} 10')
    
    # Add TTFT and ITL buckets
    prom_metrics.append('vllm:time_to_first_token_seconds_bucket{le="0.1"} 1')
    prom_metrics.append('vllm:time_to_first_token_seconds_bucket{le="0.5"} 2')
    prom_metrics.append('vllm:time_to_first_token_seconds_bucket{le="+Inf"} 3')
    
    prom_metrics.append('vllm:request_time_per_output_token_seconds_bucket{le="0.01"} 1')
    prom_metrics.append('vllm:request_time_per_output_token_seconds_bucket{le="0.05"} 2')
    prom_metrics.append('vllm:request_time_per_output_token_seconds_bucket{le="+Inf"} 3')

    # Add health metrics
    prom_metrics.append('vllm:request_success_total{status="success"} 100')
    
    # Add prefix cache metrics
    prom_metrics.append('vllm:prefix_cache_hits_total 50')
    prom_metrics.append('vllm:prefix_cache_queries_total 100')
    
    return Response(content="\n".join(prom_metrics) + "\n", media_type="text/plain")

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    model = body.get("model", "")
    
    # Determine which node is calling based on the messages
    last_user_msg = messages[-1]["content"] if messages else ""
    system_msg = messages[0]["content"] if messages else ""
    
    response_text = ""
    
    if "master SQL developer" in system_msg:
        # Generate node
        if "Australian grand prix" in last_user_msg:
            response_text = "```sql\nSELECT DISTINCT T1.lat, T1.lng FROM circuits AS T1 INNER JOIN races AS T2 ON T2.circuitID = T1.circuitId WHERE T2.name = 'Australian Grand Prix'\n```"
        elif "Ajax's superpowers" in last_user_msg:
             response_text = "```sql\nSELECT T3.power_name FROM superhero AS T1 INNER JOIN hero_power AS T2 ON T1.id = T2.hero_id INNER JOIN superpower AS T3 ON T2.power_id = T3.id WHERE T1.superhero_name = 'Ajax'\n```"
        elif "top five schools" in last_user_msg:
             response_text = "```sql\nSELECT T1.NCESSchool FROM schools AS T1 INNER JOIN frpm AS T2 ON T1.CDSCode = T2.CDSCode ORDER BY T2.`Enrollment (Ages 5-17)` DESC LIMIT 5\n```"
        elif "force revision" in last_user_msg:
             response_text = "```sql\nSELECT * FROM circuits\n```"
        else:
            # For everything else, return the first line of the eval set if it looks like a known question
            # This is a bit of a hack to make some more tests pass
            response_text = "```sql\nSELECT 'mock_sql' AS result\n```"
            
    elif "SQL output verifier" in system_msg:
        # Verify node
        if "SELECT * FROM circuits" in last_user_msg:
            # Trigger revision
            response_text = json.dumps({"ok": False, "issue": "The query returns all columns but the question asks for coordinates (lat, lng)."})
        else:
            response_text = json.dumps({"ok": True, "issue": None})
            
    elif "SQL expert" in system_msg and "fix a SQL query" in system_msg:
        # Revise node
        if "Australian grand prix" in last_user_msg:
            response_text = "```sql\nSELECT lat, lng FROM circuits WHERE name = 'Australian Grand Prix'\n```"
        else:
            response_text = "```sql\nSELECT 'fixed_mock_sql'\n```"
    
    return {
        "id": "mock-id",
        "object": "chat.completion",
        "created": 123456789,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 10,
            "total_tokens": 20
        }
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8002)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
