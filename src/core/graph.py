from langgraph.graph import StateGraph, END
from src.core.state import GraphState
from src.core.nodes import (
    get_diff_node,
    analyze_code_node,
    generate_improvements_node,
    apply_patch_node,
    generate_commit_message_node,
    commit_and_push_node,
)
from src.core.router import route_after_diff
from src.core.edges import should_apply_patch


def create_graph():
    """
    Creates the single, unified graph for both analysis and commit workflows.
    """
    workflow = StateGraph(GraphState)

    workflow.add_node("get_diff", get_diff_node)
    workflow.add_node("analyze_code", analyze_code_node)
    workflow.add_node("generate_improvements", generate_improvements_node)
    workflow.add_node("apply_patch", apply_patch_node)
    workflow.add_node("generate_commit", generate_commit_message_node)
    workflow.add_node("commit_push", commit_and_push_node)


    workflow.set_entry_point("get_diff")

    workflow.add_conditional_edges(
        "get_diff",
        route_after_diff,
        {
            "analyze_code": "analyze_code",
            "generate_commit": "generate_commit",
            "end": END,
        },
    )

    workflow.add_edge("analyze_code", "generate_improvements")
    workflow.add_conditional_edges(
        "generate_improvements",
        should_apply_patch,
        {"apply_patch": "apply_patch", "end": END},
    )
    workflow.add_edge("apply_patch", END)

    workflow.add_edge("generate_commit", "commit_push")
    workflow.add_edge("commit_push", END)

    return workflow