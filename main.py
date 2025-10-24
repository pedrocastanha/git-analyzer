import os
from dotenv import load_dotenv
from nodes import initialize_state
from graph import create_agent_workflow

load_dotenv() # Carrega as variáveis do .env

def run_agent(task_content: str, github_token: str, target_repo_name: str):
    """Runs the Git Analyzer agent workflow."""
    try:
        agent = create_agent_workflow()
        initial_state = initialize_state(task_content, github_token, target_repo_name)

        if initial_state["status"] == "failed":
            print("Failed to initialize agent state. Exiting.")
            return {"status": "failed"}

        print("Starting agent workflow...")
        # The invoke method returns the final state after the graph has run
        final_state = agent.invoke(initial_state)

        if final_state["status"] == "completed":
            print(f"Agent completed successfully. PR URL: {final_state.get('pr_url', 'N/A')}")
        else:
            print(f"Agent failed to complete the task. Final status: {final_state['status']}")

        return {
            "status": final_state["status"],
            "generation": final_state.get("generation").code_snippet if final_state.get("generation") else None,
            "pr_url": final_state.get("pr_url")
        }
    except Exception as e:
        print(f"Agent execution failed: {str(e)}")
        return {"status": "failed"}

if __name__ == "__main__":
    github_token = os.getenv("GITHUB_TOKEN")
    target_repo_name = os.getenv("TARGET_REPO_NAME")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    task_content = """
        # Task: Implement a Python function to calculate the product of all elements in a list, excluding the element at the current index.
        
        ## Description
        Given a list of integers `nums`, write a Python function `calculate_products(nums)` that returns a new list `products` where `products[i]` is the product of all elements in `nums` except `nums[i]`.
        
        ## Constraints
        - The input list `nums` will always contain at least two elements.
        - The product of any prefix or suffix (or the total product) will fit within a standard integer type.
        
        ## Example
        ```python
        # Input:
        nums = [1, 2, 3, 4]
        
        # Output:
        # products[0] = 2 * 3 * 4 = 24
        # products[1] = 1 * 3 * 4 = 12
        # products[2] = 1 * 2 * 4 = 8
        # products[3] = 1 * 2 * 3 = 6
        # Result: [24, 12, 8, 6]
        ```
"""

    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set.")
        exit(1)
    if not target_repo_name:
        print("Error: TARGET_REPO_NAME environment variable not set. Example: 'owner/repo'")
        exit(1)
    if not google_api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        exit(1)

    print(f"Running Git Analyzer for target repository: {target_repo_name}")
    result = run_agent(task_content, github_token, target_repo_name)
    print("\n--- Agent Run Summary ---")
    print(f"Status: {result["status"]}")
    if result.get("pr_url"):
        print(f"Pull Request URL: {result["pr_url"]}")
    elif result.get("generation"):
        print("Generated Code Snippet (if available):\n" + result["generation"][:200] + "...")
