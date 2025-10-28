from src.core.state import GraphState


def route_after_diff(state: GraphState):
    """
    Router that decides the next step based on the 'current_action' field in the state.
    """
    current_action = state.get("current_action")
    diff = state.get("diff")

    if not diff:
        return "end"

    if current_action == "analyze":
        return "analyze_code"
    elif current_action == "commit":
        return "generate_commit"
    else:
        return "end"
