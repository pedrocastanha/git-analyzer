from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.messages import (
    AnalyzerSystemPrompt,
    GenerateImprovementsSystemPrompt,
    GenerateCommitMessageSystemPrompt,
    DeepAnalyzeCriticSystemPrompt,
    DeepAnalyzeConstructiveSystemPrompt,
    PatchGeneratorSystemPrompt,
)


class PromptManager:
    @staticmethod
    def get_analyzer_prompt():
        return ChatPromptTemplate.from_messages(
            [
                ("system", AnalyzerSystemPrompt.PROMPT),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    @staticmethod
    def get_generate_improvements_prompt():
        return ChatPromptTemplate.from_messages(
            [
                ("system", GenerateImprovementsSystemPrompt.PROMPT),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    @staticmethod
    def get_generate_commit_message_prompt():
        return ChatPromptTemplate.from_messages(
            [
                ("system", GenerateCommitMessageSystemPrompt.PROMPT),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    @staticmethod
    def get_deep_analyze_critic_prompt():
        return ChatPromptTemplate.from_messages(
            [
                ("system", DeepAnalyzeCriticSystemPrompt.PROMPT),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    @staticmethod
    def get_deep_analyze_constructive_prompt():
        return ChatPromptTemplate.from_messages(
            [
                ("system", DeepAnalyzeConstructiveSystemPrompt.PROMPT),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    @staticmethod
    def get_patch_generator_prompt():
        return ChatPromptTemplate.from_messages(
            [
                ("system", PatchGeneratorSystemPrompt.PROMPT),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
