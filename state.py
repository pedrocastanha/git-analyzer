from typing import TypedDict
from models import CodeSolution

class GraphState(TypedDict):
    """
    Represents the state of the agent graph.

    Attributes:
        status: The current status of the agent's execution.
        task_content: The content of the task read from the repository.
        repo_dir: The local directory where the repository is cloned.
        generation: The generated code solution.
        iterations: The number of attempts to generate a valid solution.
        pr_url: The URL of the created pull request.
    """
    status: str
    task_content: str
    repo_dir: str
    generation: CodeSolution | None
    iterations: int
    pr_url: str | None
