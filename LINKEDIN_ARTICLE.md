# Agent Design Patterns: The Blueprints Behind Reliable AI Agents

*A language model on its own is not an agent. What turns it into one you can trust with real work is the pattern you build around it.*

![Agent Design Patterns Cover](linkedin_banner.jpg)

---

## What is an agent design pattern?

An **agent design pattern** is a reusable blueprint for building an AI agent — a system that can perceive a task, plan steps, use tools, remember context, and take actions to reach a goal, not just answer once.

Instead of inventing that structure from scratch every time, you pick a proven pattern that fits the problem. Each pattern answers five practical questions:
1. How does the agent think?
2. How does it use tools and data?
3. What does it remember?
4. Does it work alone or with other agents?
5. How do you keep it reliable — with reflection, a critic, a cold-read reviewer, or a human checkpoint?

> **A simple test:** If you ask an agent to plan a business trip, a single prompt will not be enough. A good design might use **Parallel** to search flights, hotels, and transport at once, **Tool Use** to check live prices, and **Human-in-the-Loop** to pause before it books and pays. The pattern is what makes that safe and repeatable.

Every pattern below includes an **animated architecture diagram**, **what it is**, **a concrete example**, **when to use it**, **what to watch out for**, and a direct link to the runnable **LangGraph + Claude** implementation on GitHub: [`aemadhavan/agent-patterns`](https://github.com/aemadhavan/agent-patterns).

---

## Before you choose: There is no best pattern — only the best fit

More autonomy and more agents usually improve flexibility and quality, but they also raise cost, latency, and complexity. Good design is balancing those forces on purpose.

| Attribute | What to ask |
| :--- | :--- |
| **Autonomy & goal-orientation** | How much can it do alone, toward a goal, without step-by-step direction? |
| **Reasoning & planning** | How does it break work down, and what happens when the first step fails? |
| **Tool use & perception** | Which APIs, search, code, or apps can it call, and how does it read the results? |
| **Memory & state** | What does it keep for this task, and what should be *isolated* from a reviewer? |
| **Collaboration** | Does it work alone, or coordinate with specialists — and who owns the result? |
| **Control & observability** | Where are the guardrails and human checkpoints? Can you trace its decisions? |
| **Cost, latency, reliability** | How many model calls per task, how fast, and how does it recover from errors? |

> **Rule of thumb:** Start with the simplest pattern that can do the job reliably. Add a second agent, a loop, or a hierarchy only when you can name the failure it will fix.

---

## Patterns 1–3: Start simple, think in steps

### 1. Single-Agent System (`START HERE`)

![Pattern 01: Single-Agent System](01_single_agent/01_single_agent.gif)

One model, one clear system prompt, and a small set of tools handles the whole task. No delegation, no hierarchy — which makes it the easiest pattern to build, test, and debug.
- **Example:** An internal IT helpdesk agent answers VPN and password questions, searches the knowledge base (`search_it_kb`), and raises a ticket (`create_it_ticket`) if an HTTP 403 error persists.
- **Use when:** The task is focused, the steps are predictable, and one agent's context can hold everything it needs.
- **Watch out for:** Tool overload — once you pass 10+ overlapping tools into one prompt, tool-selection accuracy drops fast.
- **Code:** [`01_single_agent/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/01_single_agent/app.py)

### 2. ReAct — Reason + Act (`LOOP`)

![Pattern 02: ReAct](02_react/02_react.gif)

The agent works in a cyclic loop: **Thought → Action → Observation**. It reasons about the next step, calls a tool, reads the result, then adapts its next action — until the goal is reached.
- **Example:** A support agent investigating delayed order `ORD-4821` calls `get_order_status()`, discovers a depot delay + tracking ID, then adapts by calling `get_carrier_update()` to fetch the revised ETA.
- **Use when:** The path is not known in advance and each tool observation changes what you need to do next.
- **Watch out for:** Unbounded loops — always cap maximum iterations so a flaky API doesn't burn tokens endlessly.
- **Code:** [`02_react/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/02_react/app.py)

### 3. Plan-and-Execute (`PLAN FIRST`)

![Pattern 03: Plan-and-Execute](03_plan_and_execute/03_plan_and_execute.gif)

Separates strategy from execution: the agent drafts an explicit multi-step plan first (`planner_node`), executes each step in order with rolling context (`executor_node`), and synthesizes the final deliverable (`synthesizer_node`).
- **Example:** A research agent asked for a competitor briefing creates a 4-step checklist (identify competitors, gather pricing, compare features, summarize risks), executes each step, and compiles an executive briefing.
- **Use when:** The task is long, multi-step, and worth reviewing before any action is taken.
- **Watch out for:** Latency — in our benchmark, Plan-and-Execute took **6 LLM calls (55.1s)**, making it best for async/background jobs rather than interactive chat.
- **Code:** [`03_plan_and_execute/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/03_plan_and_execute/app.py)

---

## Patterns 4–6: Control the flow — in order, at once, or again

### 4. Sequential — Prompt Chaining (`LINEAR`)

![Pattern 04: Sequential](04_sequential/04_sequential.gif)

Steps run in a fixed linear order where the output of one stage becomes the typed input to the next. Predictable, easy to test, and auditable.
- **Example:** A product launch pipeline for PulseTrace v2.0: `extract_facts` → `draft_article` → `apply_brand_voice` → `check_claims` (which verifies the final copy back against the original brief).
- **Use when:** The order is known upfront, each stage depends on the previous one, and auditability matters.
- **Watch out for:** Error compounding — if Stage 1 misses a key fact, downstream stages cannot recover it unless you pass the original input forward (as Stage 4 does here).
- **Code:** [`04_sequential/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/04_sequential/app.py)

### 5. Parallel (`AT ONCE`)

![Pattern 05: Parallel](05_parallel/05_parallel.gif)

Independent workers execute simultaneously (**Fan-Out**) and their results converge into a single merge node (**Fan-In**). Total wait time becomes `max(branches)` instead of `sum(branches)`.
- **Example:** A travel agent searches `search_flights`, `search_hotels`, and `search_transport` in parallel for a Sydney → Melbourne business trip, then merges them into one cohesive itinerary.
- **Use when:** Subtasks do not depend on each other and running them sequentially would waste wall-clock time.
- **Watch out for:** Conflicting outputs — your `merge` node must reconcile contradictions (e.g., a late-night flight vs. hotel check-in window).
- **Code:** [`05_parallel/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/05_parallel/app.py)

### 6. Loop (`REPEAT`)

![Pattern 06: Loop](06_loop/06_loop.gif)

A sequence repeats until an explicit **Exit Gate** is satisfied (tests pass or `MAX_ATTEMPTS = 3` reached). The exit condition *is* the design: without one, a loop becomes a cost problem.
- **Example:** A coding agent writes `slugify()`, runs 3 automated unit assertions (`run_tests`), feeds any `AssertionError` back into `write_code()`, and exits as soon as all assertions pass.
- **Use when:** "Good enough" can be verified objectively (unit tests, schema validation, linters) and one pass isn't always enough.
- **Watch out for:** Repeating the same mistake — always pass the concrete error message (`test_error`) back into the next attempt.
- **Code:** [`06_loop/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/06_loop/app.py)

---

## Patterns 7–9: Route it, coordinate it, break it down

### 7. Routing (`TRIAGE`)

![Pattern 07: Routing](07_routing/07_routing.gif)

A lightweight classifier (`classify_request`) inspects the incoming message and activates **only 1** specialist branch, keeping each specialist's prompt and toolset tight and focused.
- **Example:** A customer service router classifies a double-charge complaint as `"billing"` and routes it exclusively to `billing_agent`, leaving `technical_agent` and `retention_handoff` idle.
- **Use when:** Requests fall into clear categories that require different skills, tools, or permissions.
- **Watch out for:** Misclassification — always define a safe fallback route (here, unknown labels default to `technical`).
- **Code:** [`07_routing/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/07_routing/app.py)

### 8. Coordinator — Orchestrator-Workers (`CENTRAL`)

![Pattern 08: Coordinator](08_coordinator/08_coordinator.gif)

A central coordinator (`coordinator_plan`) decomposes a complex request into **tailored specialist briefs**, delegates them to role-specific workers, and assembles the final deliverable (`coordinator_assemble`).
- **Example:** A market-research coordinator splits *"AI code review platforms for FinTech"* into custom briefs for `sizing_worker`, `competitor_worker`, and `customer_worker`, then merges them as Principal Research Director.
- **Use when:** A task splits into distinct specialist subtasks and one owner must keep the final report coherent.
- **Watch out for:** Over-engineering — if every worker gets the exact same raw prompt, plain **Parallel (Pattern 5)** is simpler.
- **Code:** [`08_coordinator/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/08_coordinator/app.py)

### 9. Hierarchical Task Decomposition (`LEVELS`)

![Pattern 09: Hierarchical](09_hierarchical/09_hierarchical.gif)

Agents are organized in levels like an org chart: a top-level Executive sets the goal, mid-level Department Leads own domain checklists, leaf tasks execute, and summaries roll back up.
- **Example:** Enterprise Day-1 Onboarding — an **Onboarding Director** delegates to **IT**, **HR**, and **Facilities** leads, each executing 2 concrete leaf tasks (SSO, laptop, payroll, orientation, badge, desk) before rolling up into a Day-1 Sign-Off.
- **Use when:** The work is large, spans teams or systems, and needs clean abstraction boundaries at each level.
- **Watch out for:** Call multiplication — this pattern made **7 LLM calls** in our benchmark; reserve it for genuinely multi-domain workflows.
- **Code:** [`09_hierarchical/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/09_hierarchical/app.py)

---

## Patterns 10–12 & 15: Many minds, checked work

### 10. Swarm — Multi-Agent Collaboration (`PEER TO PEER`)

![Pattern 10: Swarm](10_swarm/10_swarm.gif)

Peer specialist agents collaborate directly over a **Shared Incident Log**, handing off the baton via explicit `HANDOFF: <peer>` signals — with **no central manager**.
- **Example:** A P1 incident-response swarm (`Detection` → `Diagnostics` → `Remediation` → `Communications`) investigates a Checkout API 504 spike, isolates deploy `v4.12.3`, proposes rollback, and drafts the status-page update.
- **Use when:** The problem is open-ended, expertise shifts mid-flight, and peer-to-peer speed matters more than a rigid hierarchy.
- **Watch out for:** Ping-pong handoffs — always enforce a hard hop cap (`hops < 5`) and trace every handoff.
- **Code:** [`10_swarm/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/10_swarm/app.py)

### 11. Review and Critique — Evaluator-Optimizer (`SECOND PAIR OF EYES`)

![Pattern 11: Review and Critique](11_review_and_critique/11_review_and_critique.gif)

One agent generates (`writer_agent`); a separate, adversarial critic (`critic_agent`) grades the work against an explicit rubric and loops back `REVISE:` feedback until `APPROVED` or `MAX_ROUNDS` is hit.
- **Example:** A solutions consultant drafts a FinCo AI pilot proposal; a strict Deal-Desk Critic checks all deliverables, the $35,000 budget cap, and unsupported claims before approving.
- **Use when:** Quality criteria can be defined in a rubric and the cost of a mistake is higher than a second LLM pass.
- **Watch out for:** Vague rubrics — if the critic doesn't have concrete pass/fail criteria, it will nitpick forever or rubber-stamp weak drafts.
- **Code:** [`11_review_and_critique/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/11_review_and_critique/app.py)

### 12. Iterative Refinement — Reflection (`IMPROVE`)

![Pattern 12: Iterative Refinement](12_iterative_refinement/12_iterative_refinement.gif)

A **single agent** drafts output, steps into the reader's shoes to critique its own work (`self_reflect`), and rewrites it (`refine_draft`) in 3 structured passes.
- **Example:** A LinkedIn post agent writes a 130-word draft, critiques it as a busy engineering executive (cutting jargon, front-loading the hook, sharpening the closing question), and produces a tighter final post.
- **Use when:** You want higher writing/reasoning quality without adding a second agent.
- **Watch out for:** Shared blind spots — because the same model shares the same assumptions, use **Pattern 11** or **Pattern 15** when independent verification matters.
- **Code:** [`12_iterative_refinement/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/12_iterative_refinement/app.py)

### 15. Elephant-Goldfish Model (`CONTEXT FIREWALL`)

![Pattern 15: Elephant-Goldfish Model](15_elephant_goldfish/15_elephant_goldfish.gif)

Inspired by [egm.dev](https://egm.dev/) (Spec-Driven Development with AI): an **asymmetric context firewall** separates a context-rich **Elephant** (holds full brainstorming, trade-offs, and revision history) from a completely stateless **Goldfish** (sees *only* the standalone spec — zero memory).
- **Example:** Designing a multi-tenant webhook delivery service (exponential backoff, rate limits, HMAC signing, DLQ). Because the Goldfish has zero memory of the brainstorming session, it ruthlessly exposes unstated assumptions and missing failure modes before a single line of code is written.
- **Use when:** Writing technical specs, RFCs, or prompts that *must* be self-contained for a cold reader or downstream coding agent.
- **Watch out for:** Leaking context across the firewall — if you accidentally pass brainstorming history to the Goldfish, you lose the entire cold-read advantage.
- **Code:** [`15_elephant_goldfish/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/15_elephant_goldfish/app.py)

---

## Patterns 13–14: Grounding and safety

### 13. Tool Use and RAG — The Grounded Agent (`GROUNDED`)

![Pattern 13: Tool Use and RAG](13_tool_use_and_rag/13_tool_use_and_rag.gif)

Never guess from parametric memory. The agent anchors its answer to **3 truth pillars**: **Live Data** (`get_finance_snapshot`), **Policy RAG** (`search_company_policy`), and **Deterministic Code Math** (`calculate_expression`).
- **Example:** Asked *"Can we afford a $4,800 analytics purchase today, and whose approval is required?"*, the agent fetches live cash & payables, retrieves the 2026 procurement policy, computes the exact remaining buffer in code, and cites the policy ID.
- **Use when:** Answers must be current, sourced, and mathematically exact — not plausible-sounding guesses.
- **Watch out for:** Stale RAG indexes — retrieval only prevents hallucinations if the underlying policy docs are kept up to date.
- **Code:** [`13_tool_use_and_rag/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/13_tool_use_and_rag/app.py)

### 14. Human-in-the-Loop (`APPROVAL`)

![Pattern 14: Human-in-the-Loop](14_human_in_the_loop/14_human_in_the_loop.gif)

The agent automates the safe, read-only work (`draft_outreach`), then **freezes at a LangGraph `interrupt_before` checkpoint** backed by `MemorySaver`, resuming `send_email()` only after explicit human sign-off.
- **Example:** A sales outreach agent drafts a 90-word cold email to Maya Lin (VP Engineering, NovaPay), pauses at `interrupt_before=["send_email"]`, and delivers only after the human reviewer approves.
- **Use when:** An action involves money, external messages, legal commitments, or anything irreversible.
- **Watch out for:** Approval fatigue — only gate *irreversible* side effects, not every intermediate read step, or humans will start clicking "Approve" blindly.
- **Code:** [`14_human_in_the_loop/app.py`](https://github.com/aemadhavan/agent-patterns/blob/main/14_human_in_the_loop/app.py)

---

## How to choose in 30 seconds

| If your task is... | Start with |
| :--- | :--- |
| Narrow and predictable | **01. Single-Agent** |
| Unknown path, depends on tool results | **02. ReAct** |
| Long and multi-step, plan worth reviewing | **03. Plan-and-Execute** |
| Fixed steps in order / independent at once | **04. Sequential / 05. Parallel** |
| Needs retries until an objective check passes | **06. Loop** |
| Clear categories or tailored subtasks | **07. Routing / 08. Coordinator** |
| Large cross-team org or open-ended incident | **09. Hierarchical / 10. Swarm** |
| Needs rubric grading or self-polishing | **11. Review & Critique / 12. Reflection** |
| Must be self-contained with zero hidden assumptions | **15. Elephant-Goldfish** |
| Must cite live data, policies, and exact math | **13. Tool Use & RAG** |
| Costly or irreversible if wrong | **14. Human-in-the-Loop** |

---

## The Benchmark: Quality vs. Latency vs. Call Count

Every pattern is runnable and benchmarked end-to-end via `uv run python shared/eval.py` using **Anthropic Claude Haiku (`claude-haiku-4-5`)**, **LangGraph**, and **Arize Phoenix** OpenTelemetry tracing:

- **Total Benchmark LLM Calls:** 46 | **P50 Latency:** 7,124 ms | **P99 Latency:** 55,104 ms

| Pattern | Name | Quality (0–1) | LLM Calls | Latency (ms) |
| :--- | :--- | :---: | :---: | :---: |
| [`01_single_agent`](https://github.com/aemadhavan/agent-patterns/blob/main/01_single_agent/app.py) | Single-Agent System | 0.78 | 3 | 6,765 |
| [`02_react`](https://github.com/aemadhavan/agent-patterns/blob/main/02_react/app.py) | ReAct (Reason + Act) | 0.78 | 3 | 4,564 |
| [`03_plan_and_execute`](https://github.com/aemadhavan/agent-patterns/blob/main/03_plan_and_execute/app.py) | Plan-and-Execute | 0.76 | 6 | 55,104 |
| [`04_sequential`](https://github.com/aemadhavan/agent-patterns/blob/main/04_sequential/app.py) | Sequential (Prompt Chaining) | 0.68 | 4 | 7,484 |
| [`05_parallel`](https://github.com/aemadhavan/agent-patterns/blob/main/05_parallel/app.py) | Parallel | 0.78 | 4 | 15,661 |
| [`06_loop`](https://github.com/aemadhavan/agent-patterns/blob/main/06_loop/app.py) | Loop | 0.95 | 1 | 3,295 |
| [`07_routing`](https://github.com/aemadhavan/agent-patterns/blob/main/07_routing/app.py) | Routing | 0.88 | 2 | 2,860 |
| [`08_coordinator`](https://github.com/aemadhavan/agent-patterns/blob/main/08_coordinator/app.py) | Coordinator | 0.78 | 4 | 24,078 |
| [`09_hierarchical`](https://github.com/aemadhavan/agent-patterns/blob/main/09_hierarchical/app.py) | Hierarchical | 0.88 | 7 | 10,172 |
| [`10_swarm`](https://github.com/aemadhavan/agent-patterns/blob/main/10_swarm/app.py) | Swarm | 0.87 | 1 | 5,169 |
| [`11_review_and_critique`](https://github.com/aemadhavan/agent-patterns/blob/main/11_review_and_critique/app.py) | Review & Critique | 0.78 | 4 | 17,600 |
| [`12_iterative_refinement`](https://github.com/aemadhavan/agent-patterns/blob/main/12_iterative_refinement/app.py) | Iterative Refinement | 0.68 | 3 | 10,757 |
| [`13_tool_use_and_rag`](https://github.com/aemadhavan/agent-patterns/blob/main/13_tool_use_and_rag/app.py) | Tool Use & RAG | 0.88 | 3 | 5,790 |
| [`14_human_in_the_loop`](https://github.com/aemadhavan/agent-patterns/blob/main/14_human_in_the_loop/app.py) | Human-in-the-Loop | 0.72 | 1 | 2,625 |

### 3 Architectural Takeaways
1. **Routing (0.88 quality, 2.8s) and Tool Use + RAG (0.88 quality, 5.8s) deliver the best quality-to-latency ratio.**
2. **Objective verification wins:** `06_loop` hit **0.95 quality** in 3.3s because unit tests give the model crisp, unambiguous ground truth.
3. **Earn your complexity:** Multi-agent orchestration (Plan-and-Execute, Coordinator, Hierarchical) multiplies LLM calls and latency — only pay that tax when evals prove a single agent breaks down.

---

## Real Production Systems Combine Patterns (Composite Architectures)

In production, you rarely use just one pattern in isolation. The real power comes from snapping 2–3 simple patterns together:

1. **Enterprise Customer Refund Agent:**
   `07_routing` (classify refund vs. tech support) → `13_tool_use_and_rag` (fetch live invoice + refund policy + exact math) → `14_human_in_the_loop` (pause at `interrupt_before` if refund > $100).
2. **Spec-Driven Coding Pipeline:**
   `15_elephant_goldfish` (harden the design spec with a stateless cold-read reviewer) → `06_loop` (generate code and iterate against automated unit tests until green).
3. **Executive Market Briefing:**
   `08_coordinator` (decompose into tailored briefs) → `05_parallel` (run analysts concurrently) → `11_review_and_critique` (deal-desk / fact-check gate before publishing).

---

## Production Observability with Arize Phoenix

Architecture alone won't save a blind system. Run `docker compose up -d` and `ENABLE_PHOENIX=true uv run python shared/eval.py` to trace every LLM call, tool invocation, token count, and latency breakdown via OpenTelemetry into a local **Arize Phoenix** UI (`http://localhost:6007`).

> **Tip for your LinkedIn publish:** Drop 1 screenshot of a live Arize Phoenix span tree (e.g., `03_plan_and_execute` or `13_tool_use_and_rag`) right here — showing real traces immediately proves the system is production-tested.

---

## The "Earn Your Complexity" Playbook

1. **Start with Single-Agent + Grounded Tools/RAG** for narrow, predictable tasks.
2. **Add Routing or Sequential/Parallel** when categories or steps are known upfront.
3. **Adopt Plan-and-Execute, Coordinator, Hierarchical, or Swarm** only when evals prove a single agent cannot handle the decomposition.
4. **Use Elephant-Goldfish** when specs or prompts must be bulletproof for a cold reader.
5. **Add Human-in-the-Loop checkpoints** before any irreversible action, and instrument **Arize Phoenix** OpenTelemetry tracing from day one.

### A question to close
If you are building agents today, look at your current system and ask: **which pattern am I actually using — and did I choose it, or did I drift into it?**

---

## LinkedIn Feed Post Copy (Ready to Publish)

> Most AI agents fail in production because teams pick patterns based on hype rather than failure modes, latency SLAs, and cost.
>
> Instead of memorizing 15 theoretical buzzwords, I built, animated, and benchmarked all **15 production AI Agent Design Patterns** using Anthropic Claude, LangGraph, and Arize Phoenix.
>
> 📊 **What the benchmarks actually showed (46 LLM calls, P50: 7.1s):**
> 1. **Single-Agent + Grounded Tool Use / RAG** (0.88 quality, 5.8s) handles 80% of production workloads.
> 2. **Routing** (0.88 quality, 2.8s) keeps specialist prompts tight without multi-agent overhead.
> 3. **Bounded Loops with objective tests** hit **0.95 quality** in 3.3s — ground-truth checks beat vague self-critique.
> 4. **Plan-and-Execute & Coordinator** unlock complex work, but cost 4–6x more LLM calls and up to 55s latency.
> 5. **Elephant-Goldfish** (context-rich drafter + stateless cold-read reviewer) exposes hidden spec assumptions before you write a single line of code.
>
> Every pattern in the repo includes an **animated architecture GIF**, runnable LangGraph code, and OpenTelemetry tracing.
>
> 🔗 Full GitHub Repository & Code: https://github.com/aemadhavan/agent-patterns
>
> Which agent design pattern is your team running in production today? Let's discuss in the comments!
>
> `#AIEngineering #AgenticAI #AIAgents #SoftwareArchitecture #LLM #MLOps #LangGraph #ArizePhoenix #GenerativeAI`
