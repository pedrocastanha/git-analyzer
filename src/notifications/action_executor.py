import asyncio
from typing import Dict, Any
from .suggestion_builder import Suggestion, SuggestionType
import git
import tempfile
import subprocess
import os


class ActionExecutor:
    def __init__(self, agent_ref):
        self.agent = agent_ref
        self.repo_path = agent_ref.repo_path
        self.config = agent_ref.config_manager.config
        self.language = self.config.get("language", "pt")

    async def execute(self, suggestion: Suggestion) -> bool:
        print("\n" + "=" * 80)
        if self.language == "pt":
            print(f"Executando: {suggestion.title}")
        else:
            print(f"Executing: {suggestion.title}")
        print("=" * 80 + "\n")

        try:
            if suggestion.type == SuggestionType.COMMIT:
                return await self._execute_commit(suggestion)
            elif suggestion.type == SuggestionType.FIX_ERROR:
                return await self._execute_fix(suggestion)
            elif suggestion.type == SuggestionType.IMPROVE:
                return await self._execute_improvement(suggestion)
            elif suggestion.type == SuggestionType.SECURITY:
                return await self._execute_security_fix(suggestion)
            elif suggestion.type == SuggestionType.REFACTOR:
                return await self._execute_refactor(suggestion)
            else:
                print(f"Tipo de acao nao implementado: {suggestion.type}")
                return False
        except Exception as e:
            print(f"Erro ao executar acao: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def _execute_commit(self, suggestion: Suggestion) -> bool:
        print(f"Usando comando 'split-up' existente...")
        await self.agent.split_commit_and_push()
        return True

    async def _execute_fix(self, suggestion: Suggestion) -> bool:
        file_path = suggestion.data.get("file")
        line = suggestion.data.get("line")
        error_desc = suggestion.data.get("error_description", suggestion.description)

        print(f"Gerando correcao para: {error_desc}")

        current_code = ""
        if file_path and os.path.exists(os.path.join(self.repo_path, file_path)):
            with open(os.path.join(self.repo_path, file_path), 'r') as f:
                current_code = f.read()

        from src.providers.llms import LLMManager
        from src.core.nodes import extract_llm_content

        provider = self.config.get("ai_provider", "gemini")
        llm = LLMManager.get_llm(provider, self.config)

        prompt = f"""Voce e um assistente especializado em corrigir codigo.

ERRO DETECTADO:
{error_desc}

ARQUIVO: {file_path if file_path else 'nao especificado'}
LINHA: {line if line else 'nao especificada'}

CODIGO ATUAL:
```
{current_code[:2000] if current_code else 'Nao disponivel'}
```

Por favor, gere um patch (unified diff format) para corrigir este erro.
Retorne APENAS o patch, sem explicacoes.
"""

        chain = llm | (lambda x: x)
        response = await chain.ainvoke(prompt)
        fix_patch = extract_llm_content(response.content) if hasattr(response, 'content') else str(response)

        print(f"\nPatch gerado:")
        print(fix_patch[:500] + "..." if len(fix_patch) > 500 else fix_patch)

        if self.language == "pt":
            confirm = input("\nAplicar este patch? (s/n): ").strip().lower()
        else:
            confirm = input("\nApply this patch? (y/n): ").strip().lower()

        if confirm not in ["s", "sim", "y", "yes"]:
            print("Operacao cancelada")
            return False

        with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
            f.write(fix_patch)
            patch_path = f.name

        try:
            result = subprocess.run(
                ["git", "apply", patch_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("Correcao aplicada com sucesso!")
                return True
            else:
                print(f"Erro ao aplicar patch: {result.stderr}")
                return False
        finally:
            os.unlink(patch_path)

    async def _execute_improvement(self, suggestion: Suggestion) -> bool:
        improvement_desc = suggestion.data.get("improvement_description", suggestion.description)
        print(f"Aplicando melhoria: {improvement_desc}")
        print("Melhorias devem ser aplicadas manualmente por enquanto.")
        print(f"   Sugestao: {improvement_desc}")
        return False

    async def _execute_security_fix(self, suggestion: Suggestion) -> bool:
        security_desc = suggestion.data.get("security_description", suggestion.description)
        print(f"ALERTA DE SEGURANCA: {security_desc}")
        print("\nEsta e uma correcao de seguranca critica!")

        if self.language == "pt":
            confirm = input("\nDeseja gerar e aplicar correcao? (s/n): ").strip().lower()
        else:
            confirm = input("\nGenerate and apply fix? (y/n): ").strip().lower()

        if confirm not in ["s", "sim", "y", "yes"]:
            print("Operacao cancelada")
            return False

        return await self._execute_fix(suggestion)

    async def _execute_refactor(self, suggestion: Suggestion) -> bool:
        refactor_desc = suggestion.data.get("refactor_description", suggestion.description)
        print(f"Refatoracao: {refactor_desc}")
        print("Refatoracoes devem ser aplicadas manualmente por enquanto.")
        return False
