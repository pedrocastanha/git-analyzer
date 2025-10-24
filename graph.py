from langgraph.graph import StateGraph, END, START
from state import GraphState
from nodes import generate_solution, test_solution, create_pr, should_continue

def create_agent_workflow():
    """Creates and compiles the LangGraph workflow for the Git Analyzer agent."""
    workflow = StateGraph(GraphState)

    workflow.add_node("generate", generate_solution)
    workflow.add_node("test", test_solution)
    workflow.add_node("create_pr", create_pr)

    workflow.add_edge(START, "generate")

    workflow.add_conditional_edges(
        "test",
        should_continue,
        {
            "generate": "generate",
            "create_pr": "create_pr",
            "end": END,
        },
    )
    workflow.add_edge("generate", "test")
    workflow.add_edge("create_pr", END)

    return workflow.compile()
