# Kage Bunshin Plugin

Multi-AI orchestration tools for Claude Code - health checks, model validation, and environment management.

## Overview

Kage Bunshin (Shadow Clone) provides skills for managing and validating the multi-AI infrastructure used by the LLM Council and other AI orchestration systems.

## Skills

### `/kb-status` - Environment Health Check

Comprehensive health check across all Kage Bunshin infrastructure components.

```bash
# Run via skill
/kb-status

# Or run script directly
python3 ~/.claude/plugins/local/kage-bunshin/skills/kb-status/scripts/health_check.py
```

**Components Checked:**
| Component | Check | Expected |
|-----------|-------|----------|
| API Server | HTTP GET /health | 200 OK |
| PostgreSQL | `psql SELECT 1` | Connection success |
| Ollama | GET /api/tags | Models listed |
| Tailscale | `tailscale status` | Nodes online |

**Output:**
```
KAGE BUNSHIN ENVIRONMENT STATUS
==================================================
Component              Status   Details
--------------------------------------------------
API Server             OK       localhost:8000 responding
PostgreSQL             OK       claude_memory@localhost
Ollama                 OK       4 models: deepseek-r1:32b, deepseek-code...
Tailscale              OK       6 nodes online
--------------------------------------------------
Overall: HEALTHY
```

### `/council` - LLM Council Query

Query 4+ LLMs in parallel and get a synthesized answer.

```bash
# Basic query with streaming
/council "What are the benefits of TypeScript?"

# Or run directly with flags
python3 ~/projects/llm-council/council.py --stream "Your question"

# With peer review (2-stage deliberation)
python3 ~/projects/llm-council/council.py --stream --peer-review "Complex question"

# Disable specialists
python3 ~/projects/llm-council/council.py --stream --no-specialists "Coding question"
```

**Models:**
| Model | Type | Strength |
|-------|------|----------|
| GPT-5.2 | Core | Reasoning, frameworks |
| Claude Sonnet 4.5 | Core | Clarity, synthesis |
| Gemini 3 Pro | Core | Comprehensive analysis |
| Perplexity Sonar | Core | Real-time web search |
| DeepSeek Coder 33B | Specialist | Auto-added for coding |
| DeepSeek R1 32B | Specialist | Auto-added for math |

**Flags:**
- `--stream` - Show responses as they complete
- `--peer-review` - 2-stage deliberation (2x cost)
- `--no-specialists` - Core 4 models only
- `--no-cache` - Fresh results

### `/ollama-smoke-test` - Model Validation

Run coding probes against Ollama models to validate they're working correctly.

```bash
# Test default model (deepseek-coder:33b)
/ollama-smoke-test

# Test specific model
python3 ~/.claude/plugins/local/kage-bunshin/skills/ollama-smoke-test/scripts/smoke_test.py --model qwen2.5:32b

# Test all available models
python3 ~/.claude/plugins/local/kage-bunshin/skills/ollama-smoke-test/scripts/smoke_test.py --all

# Quick test (2 probes only)
python3 ~/.claude/plugins/local/kage-bunshin/skills/ollama-smoke-test/scripts/smoke_test.py --quick
```

**Probes:**
| Probe | Description | Success Criteria |
|-------|-------------|------------------|
| `fibonacci` | Generate fibonacci function | Contains `def`, `return` |
| `palindrome` | Check if string is palindrome | Uses reversal, handles case |
| `fizzbuzz` | Classic FizzBuzz | Loop with modulo logic |
| `json_parse` | Parse JSON and extract field | Uses `json` module |
| `error_explain` | Explain Python error | Identifies the issue |

**Sample Results:**
```
OLLAMA SMOKE TEST RESULTS
==================================================
Model: qwen2.5:32b
Host: http://localhost:11434

Probe              Result   Time     Details
--------------------------------------------------
fibonacci          PASS     20.4s    Function generated correctly
palindrome         PASS      1.2s    Handles case and reversal
fizzbuzz           PASS      2.7s    Loop with modulo logic
json_parse         PASS      1.0s    Uses json.loads()
error_explain      PASS      1.3s    Identified NameError issue
--------------------------------------------------
Summary: 5/5 passed (100%)
Total time: 26.7s
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KB_API_HOST` | `http://localhost:8000` | Kage Bunshin API server |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server |
| `OLLAMA_TIMEOUT` | `60` | Request timeout in seconds |
| `PG_HOST` | `localhost` | PostgreSQL host |
| `PG_DATABASE` | `claude_memory` | Database name |
| `PG_USER` | `claude_mcp` | Database user |

## Infrastructure

Configure your nodes in `skills/kb-status/scripts/health_check.py`:

```python
nodes = [
    ("<GPU_PRIMARY_IP>", "node-gpu-primary"),
    ("<PRIMARY_IP>", "node-primary"),
    ("<SECONDARY_IP>", "node-secondary"),
]
```

### Models Available

| Model | Size | Best For |
|-------|------|----------|
| deepseek-coder:33b | 33B | Code generation, debugging |
| deepseek-r1:32b | 32B | Math, reasoning, proofs |
| qwen2.5:32b | 32B | General coding, fast |
| qwen2.5:3b | 3B | Quick tests, low latency |

## Installation

This plugin is auto-discovered from `~/.claude/plugins/local/kage-bunshin/`.

## Version

- **Plugin Version**: 0.3.0
- **Last Updated**: 2026-01-10
