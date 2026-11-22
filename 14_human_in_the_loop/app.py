"""Pattern 14: Human-in-the-Loop (HITL).

The agent pauses at an explicit checkpoint before taking any costly, irreversible,
or external action, letting a human approve, edit, or reject the work.
Example: A sales outreach agent drafts a personalized prospect email, pauses at
a LangGraph `interrupt_before` checkpoint using MemorySaver, and only "sends"
after explicit human approval.
"""

import sys
from pathlib import Path
from typing import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import generate_text


class OutreachState(TypedDict):
    prospect: str
    draft_email: str
    approved: bool
    delivery_status: str


def draft_outreach(state: OutreachState) -> dict:
    email = generate_text(
        f"Draft a concise, personalized 90-word cold outreach email for:\n{state['prospect']}"
    )
    return {"draft_email": email}


def send_email(state: OutreachState) -> dict:
    if not state["approved"]:
        return {"delivery_status": "CANCELLED — Rejected at human approval gate."}
    return {"delivery_status": f"SENT — Approved by human reviewer.\n\n{state['draft_email']}"}


def build_graph():
    graph = StateGraph(OutreachState)
    graph.add_node("draft_outreach", draft_outreach)
    graph.add_node("send_email", send_email)
    graph.add_edge(START, "draft_outreach")
    graph.add_edge("draft_outreach", "send_email")
    graph.add_edge("send_email", END)
    return graph.compile(checkpointer=MemorySaver(), interrupt_before=["send_email"])


def run(task: str | None = None, auto_approve: bool = True) -> str:
    prospect = task or "Maya Lin, VP Engineering at NovaPay — recently launched a multi-agent support platform."
    app = build_graph()
    config = {"configurable": {"thread_id": "outreach-demo-1"}}

    # Step 1: Run until the human approval checkpoint
    app.invoke(
        {"prospect": prospect, "draft_email": "", "approved": False, "delivery_status": ""},
        config=config,
    )
    snapshot = app.get_state(config)
    draft = snapshot.values["draft_email"]

    # Step 2: Human review checkpoint (interactive in CLI, or auto_approve in benchmarks)
    if auto_approve:
        approved = True
    else:
        print("\n--- HUMAN APPROVAL CHECKPOINT ---")
        print(draft)
        choice = input("\nApprove and send this email? [y/N]: ").strip().lower()
        approved = choice == "y"

    # Step 3: Resume graph after human decision
    app.update_state(config, {"approved": approved})
    final_state = app.invoke(None, config=config)
    return final_state["delivery_status"]


if __name__ == "__main__":
    print(run(auto_approve=False))
