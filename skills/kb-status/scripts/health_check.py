#!/usr/bin/env python3
"""
Kage Bunshin Environment Health Check
======================================

Validates all infrastructure components:
- API Server (FastAPI)
- PostgreSQL Database
- Ollama LLM Runtime
- Tailscale Network
"""

import json
import os
import socket
import subprocess
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class HealthResult:
    component: str
    status: str  # OK, WARN, FAIL
    details: str

    @property
    def icon(self) -> str:
        return {"OK": "✓", "WARN": "!", "FAIL": "✗"}.get(self.status, "?")

    @property
    def color(self) -> str:
        return {"OK": "\033[92m", "WARN": "\033[93m", "FAIL": "\033[91m"}.get(self.status, "")


class HealthChecker:
    def __init__(self):
        self.api_host = os.environ.get("KB_API_HOST", "http://localhost:8000")
        self.ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.pg_host = os.environ.get("PG_HOST", "localhost")
        self.pg_database = os.environ.get("PG_DATABASE", "claude_memory")
        self.pg_user = os.environ.get("PG_USER", "claude_mcp")
        self.results: List[HealthResult] = []

    def check_api_server(self) -> HealthResult:
        """Check Kage Bunshin API server."""
        try:
            req = urllib.request.Request(f"{self.api_host}/health", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return HealthResult("API Server", "OK", f"{self.api_host} responding")
                return HealthResult("API Server", "WARN", f"Status {resp.status}")
        except urllib.error.URLError as e:
            return HealthResult("API Server", "FAIL", f"Connection failed: {e.reason}")
        except Exception as e:
            return HealthResult("API Server", "FAIL", str(e))

    def check_postgresql(self) -> HealthResult:
        """Check PostgreSQL database connectivity."""
        try:
            env = os.environ.copy()
            env["PGPASSFILE"] = os.path.expanduser("~/.pgpass")
            result = subprocess.run(
                ["psql", "-h", self.pg_host, "-U", self.pg_user, "-d", self.pg_database,
                 "-c", "SELECT 1", "-t", "-A", "-w"],  # -w = never prompt for password
                capture_output=True,
                timeout=10,
                env=env
            )
            if result.returncode == 0:
                return HealthResult("PostgreSQL", "OK", f"{self.pg_database}@{self.pg_host}")
            return HealthResult("PostgreSQL", "FAIL", result.stderr.decode().strip()[:50])
        except subprocess.TimeoutExpired:
            return HealthResult("PostgreSQL", "FAIL", "Connection timeout")
        except FileNotFoundError:
            return HealthResult("PostgreSQL", "WARN", "psql not in PATH")
        except Exception as e:
            return HealthResult("PostgreSQL", "FAIL", str(e)[:50])

    def check_ollama(self) -> HealthResult:
        """Check Ollama LLM runtime."""
        try:
            req = urllib.request.Request(f"{self.ollama_host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                models = [m["name"] for m in data.get("models", [])]
                if models:
                    return HealthResult("Ollama", "OK", f"{len(models)} models: {', '.join(models[:3])}")
                return HealthResult("Ollama", "WARN", "No models loaded")
        except urllib.error.URLError as e:
            return HealthResult("Ollama", "FAIL", f"Unreachable: {e.reason}")
        except Exception as e:
            return HealthResult("Ollama", "FAIL", str(e)[:50])

    def check_tailscale(self) -> HealthResult:
        """Check Tailscale network status."""
        try:
            result = subprocess.run(
                ["tailscale", "status", "--json"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                data = json.loads(result.stdout.decode())
                peers = data.get("Peer", {})
                online = sum(1 for p in peers.values() if p.get("Online"))
                return HealthResult("Tailscale", "OK", f"{online + 1} nodes online")
            return HealthResult("Tailscale", "FAIL", "Status check failed")
        except FileNotFoundError:
            return HealthResult("Tailscale", "WARN", "tailscale not in PATH")
        except Exception as e:
            return HealthResult("Tailscale", "FAIL", str(e)[:50])

    def check_node_connectivity(self, host: str, name: str) -> HealthResult:
        """Check connectivity to a specific node."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, 22))  # SSH port
            sock.close()
            if result == 0:
                return HealthResult(f"Node: {name}", "OK", f"{host} reachable")
            return HealthResult(f"Node: {name}", "FAIL", f"{host} port 22 closed")
        except socket.timeout:
            return HealthResult(f"Node: {name}", "FAIL", f"{host} timeout")
        except Exception as e:
            return HealthResult(f"Node: {name}", "FAIL", str(e)[:30])

    def run_all_checks(self) -> List[HealthResult]:
        """Run all health checks."""
        self.results = [
            self.check_api_server(),
            self.check_postgresql(),
            self.check_ollama(),
            self.check_tailscale(),
        ]

        # Check key nodes - UPDATE THESE WITH YOUR IPs
        nodes = [
            # ("<GPU_PRIMARY_IP>", "node-gpu-primary"),
            # ("<PRIMARY_IP>", "node-primary"),
            # ("<SECONDARY_IP>", "node-secondary"),
        ]
        for host, name in nodes:
            self.results.append(self.check_node_connectivity(host, name))

        return self.results

    def print_report(self):
        """Print formatted health report."""
        reset = "\033[0m"
        bold = "\033[1m"

        print(f"\n{bold}KAGE BUNSHIN ENVIRONMENT STATUS{reset}")
        print("=" * 50)
        print(f"{'Component':<22} {'Status':<8} {'Details'}")
        print("-" * 50)

        for r in self.results:
            print(f"{r.component:<22} {r.color}{r.icon} {r.status:<5}{reset} {r.details[:40]}")

        print("-" * 50)

        # Overall status
        fails = sum(1 for r in self.results if r.status == "FAIL")
        warns = sum(1 for r in self.results if r.status == "WARN")

        if fails == 0 and warns == 0:
            print(f"\033[92m{bold}Overall: HEALTHY{reset}")
        elif fails == 0:
            print(f"\033[93m{bold}Overall: DEGRADED ({warns} warnings){reset}")
        else:
            print(f"\033[91m{bold}Overall: UNHEALTHY ({fails} failures){reset}")

        print()
        return fails == 0


def main():
    checker = HealthChecker()
    checker.run_all_checks()
    healthy = checker.print_report()
    return 0 if healthy else 1


if __name__ == "__main__":
    exit(main())
