# 🤖 gitcast - AI Git Assistant

Um assistente Git inteligente que usa IA para analisar código, sugerir melhorias e gerar commits automáticos.

## ✨ Features

- 🔍 **Análise simples** - Sugestões de melhorias manuais formatadas em markdown
- 🧠 **Análise profunda** - Multi-agent discussion com relatório executivo colorido
- 📝 **Commits inteligentes** - Mensagens concisas seguindo conventional commits
- 🎨 **Interface colorida** - Código atual (vermelho) vs sugerido (verde)
- 🤝 **Multi-provider** - Suporta OpenAI (GPT-4) e Google (Gemini)

## 🚀 Instalação

### Método 1: Clone manual (recomendado se curl não funcionar)

```bash
git clone https://github.com/pedrocastanha/git-analyzer.git
cd git-analyzer
./install.sh
```

### Pós-instalação

Se `~/.local/bin` não estiver no seu PATH, adicione ao seu shell:

**Bash:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Zsh:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## 🎯 Uso

### Primeira execução

Na primeira vez, você será guiado por um setup interativo:

```bash
gitcast
```

Você precisará:
1. Escolher seu provider (OpenAI ou Gemini)
2. Configurar sua API key

### Comandos disponíveis

Entre em qualquer repositório Git e execute:

```bash
gitcast
```

Comandos dentro do CLI:

- **`analyze`** - Análise simples de mudanças
- **`danalyze`** - Análise profunda com múltiplos agentes (critic + constructive)
- **`up`** - Gera commit message e faz push inteligente
- **`config`** - Altera configurações (provider, API keys, etc)
- **`mermaid`** - Visualiza o workflow em formato Mermaid
- **`exit`** - Sair

### Exemplos

**Análise simples:**
```bash
# Faça mudanças no código
git add .

# Execute
gitcast
> analyze
```

**Análise profunda (recomendado para mudanças complexas):**
```bash
gitcast
> danalyze
# Dois agentes discutem o código:
# 🔴 Crítico (segurança + padrões)
# 🟢 Construtivo (lógica + performance)
```

**Commit automático:**
```bash
# Faça mudanças
git add .

gitcast
> up
# Gera mensagem seguindo conventional commits
# Faz commit e push automaticamente
```

## 🔑 Onde conseguir API Keys

### OpenAI
1. Crie uma conta em https://platform.openai.com/
2. Vá em https://platform.openai.com/api-keys
3. Crie uma nova API key

### Gemini (Google)
1. Acesse https://aistudio.google.com/app/apikey
2. Clique em "Create API Key"

## ⚙️ Configuração

As configurações ficam em `~/.config/gitcast/config.json`.

### Alterar provider

```bash
gitcast
> config
> 1  # Escolher provider
```

### Alterar API key

```bash
gitcast
> config
> 2  # Configurar API keys
```

### Configurações disponíveis

```json
{
  "ai_provider": "gemini",           // "openai" ou "gemini"
  "auto_stage": true,                // Auto-stage arquivos antes do commit
  "auto_push": true,                 // Auto-push após commit
  "diff_max_size": 15000,            // Tamanho máximo do diff (chars)
  "language": "pt",                  // Idioma dos commits: "pt" ou "en"
  "gemini_model": "gemini-2.5-flash",
  "openai_model": "gpt-4o-mini"
}
```

## 🏗️ Arquitetura

O projeto usa **LangGraph** para orquestração de agentes:

- **Nodes**: Etapas do workflow (análise, geração de patch, commit)
- **Edges**: Lógica de roteamento entre nodes
- **State**: Estado compartilhado entre nodes

### Deep Analysis (danalyze)

Utiliza dois agentes especializados que discutem o código:

1. **🔴 Crítico** - Foca em segurança e padrões
2. **🟢 Construtivo** - Foca em lógica e performance

Eles alternam mensagens até:
- Chegarem a um acordo (AGREEMENT)
- Atingirem 8 mensagens (limite)

Depois, um terceiro agente sintetiza a discussão em um plano de ação + patch.

## 🛠️ Desenvolvimento

### Estrutura do projeto

```
git-analyzer/
├── src/
│   ├── core/           # LangGraph workflow
│   │   ├── graph.py    # Definição do grafo
│   │   ├── nodes.py    # Implementação dos nodes
│   │   ├── router.py   # Lógica de roteamento
│   │   └── state.py    # Schema do estado
│   ├── providers/      # Integração com LLMs
│   │   ├── agents.py   # Factory de agents
│   │   ├── chains.py   # LangChain chains
│   │   ├── llms.py     # Configuração de LLMs
│   │   └── prompts.py  # Templates de prompts
│   ├── config.py       # Gerenciamento de config
│   └── messages.py     # System prompts
├── main.py             # Entry point CLI
├── install.sh          # Script de instalação
└── pyproject.toml      # Dependências
```

### Dependências

- Python 3.9+
- LangGraph
- LangChain
- GitPython
- OpenAI SDK / Google GenAI SDK


## 🤝 Contribuindo

Contributions são bem-vindas! Abra issues ou pull requests.

## 💡 Dicas

- Use `danalyze` para mudanças complexas ou críticas
- Use `analyze` para mudanças simples do dia-a-dia
- Configure `auto_push: false` se preferir revisar antes de push
- O diff é truncado em 15000 chars por padrão (ajustável)


---

Feito com ❤️ usando LangGraph
