import importlib.util
from pathlib import Path
from unittest.mock import MagicMock
import pytest

ROOT = Path(__file__).resolve().parent.parent

ALL_PATTERNS = [
    "01_single_agent",
    "02_react",
    "03_plan_and_execute",
    "04_sequential",
    "05_parallel",
    "06_loop",
    "07_routing",
    "08_coordinator",
    "09_hierarchical",
    "10_swarm",
    "11_review_and_critique",
    "12_iterative_refinement",
    "13_tool_use_and_rag",
    "14_human_in_the_loop",
    "15_elephant_goldfish",
]


def load_pattern(folder: str):
    path = ROOT / folder / "app.py"
    spec = importlib.util.spec_from_file_location(f"test_{folder}_app", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("folder", ALL_PATTERNS)
def test_all_patterns_expose_run_and_compile(folder: str, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mod = load_pattern(folder)
    assert callable(getattr(mod, "run", None))
    if hasattr(mod, "build_graph"):
        assert mod.build_graph() is not None
    elif hasattr(mod, "build_agent"):
        assert mod.build_agent() is not None


def test_04_sequential_pipeline_order(monkeypatch):
    mod = load_pattern("04_sequential")
    calls = []

    def fake_generate(prompt: str, **kwargs) -> str:
        calls.append(prompt)
        return f"step-{len(calls)}"

    monkeypatch.setattr(mod, "generate_text", fake_generate)
    output = mod.run("Brief: PulseTrace v2.0")
    assert len(calls) == 4
    assert output == "step-4"
    assert "step-1" in calls[1]
    assert "step-2" in calls[2]
    assert "step-3" in calls[3]


def test_06_loop_unit_tests_and_exit_condition():
    mod = load_pattern("06_loop")

    good_code = (
        "import re\n"
        "def slugify(text: str) -> str:\n"
        "    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')\n"
    )
    res_pass = mod.run_tests({"spec": "", "code": good_code, "test_error": "", "attempts": 1, "passed": False})
    assert res_pass["passed"] is True
    assert res_pass["test_error"] == ""

    bad_code = "def slugify(text: str) -> str:\n    return text\n"
    res_fail = mod.run_tests({"spec": "", "code": bad_code, "test_error": "", "attempts": 1, "passed": False})
    assert res_fail["passed"] is False
    assert "AssertionError" in res_fail["test_error"]

    assert mod.should_continue({"passed": True, "attempts": 1}) == "__end__"
    assert mod.should_continue({"passed": False, "attempts": 3}) == "__end__"
    assert mod.should_continue({"passed": False, "attempts": 2}) == "write_code"


@pytest.mark.parametrize(
    "label,expected_header",
    [
        ("billing", "[Routed -> Billing Agent]"),
        ("technical", "[Routed -> Technical Support Agent]"),
        ("retention", "[Routed -> Human Retention Flow]"),
        ("unknown_label", "[Routed -> Technical Support Agent]"),
    ],
)
def test_07_routing_branches_and_fallback(monkeypatch, label: str, expected_header: str):
    mod = load_pattern("07_routing")
    responses = iter([label, "Specialist reply"])
    monkeypatch.setattr(mod, "generate_text", lambda prompt, **kw: next(responses))
    out = mod.run("Test message")
    assert out.startswith(expected_header)
    assert "Specialist reply" in out


def test_14_hitl_approve_and_reject(monkeypatch):
    mod = load_pattern("14_human_in_the_loop")
    monkeypatch.setattr(mod, "generate_text", lambda prompt, **kw: "Hi Maya, quick note...")

    sent = mod.run("Maya Lin", auto_approve=True)
    assert sent.startswith("SENT — Approved by human reviewer.")
    assert "Hi Maya" in sent

    monkeypatch.setattr("builtins.input", lambda _: "n")
    cancelled = mod.run("Maya Lin", auto_approve=False)
    assert cancelled.startswith("CANCELLED — Rejected at human approval gate.")

    monkeypatch.setattr("builtins.input", lambda _: "y")
    approved_cli = mod.run("Maya Lin", auto_approve=False)
    assert approved_cli.startswith("SENT — Approved by human reviewer.")


def test_15_elephant_goldfish_context_isolation(monkeypatch):
    mod = load_pattern("15_elephant_goldfish")
    prompts_seen = []

    def fake_generate(prompt: str, system: str | None = None, **kwargs) -> str:
        prompts_seen.append((system, prompt))
        if system == mod.ELEPHANT_SYSTEM and "Brainstorm" in prompt:
            return "SECRET_BRAINSTORM_NOTE: use Redis streams."
        if system == mod.ELEPHANT_SYSTEM:
            if "missing DLQ retention" in prompt:
                return "Spec v2: includes 14-day DLQ retention and HMAC-SHA256."
            return "Spec v1: webhook delivery with retries."
        # Goldfish cold-read reviewer
        if "v1" in prompt:
            return "REVISE: missing DLQ retention policy."
        return "APPROVED: self-contained and clear."

    monkeypatch.setattr(mod, "generate_text", fake_generate)
    output = mod.run("Design a webhook service")

    assert "Approved=True (rounds=2)" in output
    assert "Spec v2" in output

    # Goldfish prompts must NEVER contain Elephant's brainstorming notes
    goldfish_prompts = [p for sys_p, p in prompts_seen if sys_p == mod.GOLDFISH_SYSTEM]
    assert len(goldfish_prompts) == 2
    for gp in goldfish_prompts:
        assert "SECRET_BRAINSTORM_NOTE" not in gp

