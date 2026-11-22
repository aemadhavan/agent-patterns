import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent


def load_pattern(folder: str):
    path = ROOT / folder / "app.py"
    spec = importlib.util.spec_from_file_location(f"live_{folder}_app", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.live
@pytest.mark.parametrize(
    "prompt,expected_header",
    [
        ("I was double-charged $49 on my November invoice. Can you refund it?", "[Routed -> Billing Agent]"),
        ("My API webhook is returning HTTP 502 timeouts since the v2 deploy.", "[Routed -> Technical Support Agent]"),
        ("I want to cancel my subscription and close my account today.", "[Routed -> Human Retention Flow]"),
    ],
)
def test_07_routing_live_all_three_routes(prompt: str, expected_header: str):
    mod = load_pattern("07_routing")
    output = mod.run(prompt)
    assert output.startswith(expected_header), f"Unexpected routing output:\n{output}"


@pytest.mark.live
def test_14_hitl_live_approve_and_reject(monkeypatch):
    mod = load_pattern("14_human_in_the_loop")

    monkeypatch.setattr("builtins.input", lambda _: "n")
    rejected = mod.run(auto_approve=False)
    assert rejected.startswith("CANCELLED")

    monkeypatch.setattr("builtins.input", lambda _: "y")
    approved = mod.run(auto_approve=False)
    assert approved.startswith("SENT")


@pytest.mark.live
def test_04_sequential_live_preserves_brief_facts():
    mod = load_pattern("04_sequential")
    output = mod.run()
    print("\n--- 04_sequential live output ---\n" + output)
    for token in ("PulseTrace", "December 1, 2026", "40%", "OpenTelemetry", "$99"):
        assert token in output, f"Missing expected fact `{token}` in:\n{output}"
