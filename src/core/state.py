from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
    diff: str | None
    analysis: str | None
    commit_message: str | None
    patch: str | None
    current_action: str | None
    user_confirmation: bool | None
    error: str | None
    repo_path: str
    config: dict
    conversation_history: Annotated[list, add_messages]
    split_commits: list[dict] | None
