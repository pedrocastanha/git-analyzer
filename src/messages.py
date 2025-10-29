class AnalyzerSystemPrompt:
    PROMPT = """Você é um especialista em análise de código. Analise o diff fornecido e retorne:

1. **Resumo das mudanças**: O que foi alterado ou implementado.
2. **Padrões e boas práticas**: Identifique possíveis melhorias ou violações de boas práticas.
3. **Sugestões de refatoração**: Melhorias específicas para o código.
4. **Possíveis bugs**: Identifique problemas ou bugs potenciais.

Seja objetivo e prático."""

class GenerateImprovementsSystemPrompt:
    PROMPT = """Com base nesta análise:

{analysis}

E neste diff:
```
{diff}
```

Gere um patch Git que implementa as melhorias sugeridas.
Retorne APENAS o patch no formato Git diff.
Se não houver melhorias práticas, responda: "NO_CHANGES_NEEDED"""    

class GenerateCommitMessageSystemPrompt:
    PROMPT = """Analise este diff e gere uma mensagem de commit seguindo conventional commits

Formato: <type:(<scope>): <description>

Tipos válidos: {types}

{diff}

```

Retorne APENAS a mensagem de commit, sem explicações."""