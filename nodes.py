import os
from git import Repo
from github import Github
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from state import GraphState
from models import CodeSolution

def initialize_state(task_content: str, github_token: str, target_repo_name: str) -> dict:
    """Initializes the graph state by cloning the target repository and setting the task content."""
    repo_dir = ""
    try:
        # Create a directory for the agent's work
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_dir = os.path.join(script_dir, 'agent-task')

        # Clean up previous work
        if os.path.exists(repo_dir):
            os.system(f'rm -rf {repo_dir}')

        g = Github(github_token)
        repo = g.get_repo(target_repo_name)
        Repo.clone_from(repo.clone_url, repo_dir)
        print(f"Successfully cloned target repository {target_repo_name} to {repo_dir}")

        return {
            "status": "initialized",
            "task_content": task_content,
            "repo_dir": repo_dir,
            "generation": None,
            "iterations": 0,
            "pr_url": None
        }
    except Exception as e:
        print(f"Repository setup failed: {str(e)}")
        return {
            "status": "failed", "task_content": task_content, "repo_dir": repo_dir,
            "generation": None, "iterations": 0, "pr_url": None
        }

def generate_solution(state: GraphState) -> dict:
    print(f"--- Iteration {state['iterations'] + 1}: Generating Solution ---")
    task_content = state["task_content"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a python developer. Generate a solution based on the task requirements. 
        Include complete code with imports, type hints, docstrings, and examples.
        Your response must be a valid JSON that conforms to the 'CodeSolution' schema."""),
        ("human", "Task description: \n{task}"),
    ])

    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        chain = prompt | llm.with_structured_output(CodeSolution)
        
        solution = chain.invoke({"task": task_content})
        print("Solution generated successfully.")
        
        return {**state, "status": "generated", "generation": solution, "iterations": state["iterations"] + 1}
    except Exception as e:
        print(f"Failed to generate solution: {e}")
        return {**state, "status": "failed"}

def test_solution(state: GraphState) -> dict:
    """Tests the generated code solution."""
    print("--- Testing Solution ---")
    if state["status"] != "generated" or not state["generation"]:
        print("Testing skipped: No solution to test.")
        return {**state, "status": "failed"}

    try:
        # This is a hardcoded test for the specific task.
        # In a real-world scenario, this would be more dynamic.
        namespace = {}
        exec(state["generation"].code_snippet, namespace)

        # Example test case
        result = namespace['calculate_products']([1, 2, 3, 4])
        expected = [24, 12, 8, 6]
        
        if result == expected:
            print("Test passed!")
            return {**state, "status": "tested"}
        else:
            print(f"Test failed: Expected {expected}, got {result}")
            return {**state, "status": "failed"}
    except Exception as e:
        print(f"Test execution failed: {e}")
        return {**state, "status": "failed"}

def create_pr(state: GraphState) -> dict:
    """Creates a pull request on GitHub with the solution."""
    print("--- Creating Pull Request ---")
    if state["status"] != "tested" or not state["generation"]:
        print("PR creation skipped: Solution not tested or missing.")
        return {**state, "status": "failed"}

    try:
        solution = state["generation"]
        repo_dir = state["repo_dir"]
        repo = Repo(repo_dir)

        # Create a new branch
        branch_name = "solution/array-products-challenge"
        if branch_name in repo.heads:
             repo.delete_head(branch_name, '-D')
        
        current = repo.create_head(branch_name)
        current.checkout()

        # Create the solution file
        solution_path = os.path.join(repo_dir, "array_products.py")
        with open(solution_path, "w") as f:
            f.write(solution.code_snippet)

        # Commit and push
        repo.index.add([solution_path])
        repo.index.commit("feat: Add array_products.py solution")
        origin = repo.remote("origin")
        origin.push(refspec=f'{branch_name}:{branch_name}', force=True)
        print(f"Pushed changes to branch {branch_name}")

        # Create Pull Request
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GITHUB_TOKEN environment variable not set.")
            
        g = Github(github_token)
        
        # Extract 'owner/repo_name' from the remote URL
        remote_url = repo.remotes.origin.url
        repo_full_name = '/'.join(remote_url.split('/')[-2:]).replace('.git', '')
        gh_repo = g.get_repo(repo_full_name)

        pr = gh_repo.create_pull(
            title="Feat: Add array products calculator",
            body=f"### Solution Description\n\n{solution.description}",
            base="master",
            head=branch_name
        )

        print(f"Successfully created PR: {pr.html_url}")
        return {**state, "status": "completed", "pr_url": pr.html_url}
    except Exception as e:
        print(f"Failed to create PR: {e}")
        return {**state, "status": "failed"}

def should_continue(state: GraphState) -> str:
    """Determines the next step based on the current state."""
    if state["status"] == "failed":
        if state["iterations"] < 3:
            print("Attempting to regenerate solution.")
            return "generate"
        else:
            print("Maximum iterations reached. Ending process.")
            return "end"
    elif state["status"] == "tested":
        return "create_pr"
    else:
        # Default to ending if status is unexpected
        return "end"