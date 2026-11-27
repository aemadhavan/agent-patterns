"""Pattern 02: ReAct (Reason + Act).

The agent works in a Thought -> Action -> Observation loop, adapting its next
step based on what tools return until the goal is reached.
Example: A support agent investigates a delayed order by checking order status,
seeing a carrier delay, then fetching the live carrier depot update before replying.
"""

import sys
from pathlib import Path
from langchain.agents import create_agent

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import get_llm
from shared.tools import get_carrier_update, get_order_status

SYSTEM_PROMPT = (
    "You are a customer support specialist investigating shipping issues. "
    "Think step by step: first check the order status; if it is delayed with a "
    "carrier tracking ID, fetch the live carrier update before drafting a helpful, "
    "accurate reply with the new ETA."
)


def build_agent():
    return create_agent(
        model=get_llm(),
        tools=[get_order_status, get_carrier_update],
        system_prompt=SYSTEM_PROMPT,
    )


def run(task: str | None = None) -> str:
    query = task or "Where is my order ORD-4821? It was supposed to arrive two days ago."
    agent = build_agent()
    result = agent.invoke({"messages": [("user", query)]})
    return result["messages"][-1].content


if __name__ == "__main__":
    print(run())
