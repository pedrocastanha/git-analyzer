from typing import Literal

from langchain.agents import AgentState

from src.core.state import GraphState

def shoulf_continue_analysis(state: GraphState) -> Literal["generate_improvements", "end"]:
    if state.get('user_confirmation'):
        return "generate_improvements"
    return "end"


def should_apply_patch(state: GraphState) -> str:
    if not state.get('patch'):
        print("ℹ️  Sem patch para aplicar\n")
        return "end"

    if not state.get('user_confirmation'):
        print("ℹ️  Aguardando confirmação do usuário\n")
        return "end"

    print("✅ Aplicando patch confirmado...\n")
    return "apply_patch"

def has_diff(state: AgentState) -> Literal["continue", "end"]:
    if state.get('diff'):
        return "continue"
    return "end"