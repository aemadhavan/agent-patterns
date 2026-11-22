"""Pattern 11: Review and Critique (Evaluator-Optimizer).

One agent generates work; a separate critic agent evaluates it against explicit
rubric criteria and sends actionable feedback until approved or max rounds hit.
Example: A proposal writer drafts a client proposal; a critic checks requirements,
budget constraints, and unsupported claims before approving.
"""

import sys
from pathlib import Path
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import generate_text

MAX_ROUNDS = 2


class ReviewState(TypedDict):
    requirements: str
    draft: str
    feedback: str
    approved: bool
    round_num: int


def writer_agent(state: ReviewState) -> dict:
    revision_note = f"\nIncorporate this critic feedback:\n{state['feedback']}" if state["feedback"] else ""
    prompt = (
        f"Draft a concise 150-word client proposal meeting these requirements:\n"
        f"{state['requirements']}{revision_note}"
    )
    return {
        "draft": generate_text(prompt, system="You are a senior solutions consultant."),
        "round_num": state["round_num"] + 1,
    }


def critic_agent(state: ReviewState) -> dict:
    prompt = (
        f"Review this client proposal against the requirements:\n"
        f"REQUIREMENTS:\n{state['requirements']}\n\n"
        f"PROPOSAL:\n{state['draft']}\n\n"
        "Check for: (1) all deliverables covered, (2) budget respected, (3) no unsupported claims. "
        "Start your reply with `APPROVED` if it passes all checks, otherwise `REVISE:` followed by specific fixes."
    )
    critique = generate_text(prompt, system="You are a strict deal-desk proposal reviewer.")
    return {
        "feedback": critique,
        "approved": critique.strip().upper().startswith("APPROVED"),
    }


def decide(state: ReviewState) -> str:
    if state["approved"] or state["round_num"] >= MAX_ROUNDS:
        return END
    return "writer"


def build_graph():
    graph = StateGraph(ReviewState)
    graph.add_node("writer", writer_agent)
    graph.add_node("critic", critic_agent)
    graph.add_edge(START, "writer")
    graph.add_edge("writer", "critic")
    graph.add_conditional_edges("critic", decide, {"writer": "writer", END: END})
    return graph.compile()


def run(task: str | None = None) -> str:
    req = task or (
        "Client: FinCo. Scope: 6-week AI support agent pilot with RAG + human escalation. "
        "Budget cap: $35,000. Must include weekly demos and a security review deliverable."
    )
    app = build_graph()
    result = app.invoke({"requirements": req, "draft": "", "feedback": "", "approved": False, "round_num": 0})
    return f"Approved={result['approved']} (rounds={result['round_num']})\n\n{result['draft']}"


if __name__ == "__main__":
    print(run())
