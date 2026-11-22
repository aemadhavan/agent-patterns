"""Pattern 06: Loop.

A sequence repeats until an explicit exit condition is met (tests pass or max
attempts reached). The exit condition is the core design safeguard.
Example: A coding agent writes a Python function, runs automated unit tests,
reads any failure output, and retries up to 3 attempts.
"""

import sys
from pathlib import Path
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import generate_text

MAX_ATTEMPTS = 3


class LoopState(TypedDict):
    spec: str
    code: str
    test_error: str
    attempts: int
    passed: bool


def write_code(state: LoopState) -> dict:
    feedback = f"\nPrevious error to fix:\n{state['test_error']}" if state["test_error"] else ""
    prompt = (
        f"Write a Python function named `slugify(text: str) -> str` matching this spec:\n"
        f"{state['spec']}{feedback}\n\n"
        "Return ONLY valid Python code with no markdown fences."
    )
    code = generate_text(prompt).strip().removeprefix("```python").removeprefix("```").removesuffix("```").strip()
    return {"code": code, "attempts": state["attempts"] + 1}


def run_tests(state: LoopState) -> dict:
    namespace: dict = {}
    try:
        exec(state["code"], namespace, namespace)
        fn = namespace["slugify"]
        assert fn("Hello, World!") == "hello-world"
        assert fn("  Agentic   AI 2026! ") == "agentic-ai-2026"
        assert fn("a---b") == "a-b"
        return {"passed": True, "test_error": ""}
    except Exception as exc:
        return {"passed": False, "test_error": f"{type(exc).__name__}: {exc}"}


def should_continue(state: LoopState) -> str:
    if state["passed"] or state["attempts"] >= MAX_ATTEMPTS:
        return END
    return "write_code"


def build_graph():
    graph = StateGraph(LoopState)
    graph.add_node("write_code", write_code)
    graph.add_node("run_tests", run_tests)
    graph.add_edge(START, "write_code")
    graph.add_edge("write_code", "run_tests")
    graph.add_conditional_edges("run_tests", should_continue, {"write_code": "write_code", END: END})
    return graph.compile()


def run(task: str | None = None) -> str:
    spec = task or (
        "Convert a string to lowercase, replace any non-alphanumeric sequence with a single hyphen, "
        "and strip leading/trailing hyphens."
    )
    app = build_graph()
    result = app.invoke({"spec": spec, "code": "", "test_error": "", "attempts": 0, "passed": False})
    status = "PASSED" if result["passed"] else f"FAILED after {result['attempts']} attempts"
    return f"Status: {status} (attempts={result['attempts']})\n\n{result['code']}"


if __name__ == "__main__":
    print(run())
