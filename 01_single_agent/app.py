"""Pattern 01: Single-Agent System.

One model, one clear system prompt, and a small set of tools handles the whole task.
Example: An internal IT helpdesk agent answers password and VPN questions, searches
the knowledge base, and raises a ticket if it cannot resolve the issue.
"""

import sys
from pathlib import Path
from langchain.agents import create_agent

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import get_llm
from shared.tools import create_it_ticket, search_it_kb

SYSTEM_PROMPT = (
    "You are an internal IT Helpdesk agent. First search the IT knowledge base "
    "to answer VPN or password questions. If the user still has an unresolved "
    "access error (like HTTP 403), raise an IT ticket with a clear summary."
)


def build_agent():
    return create_agent(
        model=get_llm(),
        tools=[search_it_kb, create_it_ticket],
        system_prompt=SYSTEM_PROMPT,
    )


def run(task: str | None = None) -> str:
    query = task or (
        "My GlobalProtect VPN keeps failing with error 403 even after I cleared "
        "my cached credentials. Can you help and open a ticket if needed?"
    )
    agent = build_agent()
    result = agent.invoke({"messages": [("user", query)]})
    return result["messages"][-1].content


if __name__ == "__main__":
    print(run())
