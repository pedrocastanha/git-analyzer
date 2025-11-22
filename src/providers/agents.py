from src.providers.chains import ChainManager
from src.providers.llms import LLMManager
from src.providers.tools.analyzer_tools import tools_analyzer


class AgentManager:
    @staticmethod
    def get_analyzer_agent(model: str, config: dict):
        llm = LLMManager.get_llm(model, config)
        llm_with_tools = llm.bind_tools(tools_analyzer)
        language = config.get("language", "pt")
        return ChainManager.get_analyzer_chain(llm_with_tools, language)

    @staticmethod
    def get_generate_improvements_agent(model: str, config: dict):
        llm = LLMManager.get_llm(model, config)
        llm_with_tools = llm.bind_tools(tools_analyzer)
        language = config.get("language", "pt")
        return ChainManager.get_generate_improvements_chain(llm_with_tools, language)

    @staticmethod
    def get_generate_commit_message_agent(model: str, config: dict):
        llm = LLMManager.get_llm(model, config)
        llm_with_tools = llm.bind_tools(tools_analyzer)
        language = config.get("language", "pt")
        return ChainManager.get_generate_commit_message_chain(llm_with_tools, language)

    @staticmethod
    def get_deep_analyze_critic_agent(model: str, config: dict):
        llm = LLMManager.get_llm(model, config)
        llm_with_tools = llm.bind_tools(tools_analyzer)
        language = config.get("language", "pt")
        return ChainManager.get_deep_analyze_critic_chain(llm_with_tools, language)

    @staticmethod
    def get_deep_analyze_constructive_agent(model: str, config: dict):
        llm = LLMManager.get_llm(model, config)
        llm_with_tools = llm.bind_tools(tools_analyzer)
        language = config.get("language", "pt")
        return ChainManager.get_deep_analyze_constructive_chain(llm_with_tools, language)

    @staticmethod
    def get_executive_report_agent(model: str, config: dict):
        llm = LLMManager.get_llm(model, config)
        llm_with_tools = llm.bind_tools(tools_analyzer)
        language = config.get("language", "pt")
        return ChainManager.get_executive_report_chain(llm_with_tools, language)

    @staticmethod
    def get_refine_commit_message_agent(model: str, config: dict):
        llm = LLMManager.get_llm(model, config)
        return llm

    @staticmethod
    def get_split_diff_agent(model: str, config: dict):
        llm = LLMManager.get_llm(model, config)
        llm_with_tools = llm.bind_tools(tools_analyzer)
        language = config.get("language", "pt")
        return ChainManager.get_split_diff_chain(llm_with_tools, language)
