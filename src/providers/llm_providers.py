from src.providers.agents import AgentManager


class LLMProvider:
    @staticmethod
    def create(config: dict, type: str):
        provider = config.get("ai_provider", "gemini")

        if type == "analyze":
            return AgentManager.get_analyzer_agent(provider, config)
        elif type == "generate_improvements":
            return AgentManager.get_generate_improvements_agent(provider, config)
        elif type == "generate_commit_message":
            return AgentManager.get_generate_commit_message_agent(provider, config)
        elif type == "deep_analyze_critic":
            return AgentManager.get_deep_analyze_critic_agent(provider, config)
        elif type == "deep_analyze_constructive":
            return AgentManager.get_deep_analyze_constructive_agent(provider, config)
        elif type == "executive_report":
            return AgentManager.get_executive_report_agent(provider, config)
        elif type == "refine_commit_message":
            return AgentManager.get_refine_commit_message_agent(provider, config)
        elif type == "up":
            return AgentManager.get_analyzer_agent(provider, config)
