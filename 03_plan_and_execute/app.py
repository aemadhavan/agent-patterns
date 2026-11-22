"""Pattern 03: Plan-and-Execute.

Separates planning from execution: the agent creates an explicit multi-step plan
first, then executes each step in order and synthesizes the final briefing.
Example: A research agent asked for a competitor briefing plans the steps
(identify competitors, gather pricing, compare features, summarize risks) and
executes them sequentially.
"""

import sys
from pathlib import Path
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import generate_text


class PlanExecuteState(TypedDict):
    task: str
    plan: list[str]
    step_outputs: list[str]
    final_report: str


def planner_node(state: PlanExecuteState) -> dict:
    prompt = (
        f"Create a concise 4-step plan to complete this task:\n{state['task']}\n\n"
        "Return ONLY the 4 numbered steps, one per line."
    )
    raw = generate_text(prompt, system="You are a senior strategy planner.")
    steps = [line.strip() for line in raw.splitlines() if line.strip()][:4]
    return {"plan": steps, "step_outputs": []}


def executor_node(state: PlanExecuteState) -> dict:
    outputs = []
    for step in state["plan"]:
        context = "\n".join(outputs[-2:])
        prompt = (
            f"Overall task: {state['task']}\n"
            f"Prior context:\n{context or 'None'}\n\n"
            f"Execute this step concisely (3-4 bullet points):\n{step}"
        )
        outputs.append(f"### {step}\n{generate_text(prompt)}")
    return {"step_outputs": outputs}


def synthesizer_node(state: PlanExecuteState) -> dict:
    combined = "\n\n".join(state["step_outputs"])
    prompt = (
        f"Synthesize these executed research steps into a crisp executive briefing "
        f"for the request: {state['task']}\n\n{combined}"
    )
    return {"final_report": generate_text(prompt)}


def build_graph():
    graph = StateGraph(PlanExecuteState)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("synthesizer", synthesizer_node)
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "synthesizer")
    graph.add_edge("synthesizer", END)
    return graph.compile()


def run(task: str | None = None) -> str:
    query = task or "Prepare a competitor briefing for a B2B AI observability startup entering the enterprise market."
    app = build_graph()
    result = app.invoke({"task": query, "plan": [], "step_outputs": [], "final_report": ""})
    return result["final_report"]


if __name__ == "__main__":
    print(run())
