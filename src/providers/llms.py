import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from google.generativeai.types import HarmCategory, HarmBlockThreshold


class LLMManager:
    @staticmethod
    def get_llm(model: str, config: dict):
        if model == "gemini":
            return ChatGoogleGenerativeAI(
                model=config.get("gemini_model", "gemini-2.5-flash"),
                temperature=0.5,
                api_key=config.get("gemini_api_key", "") or os.getenv("GEMINI_API_KEY"),
                safety_settings={
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                },
            )
        else:
            return ChatOpenAI(
                model=config.get("openai_model", "gpt-4.1-mini"),
                temperature=0.5,
                api_key=config.get("openai_api_key", "") or os.getenv("OPENAI_API_KEY"),
            )
