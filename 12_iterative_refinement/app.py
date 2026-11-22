"""Pattern 12: Iterative Refinement (Reflection).

A single agent drafts output, then reflects on its own work from the reader's
perspective and polishes it in successive passes.
Example: A LinkedIn post agent writes a first draft, critiques it as a busy
executive (cutting jargon, front-loading the hook), and produces a sharper final post.
"""

import sys
from pathlib import Path
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import generate_text


class ReflectionState(TypedDict):
    topic: str
    draft: str
    reflection: str
    polished: str


def initial_draft(state: ReflectionState) -> dict:
    return {
        "draft": generate_text(
            f"Write a 130-word LinkedIn post about:\n{state['topic']}"
        )
    }


def self_reflect(state: ReflectionState) -> dict:
    return {
        "reflection": generate_text(
            "Re-read this LinkedIn draft as a busy engineering executive. "
            "List 3 concrete weaknesses (jargon, buried hook, weak closing question):\n\n"
            f"{state['draft']}"
        )
    }


def refine_draft(state: ReflectionState) -> dict:
    return {
        "polished": generate_text(
            "Rewrite the LinkedIn post applying every improvement from your self-reflection. "
            "Return ONLY the final polished post.\n\n"
            f"DRAFT:\n{state['draft']}\n\nREFLECTION:\n{state['reflection']}"
        )
    }


def build_graph():
    graph = StateGraph(ReflectionState)
    graph.add_node("draft", initial_draft)
    graph.add_node("reflect", self_reflect)
    graph.add_node("refine", refine_draft)
    graph.add_edge(START, "draft")
    graph.add_edge("draft", "reflect")
    graph.add_edge("reflect", "refine")
    graph.add_edge("refine", END)
    return graph.compile()


def run(task: str | None = None) -> str:
    topic = task or "Why choosing the right AI agent design pattern matters more than prompt engineering."
    app = build_graph()
    result = app.invoke({"topic": topic, "draft": "", "reflection": "", "polished": ""})
    return result["polished"]


if __name__ == "__main__":
    print(run())
