from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.messages import (
    AnalyzerSystemPrompt,
    GenerateImprovementsSystemPrompt,
    GenerateCommitMessageSystemPrompt,
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
