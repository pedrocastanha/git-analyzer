from src.providers.agents import AgentManager
from src.core.nodes import extract_llm_content
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import re


class SuggestionType(Enum):
    """Tipos de sugestão"""
    COMMIT = "commit"
    FIX_ERROR = "fix_error"
    IMPROVE = "improve"
    SECURITY = "security"
    REFACTOR = "refactor"


@dataclass
class Suggestion:
    """Estrutura de uma sugestão"""

    type: SuggestionType
    title: str
    description: str
    priority: int  # 1-5
    data: Dict[str, Any]
    auto_executable: bool = True

    def get_emoji(self) -> str:
        emojis = {
            SuggestionType.COMMIT: "💾 Commit - ",
            SuggestionType.FIX_ERROR: "🔧 Fix - ",
            SuggestionType.IMPROVE: "✨ Improve - ",
            SuggestionType.REFACTOR: "♻️ Refactor - ",
            SuggestionType.SECURITY: "🔒 Security - ",
        }
        return emojis.get(self.type, "💡")


class SuggestionBuilder:
    """
    Constrói sugestões usando IA para decidir
    SEM heurísticas - IA retorna JSON estruturado
    """

    def __init__(self, config: dict):
        self.config = config
        self.language = config.get("language", "pt")

    async def build_from_diff(self, diff: str) -> List[Suggestion]:
        """
        Chama IA para gerar sugestões estruturadas

        Args:
            diff: Diff completo do git

        Returns:
            Lista de sugestões
        """

        print("🤖 IA analisando e gerando sugestões...")

        ai_response = await self._ask_ai_for_suggestions(diff)

        if not ai_response:
            return []

        suggestions = self._parse_ai_response(ai_response)

        print(f"✅ {len(suggestions)} sugestão(ões) gerada(s)")

        return suggestions

    async def _ask_ai_for_suggestions(self, diff: str) -> Optional[str]:

        provider = self.config.get("ai_provider", "gemini")

        try:
            agent = AgentManager.get_suggestion_builder_agent(provider, self.config)

            response = await agent.ainvoke({"diff": diff[:5000]})

            content = extract_llm_content(response.content) if hasattr(response, 'content') else str(response)

            return content

        except Exception as e:
            print(f"❌ Erro ao chamar IA: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _parse_ai_response(self, response: str) -> List[Suggestion]:
        """Parseia JSON da IA"""

        json_str = self._extract_json(response)

        if not json_str:
            print("⚠️  IA não retornou JSON válido")
            return []

        try:
            data = json.loads(json_str)
            suggestions_data = data.get("suggestions", [])

            suggestions = []

            for item in suggestions_data:
                try:
                    suggestion = self._create_suggestion_from_dict(item)
                    if suggestion:
                        suggestions.append(suggestion)
                except Exception as e:
                    print(f"⚠️  Erro ao criar sugestão: {e}")
                    continue

            return suggestions

        except json.JSONDecodeError as e:
            print(f"❌ Erro ao parsear JSON: {e}")
            return []

    def _extract_json(self, text: str) -> Optional[str]:
        """Extrai JSON de texto (suporta markdown blocks)"""

        text = text.strip()

        json_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_block_pattern, text, re.DOTALL)

        if match:
            return match.group(1)

        json_pattern = r'\{.*\}'
        match = re.search(json_pattern, text, re.DOTALL)

        if match:
            return match.group(0)

        return None

    def _create_suggestion_from_dict(self, data: dict) -> Optional[Suggestion]:
        """Cria objeto Suggestion a partir de dict"""

        if "type" not in data or "title" not in data:
            return None

        try:
            suggestion_type = SuggestionType(data["type"])
        except ValueError:
            print(f"⚠️  Tipo inválido: {data['type']}")
            return None

        title = data.get("title", "")
        description = data.get("description", "")
        priority = data.get("priority", 3)
        suggestion_data = data.get("data", {})

        auto_executable = suggestion_type != SuggestionType.SECURITY

        return Suggestion(
            type=suggestion_type,
            title=title,
            description=description,
            priority=priority,
            data=suggestion_data,
            auto_executable=auto_executable
        )