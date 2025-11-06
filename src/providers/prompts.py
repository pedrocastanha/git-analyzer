from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.messages import (
    AnalyzerSystemPrompt,
    GenerateImprovementsSystemPrompt,
    GenerateCommitMessageSystemPrompt,
    DeepAnalyzeCriticSystemPrompt,
    DeepAnalyzeConstructiveSystemPrompt,
    ExecutiveReportSystemPrompt,
)


class PromptManager:
    @staticmethod
    def get_analyzer_prompt(language="pt"):
        prompt_text = AnalyzerSystemPrompt.get(language)
        return ChatPromptTemplate.from_messages(
            [
                ("system", prompt_text),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    @staticmethod
    def get_generate_improvements_prompt(language="pt"):
        prompt_text = GenerateImprovementsSystemPrompt.get(language)
        return ChatPromptTemplate.from_messages(
            [
                ("system", prompt_text),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    @staticmethod
    def get_generate_commit_message_prompt(language="pt"):
        prompt_text = GenerateCommitMessageSystemPrompt.get(language)
        return ChatPromptTemplate.from_messages(
            [
                ("system", prompt_text),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    @staticmethod
    def get_deep_analyze_critic_prompt(language="pt"):
        prompt_text = DeepAnalyzeCriticSystemPrompt.get(language)
        return ChatPromptTemplate.from_messages(
            [
                ("system", prompt_text),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    @staticmethod
    def get_deep_analyze_constructive_prompt(language="pt"):
        prompt_text = DeepAnalyzeConstructiveSystemPrompt.get(language)
        return ChatPromptTemplate.from_messages(
            [
                ("system", prompt_text),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    @staticmethod
    def get_executive_report_prompt(language="pt"):
        prompt_text = ExecutiveReportSystemPrompt.get(language)
        return ChatPromptTemplate.from_messages(
            [
                ("system", prompt_text),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
