#!/usr/bin/env python3
"""
Ollama Smoke Test
=================

Validates Ollama models with real coding probes.
"""

import argparse
import json
import os
import re
import time
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import List, Optional, Callable


@dataclass
class ProbeResult:
    name: str
    passed: bool
    duration: float
    details: str
    response: str = ""

    @property
    def icon(self) -> str:
        return "✓" if self.passed else "✗"

    @property
    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"

    @property
    def color(self) -> str:
        return "\033[92m" if self.passed else "\033[91m"


class OllamaSmokeTest:
    def __init__(self, host: str = None, model: str = None, timeout: int = None):
        self.host = host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.model = model or "deepseek-coder:33b"
        self.timeout = timeout or int(os.environ.get("OLLAMA_TIMEOUT", "60"))
        self.host = self.host.rstrip("/")
        self.results: List[ProbeResult] = []

    def generate(self, prompt: str) -> str:
        """Generate completion from Ollama."""
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            result = json.loads(resp.read().decode())
            return result.get("response", "")

    def list_models(self) -> List[str]:
        """List available models."""
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    def run_probe(
        self,
        name: str,
        prompt: str,
        validator: Callable[[str], tuple[bool, str]]
    ) -> ProbeResult:
        """Run a single probe."""
        start = time.time()
        try:
            response = self.generate(prompt)
            duration = time.time() - start
            passed, details = validator(response)
            return ProbeResult(name, passed, duration, details, response)
        except Exception as e:
            duration = time.time() - start
            return ProbeResult(name, False, duration, f"Error: {str(e)[:40]}")

    # === PROBE DEFINITIONS ===

    def probe_fibonacci(self) -> ProbeResult:
        """Test: Generate fibonacci function."""
        prompt = "Write a Python function called fibonacci(n) that returns the nth fibonacci number. Just the code, no explanation."

        def validate(response: str) -> tuple[bool, str]:
            if "def " not in response.lower():
                return False, "No function definition found"
            if "fibonacci" not in response.lower():
                return False, "Function name not found"
            if "return" not in response.lower():
                return False, "No return statement"
            return True, "Function generated correctly"

        return self.run_probe("fibonacci", prompt, validate)

    def probe_palindrome(self) -> ProbeResult:
        """Test: Check if string is palindrome."""
        prompt = "Write a Python function is_palindrome(s) that returns True if string s is a palindrome (ignoring case and spaces). Just the code."

        def validate(response: str) -> tuple[bool, str]:
            if "def " not in response.lower():
                return False, "No function definition found"
            # Check for common palindrome logic
            has_reverse = "[::-1]" in response or "reversed" in response.lower()
            has_lower = ".lower()" in response or "lower" in response
            if has_reverse and has_lower:
                return True, "Handles case and reversal"
            if has_reverse:
                return True, "Uses string reversal"
            return False, "Missing palindrome logic"

        return self.run_probe("palindrome", prompt, validate)

    def probe_fizzbuzz(self) -> ProbeResult:
        """Test: FizzBuzz implementation."""
        prompt = "Write a Python function fizzbuzz(n) that prints FizzBuzz from 1 to n. Just the code."

        def validate(response: str) -> tuple[bool, str]:
            response_lower = response.lower()
            if "def " not in response_lower:
                return False, "No function definition found"
            has_fizz = "fizz" in response_lower
            has_buzz = "buzz" in response_lower
            has_mod = "%" in response
            if has_fizz and has_buzz and has_mod:
                return True, "Loop with modulo logic"
            return False, "Missing FizzBuzz logic"

        return self.run_probe("fizzbuzz", prompt, validate)

    def probe_json_parse(self) -> ProbeResult:
        """Test: Parse JSON and extract field."""
        prompt = 'Write a Python function get_name(json_str) that parses a JSON string and returns the "name" field. Just the code.'

        def validate(response: str) -> tuple[bool, str]:
            if "json" not in response.lower():
                return False, "No json module usage"
            if "load" in response.lower():  # json.loads or json.load
                return True, "Uses json.loads()"
            return False, "Missing JSON parsing"

        return self.run_probe("json_parse", prompt, validate)

    def probe_error_explain(self) -> ProbeResult:
        """Test: Explain a Python error."""
        prompt = """Explain this Python error in one sentence:
```
NameError: name 'x' is not defined
```"""

        def validate(response: str) -> tuple[bool, str]:
            response_lower = response.lower()
            # Check for understanding of NameError
            keywords = ["not defined", "undefined", "doesn't exist", "not exist", "variable", "declared"]
            if any(kw in response_lower for kw in keywords):
                return True, "Identified NameError issue"
            return False, "Did not explain error"

        return self.run_probe("error_explain", prompt, validate)

    def run_all_probes(self, quick: bool = False) -> List[ProbeResult]:
        """Run all probes."""
        probes = [
            self.probe_fibonacci,
            self.probe_palindrome,
        ]
        if not quick:
            probes.extend([
                self.probe_fizzbuzz,
                self.probe_json_parse,
                self.probe_error_explain,
            ])

        self.results = []
        for probe in probes:
            result = probe()
            self.results.append(result)
            # Print progress
            print(f"  {result.color}{result.icon}\033[0m {result.name}: {result.status} ({result.duration:.1f}s)")

        return self.results

    def print_report(self):
        """Print formatted test report."""
        reset = "\033[0m"
        bold = "\033[1m"

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        total_time = sum(r.duration for r in self.results)
        pct = (passed / total * 100) if total > 0 else 0

        print(f"\n{bold}OLLAMA SMOKE TEST RESULTS{reset}")
        print("=" * 50)
        print(f"Model: {self.model}")
        print(f"Host: {self.host}")
        print()
        print(f"{'Probe':<18} {'Result':<8} {'Time':<8} {'Details'}")
        print("-" * 50)

        for r in self.results:
            print(f"{r.name:<18} {r.color}{r.status:<6}{reset} {r.duration:>5.1f}s   {r.details[:30]}")

        print("-" * 50)

        if passed == total:
            print(f"\033[92m{bold}Summary: {passed}/{total} passed (100%){reset}")
        elif passed > 0:
            print(f"\033[93m{bold}Summary: {passed}/{total} passed ({pct:.0f}%){reset}")
        else:
            print(f"\033[91m{bold}Summary: {passed}/{total} passed (0%){reset}")

        print(f"Total time: {total_time:.1f}s")
        print()

        return passed == total


def main():
    parser = argparse.ArgumentParser(description="Ollama Smoke Test")
    parser.add_argument("--model", "-m", help="Model to test (default: deepseek-coder:33b)")
    parser.add_argument("--host", "-H", help="Ollama host URL")
    parser.add_argument("--all", "-a", action="store_true", help="Test all available models")
    parser.add_argument("--quick", "-q", action="store_true", help="Quick test (fewer probes)")
    parser.add_argument("--timeout", "-t", type=int, default=60, help="Request timeout")
    args = parser.parse_args()

    tester = OllamaSmokeTest(
        host=args.host,
        model=args.model,
        timeout=args.timeout
    )

    if args.all:
        models = tester.list_models()
        if not models:
            print("No models found!")
            return 1

        print(f"Testing {len(models)} models...")
        all_passed = True
        for model in models:
            print(f"\n--- Testing {model} ---")
            tester.model = model
            tester.run_all_probes(quick=args.quick)
            if not tester.print_report():
                all_passed = False
        return 0 if all_passed else 1
    else:
        print(f"Running smoke test for {tester.model}...")
        tester.run_all_probes(quick=args.quick)
        passed = tester.print_report()
        return 0 if passed else 1


if __name__ == "__main__":
    exit(main())
