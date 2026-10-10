
from langgraph.graph import StateGraph, START, END

from app.ai.graph_state import AssistantState
from app.ai.graph_nodes import (
    interpret_request,
    route_request,
    clarification_node,
    unsupported_node,
    prepare_sale_node,
    quote_node,
    execute_read_tool,
    format_tool_result,
    tool_error_node,
)


def select_route(state: AssistantState) -> str:
    return state["route"]


def build_graph():
    graph = StateGraph(AssistantState)

    graph.add_node("interpret", interpret_request)
    graph.add_node("route", route_request)
    graph.add_node("clarification", clarification_node)
    graph.add_node("unsupported", unsupported_node)
    graph.add_node("prepare_sale", prepare_sale_node)
    graph.add_node("quote", quote_node)
    graph.add_node("execute_read", execute_read_tool)
    graph.add_node("format_result", format_tool_result)
    graph.add_node("tool_error", tool_error_node)

    graph.add_edge(START, "interpret")
    graph.add_edge("interpret", "route")

    graph.add_conditional_edges(
        "route",
        select_route,
        {
            "clarification": "clarification",
            "unsupported": "unsupported",
            "read": "execute_read",
            "quote": "quote",
            "prepare_sale": "prepare_sale",
        },
    )

    graph.add_conditional_edges(
        "execute_read",
        select_route,
        {
            "read_result": "format_result",
            "clarification": "clarification",
            "tool_error": "tool_error",
        },
    )

    graph.add_edge("clarification", END)
    graph.add_edge("unsupported", END)
    graph.add_edge("prepare_sale", END)
    graph.add_edge("quote", END)
    graph.add_edge("format_result", END)
    graph.add_edge("tool_error", END)

    return graph.compile()


assistant_graph = build_graph()
