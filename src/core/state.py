from typing import Annotated, List
import operator
from langchain_core.messages import BaseMessage
from pydantic import BaseModel


class GraphState(BaseModel):
    messages: Annotated[list[BaseMessage], operator.add]
    diff: str | None
    analysis: str | None
    commit_message: str | None
    patch: str | None
    current_action: str | None
    user_confirmation: bool | None
    error: str | None
    repo_path: str
    config: dict
