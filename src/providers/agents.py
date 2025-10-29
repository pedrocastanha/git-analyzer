from src.providers.chains import ChainManager
from src.providers.llms import LLMManager
from src.providers.tools.analyzer_tools import tools_analyzer


class AgentManager:
    @staticmethod
    def get_analyzer_agent(model: str, config: dict):
        llm = LLMManager.get_llm(model, config)
        llm_with_tools = llm.bind_tools(tools_analyzer)
        return ChainManager.get_analyzer_chain(llm_with_tools)

    @staticmethod
    def get_generate_improvements_agent(model: str, config: dict):
        llm = LLMManager.get_llm(model, config)
        llm_with_tools = llm.bind_tools(tools_analyzer)
        return ChainManager.get_generate_improvements_chain(llm_with_tools)

    @staticmethod
    def get_generate_commit_message_agent(model: str, config: dict):
        llm = LLMManager.get_llm(model, config)
        llm_with_tools = llm.bind_tools(tools_analyzer)
        return ChainManager.get_generate_commit_message_chain(llm_with_tools)

    @staticmethod
    def get_deep_analyze_critic_agent(model: str, config: dict):
        llm = LLMManager.get_llm(model, config)
        llm_with_tools = llm.bind_tools(tools_analyzer)
        return ChainManager.get_deep_analyze_critic_chain(llm_with_tools)

    @staticmethod
    def get_deep_analyze_constructive_agent(model: str, config: dict):
        llm = LLMManager.get_llm(model, config)
        llm_with_tools = llm.bind_tools(tools_analyzer)
        return ChainManager.get_deep_analyze_constructive_chain(llm_with_tools)
