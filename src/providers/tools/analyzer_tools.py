from langchain_core.tools import tool


@tool
def search_web_informations():
    """Search for web informations."""
    return []


@tool
def search_books_informations():
    """Search for books informations."""
    return []


tools_analyzer = [search_web_informations, search_books_informations]
