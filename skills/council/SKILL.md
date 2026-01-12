---
name: council
description: This skill should be used when the user asks to "run council", "ask the council", "query llm council", "get multi-model opinion", or wants to query multiple LLMs (GPT, Claude, Gemini, Perplexity) in parallel and get a synthesized answer.
version: 0.1.0
---

# LLM Council

Query 4+ LLMs in parallel and synthesize their responses into a comprehensive answer.

## Quick Start

```bash
# Basic query (streaming enabled by default)
python3 ~/projects/llm-council/council.py --stream "Your question here"

# With peer review (2-stage deliberation, 2x cost)
python3 ~/projects/llm-council/council.py --stream --peer-review "Complex question"

# Disable specialists (core 4 models only)
python3 ~/projects/llm-council/council.py --stream --no-specialists "Coding question"

# Fresh results (skip cache)
python3 ~/projects/llm-council/council.py --stream --no-cache "Latest news"
```

## Models

### Core Council (Always Queried)
| Model | Strength |
|-------|----------|
| GPT-5.2 | Reasoning, frameworks |
| Claude Sonnet 4.5 | Clarity, synthesis |
| Gemini 3 Pro | Comprehensive analysis |
| Perplexity Sonar | Real-time web search |

### Specialists (Auto-Added)
| Model | Trigger |
|-------|---------|
| DeepSeek Coder 33B | Coding keywords (implement, function, python, debug) |
| DeepSeek R1 32B | Math keywords (integral, derivative, prove, solve) |

## Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--stream` | `-s` | Show responses as they complete |
| `--peer-review` | `-p` | 2-stage deliberation (2x cost) |
| `--no-specialists` | | Disable auto specialist routing |
| `--no-cache` | | Skip cache, get fresh results |
| `--governed` | `-g` | Enable circuit breakers |

## Output

Results are:
1. Displayed in terminal with model timing
2. Saved to `/tmp/council_result.json`
3. Stored in PostgreSQL `council_results` table

## Cost Estimates

| Mode | Models | Typical Cost |
|------|--------|--------------|
| Standard | 4 | ~$0.03-0.05 |
| With Specialist | 5 | ~$0.03-0.05 |
| Peer Review | 4 | ~$0.10-0.15 |

## Examples

### Coding Question (auto-includes DeepSeek Coder)
```bash
python3 ~/projects/llm-council/council.py --stream "Write a Python function to find the longest palindromic substring"
```

### Math Question (auto-includes DeepSeek R1)
```bash
python3 ~/projects/llm-council/council.py --stream "Solve the integral of x^2 * e^x dx"
```

### Architecture Decision (peer review recommended)
```bash
python3 ~/projects/llm-council/council.py --stream --peer-review "What are the trade-offs between microservices and monolithic architectures?"
```

### Quick General Question
```bash
python3 ~/projects/llm-council/council.py --stream --no-specialists "What are 3 benefits of remote work?"
```

## History & Search

```bash
# View recent queries
python3 ~/projects/llm-council/council.py --history

# Search past queries
python3 ~/projects/llm-council/council.py --search "TypeScript"
```
