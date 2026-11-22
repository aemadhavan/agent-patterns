"""Pattern 15: Elephant-Goldfish Model (Context-Rich Drafter + Stateless Reviewer).

Inspired by egm.dev (Spec-Driven Development with AI):
- The **Elephant** is a context-rich session that brainstorms, holds architectural
  background, trade-offs, and revision history, and drafts a self-contained spec.
- The **Goldfish** is a completely stateless reviewer that sees ONLY the standalone
  spec document — zero brainstorming context or prior rounds. Because it has no
  memory of how the spec was conceived, it exposes unstated assumptions, missing
  edge cases, and ambiguity.

Example: Designing a rate-limited webhook delivery service before writing code.
"""

import sys
from pathlib import Path
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import generate_text

MAX_ROUNDS = 3

ELEPHANT_SYSTEM = (
    "You are the Elephant — a principal engineer with full project context. "
    "Use all accumulated brainstorming notes and reviewer feedback to produce "
    "a clear, self-contained design specification that a reader with zero prior "
    "context could implement without guessing."
)

GOLDFISH_SYSTEM = (
    "You are the Goldfish — a stateless, cold-read design reviewer with zero "
    "knowledge of any prior conversation or brainstorming. Read ONLY the spec "
    "in front of you and expose unstated assumptions, missing failure modes, "
    "or ambiguous interfaces."
)


class EGMState(TypedDict):
    problem: str
    elephant_history: list[str]
    spec: str
    goldfish_feedback: str
    approved: bool
    round_num: int


def elephant_brainstorm(state: EGMState) -> dict:
    """Elephant explores goals, constraints, and architectural trade-offs."""
    prompt = (
        f"Brainstorm the architecture and key trade-offs for this system:\n"
        f"{state['problem']}\n\n"
        "List: (1) core goals, (2) non-goals, (3) key architectural choices and "
        "why, and (4) tricky edge cases to watch out for."
    )
    notes = generate_text(prompt, system=ELEPHANT_SYSTEM)
    return {
        "elephant_history": [*state["elephant_history"], f"BRAINSTORM:\n{notes}"],
    }


def elephant_draft(state: EGMState) -> dict:
    """Elephant drafts or revises a self-contained spec using full history."""
    history_block = "\n\n---\n\n".join(state["elephant_history"])
    feedback_block = (
        f"\n\nLatest Goldfish cold-read critique to address:\n{state['goldfish_feedback']}"
        if state["goldfish_feedback"]
        else ""
    )
    prompt = (
        f"Problem statement:\n{state['problem']}\n\n"
        f"Accumulated Elephant context:\n{history_block}"
        f"{feedback_block}\n\n"
        "Write a concise, self-contained 200-word technical design spec covering: "
        "Architecture, API/Data Contract, Failure Handling & Retries, and Security. "
        "Do NOT assume the reader saw the brainstorming notes."
    )
    spec = generate_text(prompt, system=ELEPHANT_SYSTEM, max_tokens=2048)
    next_round = state["round_num"] + 1
    return {
        "spec": spec,
        "round_num": next_round,
        "elephant_history": [*state["elephant_history"], f"DRAFT v{next_round}:\n{spec}"],
    }


def goldfish_review(state: EGMState) -> dict:
    """Goldfish reviews ONLY the standalone spec — zero brainstorming history."""
    prompt = (
        "Review this standalone design specification cold (you have no other context):\n\n"
        f"{state['spec']}\n\n"
        "Check for: (1) unstated assumptions, (2) missing failure/retry semantics, "
        "(3) unclear API/security boundaries. "
        "Start your reply with `APPROVED` if it is self-contained and has no blocking gaps, "
        "otherwise start with `REVISE:` followed by the top 3-5 concrete blocking gaps to fix."
    )
    critique = generate_text(prompt, system=GOLDFISH_SYSTEM, max_tokens=2048)
    approved = critique.strip().upper().startswith("APPROVED")
    return {
        "goldfish_feedback": critique,
        "approved": approved,
        "elephant_history": [
            *state["elephant_history"],
            f"GOLDFISH REVIEW v{state['round_num']}:\n{critique}",
        ],
    }


def decide(state: EGMState) -> str:
    if state["approved"] or state["round_num"] >= MAX_ROUNDS:
        return END
    return "elephant_draft"


def build_graph():
    graph = StateGraph(EGMState)
    graph.add_node("elephant_brainstorm", elephant_brainstorm)
    graph.add_node("elephant_draft", elephant_draft)
    graph.add_node("goldfish_review", goldfish_review)

    graph.add_edge(START, "elephant_brainstorm")
    graph.add_edge("elephant_brainstorm", "elephant_draft")
    graph.add_edge("elephant_draft", "goldfish_review")
    graph.add_conditional_edges(
        "goldfish_review",
        decide,
        {"elephant_draft": "elephant_draft", END: END},
    )
    return graph.compile()


def run(task: str | None = None) -> str:
    problem = task or (
        "Design a multi-tenant webhook delivery service that guarantees at-least-once "
        "delivery with exponential backoff, per-tenant rate limits, HMAC payload signing, "
        "and a dead-letter queue for exhausted deliveries."
    )
    app = build_graph()
    result = app.invoke(
        {
            "problem": problem,
            "elephant_history": [],
            "spec": "",
            "goldfish_feedback": "",
            "approved": False,
            "round_num": 0,
        }
    )
    return (
        f"Approved={result['approved']} (rounds={result['round_num']})\n\n"
        f"## Final Spec\n{result['spec']}\n\n"
        f"## Latest Goldfish Review\n{result['goldfish_feedback']}"
    )


if __name__ == "__main__":
    print(run())
