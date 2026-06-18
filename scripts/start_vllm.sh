#!/usr/bin/env bash
#
# Start vLLM with your chosen configuration.
# Reference: https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html

set -euo pipefail

MODEL="Qwen/Qwen3-30B-A3B-Instruct-2507"

# H100 80GB Optimizations for 10 RPS / P95 < 5s
# - max-model-len: 4096 (1.5-3K prompts + headroom)
# - gpu-memory-utilization: 0.90 (slight reduction for stability)
# - enable-chunked-prefill: true (critical for multi-user latency stability)
# - max-num-seqs: 64 (tuned for 30B MoE model to prevent preemption)
# - enable-prefix-caching: true (optimizes agent's repeat schema calls)
# - trust-remote-code: required for Qwen3

exec uv run --with "transformers==4.48.3" python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --host 0.0.0.0 \
    --port 8000 \
    --tensor-parallel-size 1 \
    --trust-remote-code \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.90 \
    --enable-chunked-prefill true \
    --max-num-seqs 256 \
    --enable-prefix-caching \
    --disable-log-requests
