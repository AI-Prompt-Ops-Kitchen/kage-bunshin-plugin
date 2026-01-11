---
name: ollama-smoke-test
description: This skill should be used when the user asks to "test ollama", "smoke test ollama", "validate ollama models", "check if ollama is working", or needs to verify that Ollama models can handle real coding tasks correctly.
version: 0.1.0
---

# Ollama Smoke Test

Run a suite of coding probes against Ollama models to validate they're working correctly.

## Quick Start

```bash
# Test default model (deepseek-coder:33b)
python3 ${CLAUDE_SKILL_DIR}/scripts/smoke_test.py

# Test specific model
python3 ${CLAUDE_SKILL_DIR}/scripts/smoke_test.py --model qwen2.5:3b

# Test all available models
python3 ${CLAUDE_SKILL_DIR}/scripts/smoke_test.py --all

# Quick test (fewer probes)
python3 ${CLAUDE_SKILL_DIR}/scripts/smoke_test.py --quick
```

## Test Probes

The smoke test runs these coding challenges:

| Probe | Description | Success Criteria |
|-------|-------------|------------------|
| `fibonacci` | Generate fibonacci function | Contains `def`, returns correct values |
| `palindrome` | Check if string is palindrome | Contains `def`, handles edge cases |
| `fizzbuzz` | Classic FizzBuzz implementation | Contains loop, Fizz/Buzz logic |
| `json_parse` | Parse JSON and extract field | Uses `json` module correctly |
| `error_explain` | Explain a Python error | Identifies the issue |

## Output Format

```
OLLAMA SMOKE TEST RESULTS
=========================
Model: deepseek-coder:33b
Host: http://100.98.226.75:11434

Probe              Result   Time    Details
-----              ------   ----    -------
fibonacci          PASS     2.3s    Function generated correctly
palindrome         PASS     1.8s    Handles spaces and case
fizzbuzz           PASS     2.1s    Loop with modulo logic
json_parse         PASS     1.5s    Uses json.loads()
error_explain      PASS     1.2s    Identified NameError

Summary: 5/5 passed (100%)
Total time: 8.9s
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://100.98.226.75:11434` | Ollama server URL |
| `OLLAMA_TIMEOUT` | `60` | Request timeout in seconds |
