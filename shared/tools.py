import json
from pathlib import Path
from langchain_core.tools import tool

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json"


def _load_kb() -> dict:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


@tool
def search_it_kb(query: str) -> str:
    """Search the internal IT helpdesk knowledge base for password, VPN, or access guidance."""
    kb = _load_kb()["it_helpdesk"]
    words = [w.lower() for w in query.split() if len(w) > 2]
    matches = [
        f"{item['title']}: {item['content']}"
        for item in kb
        if any(w in item["topic"].lower() or w in item["content"].lower() for w in words)
    ]
    return "\n\n".join(matches) if matches else "No matching IT knowledge base article found."


@tool
def create_it_ticket(summary: str, priority: str = "medium") -> str:
    """Create an IT support ticket when self-service cannot resolve the issue."""
    return json.dumps(
        {
            "ticket_id": "IT-2026-8841",
            "status": "open",
            "priority": priority,
            "summary": summary,
        },
        indent=2,
    )


@tool
def get_order_status(order_id: str) -> str:
    """Look up the current status and carrier tracking ID for a customer order."""
    orders = _load_kb()["orders"]
    order = orders.get(order_id.upper())
    if not order:
        return f"Order {order_id} not found."
    return json.dumps({"order_id": order_id.upper(), **order}, indent=2)


@tool
def get_carrier_update(tracking_id: str) -> str:
    """Fetch the latest live depot and ETA update from the shipping carrier."""
    updates = _load_kb()["carrier_updates"]
    update = updates.get(tracking_id.upper())
    if not update:
        return f"No carrier update found for tracking ID {tracking_id}."
    return json.dumps({"tracking_id": tracking_id.upper(), **update}, indent=2)


@tool
def get_finance_snapshot() -> str:
    """Retrieve current operating cash balance, upcoming payables, and minimum cash buffer."""
    return json.dumps(_load_kb()["finance"], indent=2)


@tool
def search_company_policy(query: str) -> str:
    """Retrieve current company policy documents (RAG) matching the query."""
    policies = _load_kb()["policies"]
    words = [w.lower() for w in query.split() if len(w) > 2]
    matches = [
        f"[{p['id']}] {p['title']} (Effective {p['effective_date']}): {p['content']}"
        for p in policies
        if any(w in p["title"].lower() or w in p["content"].lower() for w in words)
    ]
    return "\n\n".join(matches) if matches else "No matching policy document found."


@tool
def calculate_expression(expression: str) -> str:
    """Safely evaluate a basic arithmetic expression (e.g., '42500 - 14200 - 18000')."""
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return "Error: Only basic arithmetic characters are permitted."
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(round(float(result), 2))
    except Exception as exc:
        return f"Calculation error: {exc}"
