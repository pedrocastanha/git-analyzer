from pydantic import BaseModel, Field

class CodeSolution(BaseModel):
    """Represents the generated code solution."""
    description: str = Field(..., description="Description of the code solution.")
    code_snippet: str = Field(..., description="The code snippet implementing the solution.")
