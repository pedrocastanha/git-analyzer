from langchain_core.tools import tool
from src.providers.tools.file_tools import file_tools


@tool
def search_web_informations():
    """Search for web informations."""
    return []


@tool
def search_books_informations():
    """Search for books informations."""
    return []


# Combina tools de busca + tools de arquivo
tools_analyzer = [
    search_web_informations,
    search_books_informations,
    *file_tools  # Adiciona todas as tools de arquivo
]
