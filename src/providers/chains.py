from src.providers.prompts import PromptManager


class ChainManager:
    @staticmethod
    def get_analyzer_chain(llm_with_tools):
        analyzer_agent_prompt = PromptManager.get_analyzer_prompt()
        return analyzer_agent_prompt | llm_with_tools

    @staticmethod
    def get_generate_improvements_chain(llm_with_tools):
        generate_improvements_agent_prompt = PromptManager.get_generate_improvements_prompt()
        return generate_improvements_agent_prompt | llm_with_tools

    @staticmethod
    def get_generate_commit_message_chain(llm_with_tools):
        generate_commit_message_agent_prompt = PromptManager.get_generate_commit_message_prompt()
        return generate_commit_message_agent_prompt | llm_with_tools
