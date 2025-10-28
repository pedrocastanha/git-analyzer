import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI


class LLMProvider:
    @staticmethod
    def create(config: dict):
        provider = config.get('ai_provider', 'gemini')

        if provider == 'gemini':
            api_key = config.get('gemini_api_key', '') or os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("Gemini API key not found")
            return ChatGoogleGenerativeAI(model = config.get('gemini_model', 'gemini-2.5-flash'), api_key=api_key)

        elif provider == 'openai':
            api_key = config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not found")
            return ChatOpenAI(model = config.get('openai_model', 'gpt-4o-mini'), api_key = api_key)
