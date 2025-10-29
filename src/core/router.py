from src.core.state import GraphState


def route_after_diff(state: GraphState):
    current_action = state.get("current_action")
    diff = state.get("diff")

    if not diff:
        return "end"

    if current_action == "analyze":
        return "analyze_code"
    elif current_action == "deep_analyze":
        return "deep_analyze_critic"
    elif current_action == "commit":
        return "generate_commit"
    else:
        return "end"

def route_deep_analysis(state: GraphState):
    conversation_history = state.get("conversation_history", [])
    if len(conversation_history) >= 12:
        return "deep_generate_improvements"

    last_message = conversation_history[-1] if conversation_history else None
    if last_message and last_message.name == "Crítico de Segurança e Padrões":
        return "deep_analyze_constructive"
    else:
        return "deep_analyze_critic"
