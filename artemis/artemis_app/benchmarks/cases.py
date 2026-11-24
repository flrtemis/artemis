"""Benchmark cases drawn from the AI Revolution video.

Families: terminal-bench, cursor-bench, swiss-sweep, graph-walks.
"""
from .runner import BenchmarkCase, BenchmarkSuite

TERMINAL_BENCH_CASES = [
    BenchmarkCase(
        id="tb-001", name="Implement a REST API endpoint",
        family="terminal-bench",
        prompt="Write a Python Flask endpoint that accepts a JSON payload with 'text' and returns word count. Include error handling and a unit test.",
        checks=[
            {"type": "contains", "name": "has_flask_route", "value": "@app.route", "weight": 1.0},
            {"type": "contains", "name": "has_json_parse", "value": "get_json", "weight": 1.0},
            {"type": "contains", "name": "has_word_count", "value": "split", "weight": 1.0},
            {"type": "contains", "name": "has_error_handling", "value": "try", "weight": 1.0},
        ],
    ),
    BenchmarkCase(
        id="tb-002", name="CLI file batch processor",
        family="terminal-bench",
        prompt="Create a Python CLI script that reads all .txt files in a directory, concatenates them, and writes the result to output.txt. Use argparse.",
        checks=[
            {"type": "contains", "name": "has_argparse", "value": "argparse", "weight": 1.0},
            {"type": "contains", "name": "reads_txt", "value": ".txt", "weight": 1.0},
            {"type": "contains", "name": "writes_output", "value": "output.txt", "weight": 1.0},
        ],
    ),
    BenchmarkCase(
        id="tb-003", name="Database migration helper",
        family="terminal-bench",
        prompt="Write a Python function that safely creates a SQLite table if not exists and inserts a row using parameterized queries.",
        checks=[
            {"type": "contains", "name": "has_sqlite3", "value": "sqlite3", "weight": 1.0},
            {"type": "contains", "name": "create_table", "value": "CREATE TABLE IF NOT EXISTS", "weight": 1.0},
            {"type": "contains", "name": "parameterized_query", "value": "?", "weight": 1.0},
        ],
    ),
    BenchmarkCase(
        id="tb-004", name="Async web scraper skeleton",
        family="terminal-bench",
        prompt="Write an async Python function using httpx to fetch a URL with a timeout and return the status code and body length.",
        checks=[
            {"type": "contains", "name": "has_async", "value": "async", "weight": 1.0},
            {"type": "contains", "name": "has_httpx", "value": "httpx", "weight": 1.0},
            {"type": "contains", "name": "has_timeout", "value": "timeout", "weight": 1.0},
        ],
    ),
]

CURSOR_BENCH_CASES = [
    BenchmarkCase(
        id="cb-001", name="Refactor to use pathlib",
        family="cursor-bench",
        prompt="Refactor this code to use pathlib instead of os.path: import os; path = os.path.join('dir', 'file.txt'); print(os.path.exists(path))",
        checks=[
            {"type": "contains", "name": "uses_pathlib", "value": "pathlib", "weight": 1.0},
            {"type": "contains", "name": "uses_Path", "value": "Path", "weight": 1.0},
            {"type": "not_contains", "name": "no_os_path_join", "value": "os.path.join", "weight": 1.0},
        ],
    ),
    BenchmarkCase(
        id="cb-002", name="Add type hints to function",
        family="cursor-bench",
        prompt="Add type hints to: def greet(name): return 'Hello, ' + name",
        checks=[
            {"type": "contains", "name": "has_type_hint_name", "value": "name: str", "weight": 1.0},
            {"type": "contains", "name": "has_return_type", "value": "-> str", "weight": 1.0},
        ],
    ),
]

SWISS_SWEEP_CASES = [
    BenchmarkCase(
        id="ss-001", name="Multi-hop reasoning: capital of country with largest river",
        family="swiss-sweep",
        prompt="What is the capital city of the country that contains the Amazon River? Answer with just the city name.",
        expected="Brasília",
        checks=[
            {"type": "contains", "name": "mentions_brasilia", "value": "Brasília", "weight": 2.0},
        ],
    ),
    BenchmarkCase(
        id="ss-002", name="Logical deduction: siblings",
        family="swiss-sweep",
        prompt="Alice has 4 sisters. Each sister has 1 brother. How many children are there in total? Answer with just the number.",
        expected="6",
        checks=[
            {"type": "contains", "name": "correct_count", "value": "6", "weight": 2.0},
        ],
    ),
]

GRAPH_WALK_CASES = [
    BenchmarkCase(
        id="gw-001", name="Graph walk: needle in haystack (multi-hop)",
        family="graph-walks",
        prompt=(
            "Find the hidden fact in this text. The text is long with filler. "
            "Hidden fact: the meeting is on Thursday at 3pm in room B. "
            "Ignore everything else. When was the meeting?"
        ),
        expected="Thursday",
        checks=[
            {"type": "contains", "name": "finds_day", "value": "Thursday", "weight": 2.0},
            {"type": "contains", "name": "finds_time", "value": "3pm", "weight": 1.0},
        ],
    ),
]

ALL_CASES = TERMINAL_BENCH_CASES + CURSOR_BENCH_CASES + SWISS_SWEEP_CASES + GRAPH_WALK_CASES


def build_suites() -> list[BenchmarkSuite]:
    return [
        BenchmarkSuite(id="terminal-bench", name="Terminal Bench", cases=TERMINAL_BENCH_CASES),
        BenchmarkSuite(id="cursor-bench", name="Cursor Bench", cases=CURSOR_BENCH_CASES),
        BenchmarkSuite(id="swiss-sweep", name="Swiss Sweep", cases=SWISS_SWEEP_CASES),
        BenchmarkSuite(id="graph-walks", name="Graph Walks", cases=GRAPH_WALK_CASES),
    ]
