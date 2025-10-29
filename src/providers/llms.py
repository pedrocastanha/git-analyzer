import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI


class LLMManager:
    @staticmethod
    def get_llm(model: str, config: dict):
        if model == 'gemini':
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.5,
                api_key=config.get('gemini_api_key', '') or os.getenv('GEMINI_API_KEY')
            )
        else:
            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.5,
                api_key=config.get('openai_api_key', '') or os.getenv('OPENAI_API_KEY')
            )
