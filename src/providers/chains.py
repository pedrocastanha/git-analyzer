from src.providers.prompts import PromptManager


class ChainManager:
    @staticmethod
    def get_analyzer_chain(llm_with_tools, language):
        analyzer_agent_prompt = PromptManager.get_analyzer_prompt(language)
        return analyzer_agent_prompt | llm_with_tools

    @staticmethod
    def get_generate_improvements_chain(llm_with_tools, language):
        generate_improvements_agent_prompt = (
            PromptManager.get_generate_improvements_prompt(language)
        )
        return generate_improvements_agent_prompt | llm_with_tools

    @staticmethod
    def get_generate_commit_message_chain(llm_with_tools, language):
        generate_commit_message_agent_prompt = (
            PromptManager.get_generate_commit_message_prompt(language)
        )
        return generate_commit_message_agent_prompt | llm_with_tools

    @staticmethod
    def get_deep_analyze_critic_chain(llm_with_tools, language):
        critic_prompt = PromptManager.get_deep_analyze_critic_prompt(language)
        return critic_prompt | llm_with_tools

    @staticmethod
    def get_deep_analyze_constructive_chain(llm_with_tools, language):
        deep_analyze_constructive_prompt = (
            PromptManager.get_deep_analyze_constructive_prompt(language)
        )
        return deep_analyze_constructive_prompt | llm_with_tools

    @staticmethod
    def get_refine_commit_message_chain(llm, language):
        refine_commit_message_prompt = PromptManager.get_refine_commit_message_prompt(language)
        return refine_commit_message_prompt | llm

    @staticmethod
    def get_executive_report_chain(llm_with_tools, language):
        executive_report_prompt = PromptManager.get_executive_report_prompt(language)
        return executive_report_prompt | llm_with_tools
