"""Pattern 07: Routing.

A classifier step inspects the incoming request and routes it to the right
specialist agent or workflow so each specialist stays focused.
Example: A customer service router sends billing questions to the billing
specialist, technical faults to tech support, and cancellations to a human
retention handoff.
"""

import sys
from pathlib import Path
from typing import Literal, TypedDict
from langgraph.graph import END, START, StateGraph

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import generate_text


class RouterState(TypedDict):
    message: str
    route: Literal["billing", "technical", "retention"]
    response: str


def classify_request(state: RouterState) -> dict:
    prompt = (
        "Classify this customer message into exactly one category: "
        "`billing`, `technical`, or `retention` (for cancellation requests).\n"
        f"Message: {state['message']}\n\n"
        "Respond with ONLY the single lowercase category word."
    )
    label = generate_text(prompt).strip().lower()
    if label not in ("billing", "technical", "retention"):
        label = "technical"
    return {"route": label}


def billing_agent(state: RouterState) -> dict:
    reply = generate_text(
        f"As a Billing Specialist, answer this billing inquiry concisely:\n{state['message']}"
    )
    return {"response": f"[Routed -> Billing Agent]\n{reply}"}


def technical_agent(state: RouterState) -> dict:
    reply = generate_text(
        f"As a Technical Support Engineer, troubleshoot this issue concisely:\n{state['message']}"
    )
    return {"response": f"[Routed -> Technical Support Agent]\n{reply}"}


def retention_handoff(state: RouterState) -> dict:
    reply = generate_text(
        f"Draft a warm acknowledgement explaining that a dedicated retention specialist "
        f"will reach out within 2 hours regarding:\n{state['message']}"
    )
    return {"response": f"[Routed -> Human Retention Flow]\n{reply}"}


def route_selector(state: RouterState) -> str:
    return state["route"]


def build_graph():
    graph = StateGraph(RouterState)
    graph.add_node("classify", classify_request)
    graph.add_node("billing", billing_agent)
    graph.add_node("technical", technical_agent)
    graph.add_node("retention", retention_handoff)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        route_selector,
        {"billing": "billing", "technical": "technical", "retention": "retention"},
    )
    graph.add_edge("billing", END)
    graph.add_edge("technical", END)
    graph.add_edge("retention", END)
    return graph.compile()


def run(task: str | None = None) -> str:
    msg = task or "I was double-charged $49 on my November invoice. Can you refund the duplicate charge?"
    app = build_graph()
    result = app.invoke({"message": msg, "route": "technical", "response": ""})
    return result["response"]


if __name__ == "__main__":
    print(run())
