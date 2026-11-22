"""Pattern 05: Parallel.

Independent sub-agents execute simultaneously (fan-out) and their results are
merged (fan-in) for lower latency and broader coverage.
Example: A travel agent searches flights, hotels, and local transport in parallel
for the same dates, then merges them into one cohesive itinerary.
"""

import sys
from pathlib import Path
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

sys.path.append(str(Path(__file__).resolve().parent.parent))
from shared.llm import generate_text


class TravelState(TypedDict):
    request: str
    flights: str
    hotels: str
    transport: str
    itinerary: str


def search_flights(state: TravelState) -> dict:
    return {
        "flights": generate_text(
            f"Suggest 2 realistic flight options (times + estimated USD price) for: {state['request']}"
        )
    }


def search_hotels(state: TravelState) -> dict:
    return {
        "hotels": generate_text(
            f"Suggest 2 business-friendly hotel options near the city center for: {state['request']}"
        )
    }


def search_transport(state: TravelState) -> dict:
    return {
        "transport": generate_text(
            f"Suggest airport transfer and local transit options for: {state['request']}"
        )
    }


def merge_itinerary(state: TravelState) -> dict:
    prompt = (
        f"Merge these three parallel research results into one clean business trip itinerary.\n\n"
        f"FLIGHTS:\n{state['flights']}\n\n"
        f"HOTELS:\n{state['hotels']}\n\n"
        f"TRANSPORT:\n{state['transport']}"
    )
    return {"itinerary": generate_text(prompt)}


def build_graph():
    graph = StateGraph(TravelState)
    graph.add_node("flights", search_flights)
    graph.add_node("hotels", search_hotels)
    graph.add_node("transport", search_transport)
    graph.add_node("merge", merge_itinerary)

    # Fan-out in parallel from START
    graph.add_edge(START, "flights")
    graph.add_edge(START, "hotels")
    graph.add_edge(START, "transport")

    # Fan-in to merge
    graph.add_edge("flights", "merge")
    graph.add_edge("hotels", "merge")
    graph.add_edge("transport", "merge")
    graph.add_edge("merge", END)
    return graph.compile()


def run(task: str | None = None) -> str:
    query = task or "3-day business trip from Sydney to Melbourne, Dec 8-10, 2026."
    app = build_graph()
    result = app.invoke(
        {"request": query, "flights": "", "hotels": "", "transport": "", "itinerary": ""}
    )
    return result["itinerary"]


if __name__ == "__main__":
    print(run())
