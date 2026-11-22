"""Pattern 08: Coordinator (Orchestrator-Workers).

A central coordinator decomposes a request, delegates subtasks to specialized
workers, tracks progress, and assembles the final result.
Example: A market-research coordinator delegates market sizing, competitor
analysis, and customer interview synthesis to three workers, then merges their
findings into one coherent report.
"""

import sys
from pathlib import Path
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import generate_text


class CoordinatorState(TypedDict):
    topic: str
    sizing_brief: str
    competitor_brief: str
    customer_brief: str
    sizing_result: str
    competitor_result: str
    customer_result: str
    final_report: str


def coordinator_plan(state: CoordinatorState) -> dict:
    topic = state["topic"]
    return {
        "sizing_brief": f"Estimate TAM/SAM/SOM and growth drivers for: {topic}",
        "competitor_brief": f"Identify top 3 competitors and their positioning for: {topic}",
        "customer_brief": f"Synthesize top 3 buyer pain points and objections for: {topic}",
    }


def sizing_worker(state: CoordinatorState) -> dict:
    return {"sizing_result": generate_text(state["sizing_brief"], system="You are a market sizing analyst.")}


def competitor_worker(state: CoordinatorState) -> dict:
    return {"competitor_result": generate_text(state["competitor_brief"], system="You are a competitive intelligence analyst.")}


def customer_worker(state: CoordinatorState) -> dict:
    return {"customer_result": generate_text(state["customer_brief"], system="You are a UX & customer insights researcher.")}


def coordinator_assemble(state: CoordinatorState) -> dict:
    prompt = (
        f"Assemble a cohesive executive market-research report for: {state['topic']}\n\n"
        f"## Market Sizing\n{state['sizing_result']}\n\n"
        f"## Competitors\n{state['competitor_result']}\n\n"
        f"## Customer Insights\n{state['customer_result']}"
    )
    return {"final_report": generate_text(prompt, system="You are a principal research director.")}


def build_graph():
    graph = StateGraph(CoordinatorState)
    graph.add_node("coordinator_plan", coordinator_plan)
    graph.add_node("sizing_worker", sizing_worker)
    graph.add_node("competitor_worker", competitor_worker)
    graph.add_node("customer_worker", customer_worker)
    graph.add_node("coordinator_assemble", coordinator_assemble)

    graph.add_edge(START, "coordinator_plan")
    graph.add_edge("coordinator_plan", "sizing_worker")
    graph.add_edge("coordinator_plan", "competitor_worker")
    graph.add_edge("coordinator_plan", "customer_worker")
    graph.add_edge("sizing_worker", "coordinator_assemble")
    graph.add_edge("competitor_worker", "coordinator_assemble")
    graph.add_edge("customer_worker", "coordinator_assemble")
    graph.add_edge("coordinator_assemble", END)
    return graph.compile()


def run(task: str | None = None) -> str:
    topic = task or "AI code review platforms for mid-market FinTech engineering teams"
    app = build_graph()
    result = app.invoke(
        {
            "topic": topic,
            "sizing_brief": "",
            "competitor_brief": "",
            "customer_brief": "",
            "sizing_result": "",
            "competitor_result": "",
            "customer_result": "",
            "final_report": "",
        }
    )
    return result["final_report"]


if __name__ == "__main__":
    print(run())
