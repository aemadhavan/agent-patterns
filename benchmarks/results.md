# Agent Design Patterns — Benchmark Results

- **Total Agent LLM Calls:** 46
- **P50 Latency:** 7124 ms
- **P99 Latency:** 55104 ms

| Pattern | Name | Category | Quality (0-1) | LLM Calls | Latency (ms) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `01_single_agent` | Single-Agent System | Start Simple | 0.78 | 3 | 6765 |
| `02_react` | ReAct (Reason + Act) | Start Simple | 0.78 | 3 | 4564 |
| `03_plan_and_execute` | Plan-and-Execute | Start Simple | 0.76 | 6 | 55104 |
| `04_sequential` | Sequential (Prompt Chaining) | Control Flow | 0.68 | 4 | 7484 |
| `05_parallel` | Parallel | Control Flow | 0.78 | 4 | 15661 |
| `06_loop` | Loop | Control Flow | 0.95 | 1 | 3295 |
| `07_routing` | Routing | Dispatch & Scale | 0.88 | 2 | 2860 |
| `08_coordinator` | Coordinator (Orchestrator-Workers) | Dispatch & Scale | 0.78 | 4 | 24078 |
| `09_hierarchical` | Hierarchical Task Decomposition | Dispatch & Scale | 0.88 | 7 | 10172 |
| `10_swarm` | Swarm (Multi-Agent Collaboration) | Collaboration & Quality | 0.87 | 1 | 5169 |
| `11_review_and_critique` | Review and Critique | Collaboration & Quality | 0.78 | 4 | 17600 |
| `12_iterative_refinement` | Iterative Refinement (Reflection) | Collaboration & Quality | 0.68 | 3 | 10757 |
| `13_tool_use_and_rag` | Tool Use and RAG (Grounded Agent) | Grounding & Safety | 0.88 | 3 | 5790 |
| `14_human_in_the_loop` | Human-in-the-Loop | Grounding & Safety | 0.72 | 1 | 2625 |
