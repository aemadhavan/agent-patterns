"""Pattern 09: Hierarchical Task Decomposition.

Agents are organized in levels: a top-level executive agent breaks a goal into
department sub-goals, mid-level department leads break those into concrete leaf
tasks, and results roll back up.
Example: Enterprise employee onboarding — Top agent owns "Day-1 Readiness";
mid-level IT, HR, and Facilities agents each execute their own leaf checklists.
"""

import sys
from pathlib import Path
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import generate_text


class OnboardingState(TypedDict):
    employee_profile: str
    it_report: str
    hr_report: str
    facilities_report: str
    day1_readiness_summary: str


def _department_lead(dept: str, leaf_tasks: list[str], profile: str) -> str:
    leaf_outputs = []
    for task in leaf_tasks:
        out = generate_text(
            f"Employee: {profile}\nDepartment: {dept}\nComplete this onboarding subtask in 2 concise bullets: {task}"
        )
        leaf_outputs.append(f"- **{task}**: {out.strip()}")
    return f"### {dept} Department\n" + "\n".join(leaf_outputs)


def it_department_node(state: OnboardingState) -> dict:
    return {
        "it_report": _department_lead(
            "IT",
            ["Provision SSO/Okta & GitHub accounts", "Assign laptop & security keys"],
            state["employee_profile"],
        )
    }


def hr_department_node(state: OnboardingState) -> dict:
    return {
        "hr_report": _department_lead(
            "HR",
            ["Finalize employment contract & payroll", "Schedule compliance & orientation"],
            state["employee_profile"],
        )
    }


def facilities_department_node(state: OnboardingState) -> dict:
    return {
        "facilities_report": _department_lead(
            "Facilities",
            ["Issue office access badge", "Reserve workstation & welcome kit"],
            state["employee_profile"],
        )
    }


def top_level_rollup(state: OnboardingState) -> dict:
    prompt = (
        f"You are the Top-Level Onboarding Director. Roll up these department reports into a "
        f"concise Day-1 Readiness Sign-Off for:\n{state['employee_profile']}\n\n"
        f"{state['it_report']}\n\n{state['hr_report']}\n\n{state['facilities_report']}"
    )
    return {"day1_readiness_summary": generate_text(prompt)}


def build_graph():
    graph = StateGraph(OnboardingState)
    graph.add_node("it_lead", it_department_node)
    graph.add_node("hr_lead", hr_department_node)
    graph.add_node("facilities_lead", facilities_department_node)
    graph.add_node("director_rollup", top_level_rollup)

    graph.add_edge(START, "it_lead")
    graph.add_edge(START, "hr_lead")
    graph.add_edge(START, "facilities_lead")
    graph.add_edge("it_lead", "director_rollup")
    graph.add_edge("hr_lead", "director_rollup")
    graph.add_edge("facilities_lead", "director_rollup")
    graph.add_edge("director_rollup", END)
    return graph.compile()


def run(task: str | None = None) -> str:
    profile = task or "Alex Chen — Senior Staff Engineer, Hybrid (Sydney HQ), Start Date: Dec 1, 2026."
    app = build_graph()
    result = app.invoke(
        {
            "employee_profile": profile,
            "it_report": "",
            "hr_report": "",
            "facilities_report": "",
            "day1_readiness_summary": "",
        }
    )
    return result["day1_readiness_summary"]


if __name__ == "__main__":
    print(run())
