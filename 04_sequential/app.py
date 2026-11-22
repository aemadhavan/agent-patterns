"""Pattern 04: Sequential (Prompt Chaining).

Steps run in a fixed linear order where the output of one step becomes the input
to the next. Predictable, easy to test, and auditable.
Example: A product launch content pipeline:
  1. Extract key facts from a brief
  2. Draft the launch announcement
  3. Rewrite in brand voice
  4. Fact-check claims against the original brief
"""

import sys
from pathlib import Path
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import generate_text


class PipelineState(TypedDict):
    brief: str
    facts: str
    draft: str
    branded: str
    final_output: str


def extract_facts(state: PipelineState) -> dict:
    facts = generate_text(
        f"Extract the 4 most important factual claims from this product brief as bullets:\n\n{state['brief']}"
    )
    return {"facts": facts}


def draft_article(state: PipelineState) -> dict:
    draft = generate_text(
        f"Write a short 120-word product launch announcement using ONLY these facts:\n\n{state['facts']}"
    )
    return {"draft": draft}


def apply_brand_voice(state: PipelineState) -> dict:
    branded = generate_text(
        f"Rewrite this draft in a crisp, confident, jargon-free engineering brand voice:\n\n{state['draft']}"
    )
    return {"branded": branded}


def check_claims(state: PipelineState) -> dict:
    checked = generate_text(
        f"Compare the final copy against the original brief. Fix any unsupported claims "
        f"and return ONLY the verified final announcement.\n\n"
        f"BRIEF:\n{state['brief']}\n\nCOPY:\n{state['branded']}"
    )
    return {"final_output": checked}


def build_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("extract_facts", extract_facts)
    graph.add_node("draft_article", draft_article)
    graph.add_node("apply_brand_voice", apply_brand_voice)
    graph.add_node("check_claims", check_claims)

    graph.add_edge(START, "extract_facts")
    graph.add_edge("extract_facts", "draft_article")
    graph.add_edge("draft_article", "apply_brand_voice")
    graph.add_edge("apply_brand_voice", "check_claims")
    graph.add_edge("check_claims", END)
    return graph.compile()


def run(task: str | None = None) -> str:
    brief = task or (
        "Product: PulseTrace v2.0. Launch date: December 1, 2026. "
        "Key features: real-time LLM latency alerts, 40% lower trace ingestion overhead, "
        "native OpenTelemetry support. Pricing: starts at $99/month."
    )
    app = build_graph()
    result = app.invoke(
        {"brief": brief, "facts": "", "draft": "", "branded": "", "final_output": ""}
    )
    return result["final_output"]


if __name__ == "__main__":
    print(run())
