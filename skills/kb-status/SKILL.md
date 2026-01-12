---
name: kb-status
description: This skill should be used when the user asks to "check kage bunshin status", "kb status", "check environment health", "verify infrastructure", or needs to quickly validate that all Kage Bunshin components (API server, PostgreSQL, Ollama, Tailscale) are operational.
version: 0.1.0
---

# Kage Bunshin Environment Health Check

Run comprehensive health checks across all Kage Bunshin infrastructure components.

## Quick Start

Run the health check script to get a complete status report:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/health_check.py
```

## Components Checked

### 1. Kage Bunshin API Server
- **Host**: localhost:8000 (or configured API host)
- **Endpoints**: `/health`, `/v1/tasks`
- **Expected**: HTTP 200 response

### 2. PostgreSQL Database
- **Host**: localhost (or configured PG_HOST)
- **Database**: claude_memory
- **Tables**: development_docs, tasks, progress_events

### 3. Ollama LLM Runtime
- **Host**: localhost:11434 (or configured OLLAMA_HOST)
- **Expected Models**: deepseek-coder:33b, deepseek-r1:32b, qwen2.5:32b

### 4. Tailscale Network
- **Nodes**: Configured in health_check.py
- **Check**: Ping connectivity between nodes

## Manual Checks

If the script isn't available, run these commands:

```bash
# API Server
curl -s http://localhost:8000/health

# PostgreSQL
psql -h localhost -U postgres -d claude_memory -c "SELECT 1"

# Ollama
curl -s http://localhost:11434/api/tags | python3 -c "import json,sys; print(json.load(sys.stdin)['models'])"

# Tailscale
tailscale status
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KB_API_HOST` | `http://localhost:8000` | Kage Bunshin API server |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server |
| `PG_HOST` | `localhost` | PostgreSQL host |
| `PG_DATABASE` | `claude_memory` | Database name |

## Output Format

The health check outputs a table with status for each component:

```
KAGE BUNSHIN ENVIRONMENT STATUS
================================
Component          Status    Details
---------          ------    -------
API Server         OK        localhost:8000 responding
PostgreSQL         OK        claude_memory connected
Ollama             OK        4 models available
Tailscale          OK        3 nodes online

Overall: HEALTHY
```
