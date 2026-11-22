import json
from shared import llm, tools


def test_search_it_kb_matches_and_misses():
    vpn_res = tools.search_it_kb.invoke({"query": "GlobalProtect VPN error 403"})
    assert "Corporate VPN Troubleshooting" in vpn_res
    assert "VPN-Users" in vpn_res

    pwd_res = tools.search_it_kb.invoke({"query": "password reset"})
    assert "Password Reset Policy" in pwd_res

    miss_res = tools.search_it_kb.invoke({"query": "printer jam"})
    assert "No matching IT knowledge base article found." in miss_res


def test_create_it_ticket():
    raw = tools.create_it_ticket.invoke({"summary": "VPN 403 error", "priority": "high"})
    data = json.loads(raw)
    assert data["ticket_id"] == "IT-2026-8841"
    assert data["status"] == "open"
    assert data["priority"] == "high"
    assert data["summary"] == "VPN 403 error"


def test_order_and_carrier_tools():
    order = json.loads(tools.get_order_status.invoke({"order_id": "ord-4821"}))
    assert order["order_id"] == "ORD-4821"
    assert order["tracking_id"] == "FF-99201"

    assert "not found" in tools.get_order_status.invoke({"order_id": "ORD-0000"}).lower()

    carrier = json.loads(tools.get_carrier_update.invoke({"tracking_id": "ff-99201"}))
    assert carrier["tracking_id"] == "FF-99201"
    assert carrier["new_eta"] == "2026-11-23"

    assert "no carrier update" in tools.get_carrier_update.invoke({"tracking_id": "FF-0000"}).lower()


def test_finance_and_policy_tools():
    fin = json.loads(tools.get_finance_snapshot.invoke({}))
    assert fin["operating_balance_usd"] == 42500.0
    assert fin["minimum_cash_buffer_usd"] == 5000.0

    pol = tools.search_company_policy.invoke({"query": "procurement approval"})
    assert "POL-PROC-2026" in pol

    miss = tools.search_company_policy.invoke({"query": "dress code"})
    assert "No matching policy document found." in miss


def test_calculate_expression_and_safety():
    assert tools.calculate_expression.invoke({"expression": "42500 - 14200 - 18000"}) == "10300.0"
    assert tools.calculate_expression.invoke({"expression": "(10 + 5) / 2"}) == "7.5"
    assert "Error" in tools.calculate_expression.invoke({"expression": "__import__('os').system('echo hi')"})
    assert "Calculation error" in tools.calculate_expression.invoke({"expression": "1 / 0"})


def test_llm_call_counter():
    llm.reset_call_count()
    assert llm.get_call_count() == 0
    llm._increment_call_count()
    llm._increment_call_count()
    assert llm.get_call_count() == 2
    llm.reset_call_count()
    assert llm.get_call_count() == 0
