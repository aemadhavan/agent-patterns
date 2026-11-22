"""Pattern 10: Swarm (Multi-Agent Collaboration).

Peer specialist agents collaborate directly on shared context, handing off work
to whichever peer is best placed next without a central manager.
Example: An incident-response swarm where Detection -> Diagnostics -> Remediation
-> Communications hand off directly over a shared incident log.
"""

import sys
from pathlib import Path
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import generate_text


class SwarmState(TypedDict):
    alert: str
    shared_log: list[str]
    next_agent: str
    hops: int


def _handoff(role: str, instruction: str, state: SwarmState, allowed_next: list[str]) -> dict:
    history = "\n".join(state["shared_log"]) or "None yet."
    prompt = (
        f"You are the {role} agent in an incident-response swarm.\n"
        f"Alert: {state['alert']}\n"
        f"Shared incident log:\n{history}\n\n"
        f"Task: {instruction}\n"
        f"End your response with a final line: `HANDOFF: <one of {', '.join(allowed_next)}>`"
    )
    out = generate_text(prompt)
    next_agent = "done"
    for line in reversed(out.splitlines()):
        if line.strip().upper().startswith("HANDOFF:"):
            candidate = line.split(":", 1)[1].strip().lower()
            if candidate in allowed_next:
                next_agent = candidate
            break
    return {
        "shared_log": state["shared_log"] + [f"[{role}]\n{out}"],
        "next_agent": next_agent,
        "hops": state["hops"] + 1,
    }


def detection_agent(state: SwarmState) -> dict:
    return _handoff(
        "Detection",
        "Confirm severity, blast radius, and affected service.",
        state,
        ["diagnostics", "communications"],
    )


def diagnostics_agent(state: SwarmState) -> dict:
    return _handoff(
        "Diagnostics",
        "Identify the most likely root cause from the symptoms and log evidence.",
        state,
        ["remediation", "communications"],
    )


def remediation_agent(state: SwarmState) -> dict:
    return _handoff(
        "Remediation",
        "Propose the immediate mitigation and rollback/fix steps.",
        state,
        ["communications", "done"],
    )


def communications_agent(state: SwarmState) -> dict:
    return _handoff(
        "Communications",
        "Draft a concise, transparent customer status-page update.",
        state,
        ["done"],
    )


def route_peer(state: SwarmState) -> str:
    if state["hops"] >= 5 or state["next_agent"] == "done":
        return END
    return state["next_agent"]


def build_graph():
    graph = StateGraph(SwarmState)
    graph.add_node("detection", detection_agent)
    graph.add_node("diagnostics", diagnostics_agent)
    graph.add_node("remediation", remediation_agent)
    graph.add_node("communications", communications_agent)

    graph.add_edge(START, "detection")
    for node in ("detection", "diagnostics", "remediation", "communications"):
        graph.add_conditional_edges(
            node,
            route_peer,
            {
                "diagnostics": "diagnostics",
                "remediation": "remediation",
                "communications": "communications",
                END: END,
            },
        )
    return graph.compile()


def run(task: str | None = None) -> str:
    alert = task or "P1 Alert: Checkout API 504 latency spiked to 18% error rate after deploy v4.12.3."
    app = build_graph()
    result = app.invoke({"alert": alert, "shared_log": [], "next_agent": "detection", "hops": 0})
    return "\n\n---\n\n".join(result["shared_log"])


if __name__ == "__main__":
    print(run())
