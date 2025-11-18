class AnalyzerSystemPrompt:
    PT = """Você é um especialista em análise de código. Analise o diff fornecido e retorne:
            1. **Resumo das mudanças**: O que foi alterado ou implementado.
            2. **Padrões e boas práticas**: Identifique possíveis melhorias ou violações de boas práticas.
            3. **Sugestões de refatoração**: Melhorias específicas para o código.
            4. **Possíveis bugs**: Identifique problemas ou bugs potenciais.
            
            Seja objetivo e prático."""

    EN = """You are a code analysis expert. Analyze the provided diff and return:     
            1. **Summary of changes**: What was changed or implemented.
            2. **Patterns and best practices**: Identify possible improvements or violations of best practices.
            3. **Refactoring suggestions**: Specific improvements for the code.
            4. **Potential bugs**: Identify problems or potential bugs.
            
            Be objective and practical."""

    @staticmethod
    def get(language="pt"):
        return getattr(AnalyzerSystemPrompt, language.upper(), AnalyzerSystemPrompt.PT)


class GenerateImprovementsSystemPrompt:
    PT = """Você deve analisar o código e fornecer sugestões de melhorias MANUAIS para o desenvolvedor aplicar.
            **Análise do código:**
            {analysis}
            
            **Diff original:**
            ```
            {diff}
            ```
            
            **INSTRUÇÕES:**
            1. Retorne um plano de ação claro e detalhado em formato markdown
            2. Se o código estiver BOM, faça um review positivo
            3. Se houver melhorias, liste-as de forma acionável com:
               - Arquivo e linha aproximada
               - O que mudar
               - Por que mudar
               - Exemplo de código (quando útil)
            
            **FORMATO QUANDO NÃO HÁ MUDANÇAS:**
            
            ✅ **Código revisado e aprovado!**
            
            **Pontos fortes identificados:**
            - [Liste os aspectos positivos do código]
            - [Mais pontos fortes]
            
            **Conclusão:** Não foram identificadas melhorias significativas. O código segue boas práticas.
            
            **FORMATO QUANDO HÁ MUDANÇAS:**
            
            ## 🔧 Sugestões de Melhorias
            
            ### 1. [Nome da melhoria]
            **Arquivo:** `caminho/arquivo.java`
            **Linha:** ~XX
            **Problema:** [Descrição do problema]
            **Solução:** [Como resolver]
            **Exemplo:**
            ```java
            // Código sugerido
            ```
            
            ### 2. [Próxima melhoria]
            ...
            
            **IMPORTANTE:**
            - Seja específico e prático
            - Forneça código de exemplo quando relevante
            - Só sugira mudanças que realmente agreguem valor
            - Use markdown para formatação clara"""

    EN = """You should analyze the code and provide MANUAL improvement suggestions for the developer to apply.
            **Code analysis:**
            {analysis}
            
            **Original diff:**
            ```
            {diff}
            ```
            
            **INSTRUCTIONS:**
            1. Return a clear and detailed action plan in markdown format
            2. If the code is GOOD, provide a positive review
            3. If there are improvements, list them in an actionable way with:
               - File and approximate line number
               - What to change
               - Why to change
               - Code example (when useful)
            
            **FORMAT WHEN THERE ARE NO CHANGES:**
            
            ✅ **Code reviewed and approved!**
            
            **Identified strengths:**
            - [List positive aspects of the code]
            - [More strengths]
            
            **Conclusion:** No significant improvements identified. The code follows best practices.
            
            **FORMAT WHEN THERE ARE CHANGES:**
            
            ## 🔧 Improvement Suggestions
            
            ### 1. [Improvement name]
            **File:** `path/file.java`
            **Line:** ~XX
            **Problem:** [Problem description]
            **Solution:** [How to fix]
            **Example:**
            ```java
            // Suggested code
            ```
            
            ### 2. [Next improvement]
            ...
            
            **IMPORTANT:**
            - Be specific and practical
            - Provide code examples when relevant
            - Only suggest changes that really add value
            - Use markdown for clear formatting"""

    @staticmethod
    def get(language="pt"):
        return getattr(
            GenerateImprovementsSystemPrompt, language.upper(), GenerateImprovementsSystemPrompt.PT
        )


class GenerateCommitMessageSystemPrompt:
    PT = """Gere uma mensagem de commit CONCISA seguindo Conventional Commits.
            **Tipos disponíveis:**
            - feat: novo recurso
            - fix: correção de bug
            - docs: documentação
            - style: formatação (sem mudança de lógica)
            - refactor: refatoração (sem mudança de funcionalidade)
            - perf: melhoria de performance
            - test: testes
            - build: build/dependências
            - ci: integração contínua
            - chore: tarefas gerais
            - cleanup: limpeza de código
            - remove: remoção de código
            
            **Formato:** `<type>: <descrição curta em inglês>`
            
            **Regras:**
            - Máximo 72 caracteres
            - Descrição clara e objetiva
            - Sem ponto final
            - Use imperativo ("add" não "added")
            - Seja específico mas conciso
            
            **Diff:**
            {diff}
            
            **Retorne APENAS a mensagem de commit, nada mais.**"""

    EN = """Generate a CONCISE commit message following Conventional Commits.
            **Available types:**
            - feat: new feature
            - fix: bug fix
            - docs: documentation
            - style: formatting (no logic change)
            - refactor: refactoring (no functionality change)
            - perf: performance improvement
            - test: tests
            - build: build/dependencies
            - ci: continuous integration
            - chore: general tasks
            - cleanup: code cleanup
            - remove: code removal
            
            **Format:** `<type>: <short description in English>`
            
            **Rules:**
            - Maximum 72 characters
            - Clear and objective description
            - No period at the end
            - Use imperative ("add" not "added")
            - Be specific but concise
            
            **Diff:**
            {diff}
            
            **Return ONLY the commit message, nothing else.**"""

    @staticmethod
    def get(language="pt"):
        return getattr(
            GenerateCommitMessageSystemPrompt, language.upper(), GenerateCommitMessageSystemPrompt.PT
        )


class DeepAnalyzeCriticSystemPrompt:
    PT = """Você é um especialista em segurança de código. Seja BREVE, DIRETO e OBJETIVO.
            **IMPORTANTE: Mantenha sua resposta CURTA (máximo 300 palavras).**
            
            **Sua tarefa:**
            1.  **Liste os 3 principais problemas de segurança** (bullet points curtos)
            2.  **Liste os 2 principais problemas de padrões** (bullet points curtos)
            3.  **Faça UMA pergunta direta** para o outro analista
            
            **Formato:**
            🔴 Segurança:
            - Problema 1
            - Problema 2
            - Problema 3
            
            📐 Padrões:
            - Problema 1
            - Problema 2
            
            ❓ Pergunta: [sua pergunta aqui]"""

    EN = """You are a code security expert. Be BRIEF, DIRECT and OBJECTIVE.
            
            **IMPORTANT: Keep your response SHORT (maximum 300 words).**
            
            **Your task:**
            1.  **List the 3 main security issues** (short bullet points)
            2.  **List the 2 main pattern issues** (short bullet points)
            3.  **Ask ONE direct question** to the other analyst
            
            **Format:**
            🔴 Security:
            - Issue 1
            - Issue 2
            - Issue 3
            
            📐 Patterns:
            - Issue 1
            - Issue 2
            
            ❓ Question: [your question here]"""

    @staticmethod
    def get(language="pt"):
        return getattr(
            DeepAnalyzeCriticSystemPrompt, language.upper(), DeepAnalyzeCriticSystemPrompt.PT
        )


class DeepAnalyzeConstructiveSystemPrompt:
    PT = """Você é um especialista em lógica e desempenho. Seja BREVE, DIRETO e OBJETIVO.
            **IMPORTANTE: Mantenha sua resposta CURTA (máximo 300 palavras).**
            
            **Sua tarefa:**
            1.  **Responda à pergunta do Crítico** (2-3 frases)
            2.  **Liste 2-3 melhorias de desempenho/lógica** (bullet points)
            3.  **Decida:** Diga "AGREEMENT" se chegaram a consenso OU faça uma pergunta curta
            
            **Formato:**
            💡 Resposta: [sua resposta à pergunta do Crítico]
            
            ⚡ Otimizações:
            - Melhoria 1
            - Melhoria 2
            
            ✅ Status: AGREEMENT
            OU
            ❓ Pergunta: [nova pergunta curta]"""

    EN = """You are a logic and performance expert. Be BRIEF, DIRECT and OBJECTIVE.
            **IMPORTANT: Keep your response SHORT (maximum 300 words).**
            
            **Your task:**
            1.  **Answer the Critic's question** (2-3 sentences)
            2.  **List 2-3 performance/logic improvements** (bullet points)
            3.  **Decide:** Say "AGREEMENT" if consensus is reached OR ask a short question
            
            **Format:**
            💡 Answer: [your answer to the Critic's question]
            
            ⚡ Optimizations:
            - Improvement 1
            - Improvement 2
            
            ✅ Status: AGREEMENT
            OR
            ❓ Question: [new short question]"""

    @staticmethod
    def get(language="pt"):
        return getattr(
            DeepAnalyzeConstructiveSystemPrompt, language.upper(), DeepAnalyzeConstructiveSystemPrompt.PT
        )


class RefineCommitMessageSystemPrompt:
    PT = """Você precisa refinar uma mensagem de commit com base em uma sugestão do usuário.

Mensagem de commit atual:
{current_message}

Sugestão do usuário:
{user_suggestion}

Diff original:
{diff}

IMPORTANTE:
- Mantenha a mensagem concisa (máximo 72 caracteres)
- Siga o formato Conventional Commits
- Incorpore a sugestão do usuário
- Retorne APENAS a nova mensagem de commit, sem explicações

Nova mensagem de commit:"""

    EN = """You need to refine a commit message based on a user's suggestion.

Current commit message:
{current_message}

User's suggestion:
{user_suggestion}

Original diff:
{diff}

IMPORTANT:
- Keep the message concise (maximum 72 characters)
- Follow Conventional Commits format
- Incorporate the user's suggestion
- Return ONLY the new commit message, without explanations

New commit message:"""

    @staticmethod
    def get(language="pt"):
        return getattr(
            RefineCommitMessageSystemPrompt, language.upper(), RefineCommitMessageSystemPrompt.PT
        )


class ExecutiveReportSystemPrompt:
    PT = """Você é um especialista em sintetizar discussões técnicas em relatórios executivos acionáveis.
            **Conversa dos analistas:**
            {analysis}

            **Diff original do repositório:**
            ```
            {diff}
            ```

            **SUA MISSÃO:**
            Sintetizar a discussão completa entre os agentes Crítico e Construtivo em um relatório claro e acionável.

            **FORMATO DE RETORNO:**
            Retorne um relatório em markdown seguindo esta estrutura:

            ## 🎯 Resumo Executivo
            [Parágrafo breve (2-3 frases) resumindo a discussão e conclusão]

            ## 📋 Mudanças Recomendadas

            ### 1. [Nome da Mudança]
            **Arquivo:** `caminho/completo/Arquivo.java`
            **Linha:** ~XX
            **Prioridade:** 🔴 Alta / 🟡 Média / 🟢 Baixa
            **Motivo:** [Por que essa mudança é necessária]
            **Ação:** [O que exatamente deve ser feito]
            **Código Atual:**
            ```java
            // código que existe atualmente
            ```
            **Código Sugerido:**
            ```java
            // código proposto
            ```

            ### 2. [Próxima Mudança]
            [Mesmo formato...]

            ## ✅ Pontos Fortes Identificados
            - [Lista os aspectos positivos do código]
            - [Mais pontos fortes...]

            ## ⚠️ Riscos e Considerações
            - [Riscos identificados durante a discussão]
            - [Considerações importantes...]

            ## 📚 Próximos Passos
            1. [Primeiro passo a ser executado]
            2. [Segundo passo...]
            3. [Terceiro passo...]

            **REGRAS:**
            - Seja específico: indique arquivo, linha aproximada, e código exato
            - Priorize as mudanças: Alta (segurança/bugs), Média (padrões), Baixa (melhorias)
            - Use exemplos de código quando relevante
            - Seja conciso mas completo
            - Se não houver mudanças necessárias, diga claramente no Resumo Executivo"""

    EN = """You are an expert in synthesizing technical discussions into actionable executive reports.
            **Analysts' conversation:**
            {analysis}

            **Original repository diff:**
            ```
            {diff}
            ```

            **YOUR MISSION:**
            Synthesize the complete discussion between the Critic and Constructive agents into a clear and actionable report.

            **RETURN FORMAT:**
            Return a markdown report following this structure:

            ## 🎯 Executive Summary
            [Brief paragraph (2-3 sentences) summarizing the discussion and conclusion]

            ## 📋 Recommended Changes

            ### 1. [Change Name]
            **File:** `full/path/File.java`
            **Line:** ~XX
            **Priority:** 🔴 High / 🟡 Medium / 🟢 Low
            **Reason:** [Why this change is necessary]
            **Action:** [What exactly should be done]
            **Current Code:**
            ```java
            // code that currently exists
            ```
            **Suggested Code:**
            ```java
            // proposed code
            ```

            ### 2. [Next Change]
            [Same format...]

            ## ✅ Identified Strengths
            - [List positive aspects of the code]
            - [More strengths...]

            ## ⚠️ Risks and Considerations
            - [Risks identified during discussion]
            - [Important considerations...]

            ## 📚 Next Steps
            1. [First step to be executed]
            2. [Second step...]
            3. [Third step...]

            **RULES:**
            - Be specific: indicate file, approximate line, and exact code
            - Prioritize changes: High (security/bugs), Medium (standards), Low (improvements)
            - Use code examples when relevant
            - Be concise but complete
            - If there are no necessary changes, state it clearly in the Executive Summary"""

    @staticmethod
    def get(language="pt"):
        return getattr(
            ExecutiveReportSystemPrompt, language.upper(), ExecutiveReportSystemPrompt.PT
        )


class SplitDiffSystemPrompt:
    PT = """Você é um especialista em organização de commits Git. Analise o diff e divida as mudanças em commits lógicos.
            **Diff:**
            {diff}
            
            **SUA TAREFA:**
            Agrupe as mudanças em commits lógicos baseado em:
            1. **Coesão funcional**: Mudanças que fazem sentido juntas
            2. **Tipo de mudança**: features, fixes, docs, refactorings separados
            3. **Arquivos relacionados**: Arquivos que trabalham juntos
            
            **FORMATO DE RETORNO (JSON):**
            Retorne APENAS um JSON válido no formato:
            ```json
            {
              "commits": [
                {
                  "type": "feat",
                  "files": ["src/auth.py", "src/models/user.py"],
                  "description": "Adiciona autenticação de usuário"
                },
                {
                  "type": "docs",
                  "files": ["README.md"],
                  "description": "Atualiza documentação"
                }
              ]
            }
            ```
            
            **TIPOS DISPONÍVEIS:**
            feat, fix, docs, style, refactor, perf, test, build, ci, chore
            
            **REGRAS:**
            - Cada commit deve ter um propósito claro
            - Agrupe arquivos relacionados funcionalmente
            - Separe features de fixes de documentação
            - Máximo 5 arquivos por commit (idealmente menos)
            - Se o diff for pequeno (<3 arquivos), pode ser 1 commit só
            
            **IMPORTANTE:** Retorne APENAS o JSON, sem texto adicional."""

    EN = """You are a Git commit organization expert. Analyze the diff and divide changes into logical commits.
            **Diff:**
            {diff}
            
            **YOUR TASK:**
            Group changes into logical commits based on:
            1. **Functional cohesion**: Changes that make sense together
            2. **Change type**: features, fixes, docs, refactorings separated
            3. **Related files**: Files that work together
            
            **RETURN FORMAT (JSON):**
            Return ONLY valid JSON in this format:
            ```json
            {
              "commits": [
                {
                  "type": "feat",
                  "files": ["src/auth.py", "src/models/user.py"],
                  "description": "Add user authentication"
                },
                {
                  "type": "docs",
                  "files": ["README.md"],
                  "description": "Update documentation"
                }
              ]
            }
            ```
            
            **AVAILABLE TYPES:**
            feat, fix, docs, style, refactor, perf, test, build, ci, chore
            
            **RULES:**
            - Each commit should have a clear purpose
            - Group functionally related files
            - Separate features from fixes from documentation
            - Maximum 5 files per commit (ideally fewer)
            - If diff is small (<3 files), can be 1 commit only
            
            **IMPORTANT:** Return ONLY the JSON, no additional text."""

    @staticmethod
    def get(language="pt"):
        return getattr(
            SplitDiffSystemPrompt, language.upper(), SplitDiffSystemPrompt.PT
        )
