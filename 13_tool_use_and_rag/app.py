"""Pattern 13: Tool Use and RAG (The Grounded Agent).

Instead of guessing from parametric memory, the agent retrieves live data and
current policy documents (RAG) and runs deterministic calculations via tools.
Example: A finance assistant asked "Can we afford a $4,800 purchase?" retrieves
current cash balances, upcoming payables, and the 2026 procurement policy, then
calculates remaining cash buffer in code and cites the policy.
"""

import sys
from pathlib import Path
from langgraph.prebuilt import create_react_agent

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import get_llm
from shared.tools import calculate_expression, get_finance_snapshot, search_company_policy

SYSTEM_PROMPT = (
    "You are a grounded finance & policy assistant. Never guess numbers or policy rules. "
    "Always: (1) fetch the live finance snapshot, (2) retrieve the current procurement policy, "
    "(3) use the calculator tool to compute remaining cash after upcoming payables and the "
    "proposed purchase, and (4) cite the policy ID and exact figures in your answer."
)


def build_agent():
    return create_react_agent(
        model=get_llm(),
        tools=[get_finance_snapshot, search_company_policy, calculate_expression],
        prompt=SYSTEM_PROMPT,
    )


def run(task: str | None = None) -> str:
    query = task or "Can we afford a $4,800 annual analytics software purchase today, and whose approval is required?"
    agent = build_agent()
    result = agent.invoke({"messages": [("user", query)]})
    return result["messages"][-1].content


if __name__ == "__main__":
    print(run())
