from typing import Literal

from langchain.agents import AgentState

from src.core.state import GraphState

def shoulf_continue_analysis(state: GraphState) -> Literal["generate_improvements", "end"]:
    if state.get('user_confirmation'):
        return "generate_improvements"
    return "end"

def should_apply_patch(state: AgentState) -> Literal["apply_patch", "end"]:
    if state.get('patch') and state.get('user_confirmation'):
        return "apply_patch"
    return "end"

def has_diff(state: AgentState) -> Literal["continue", "end"]:
    if state.get('diff'):
        return "continue"
    return "end"