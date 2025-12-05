# gitcast

Ferramenta CLI que usa LLMs pra analisar diffs do git, sugerir correções e gerar commits.

## O que faz

- **analyze** - Olha o diff e sugere melhorias (formatado em markdown)
- **danalyze** - Dois agentes discutem seu código (um critica, outro defende) e geram um plano
- **up** - Gera mensagem de commit e faz push
- **split-up** - Divide diffs grandes em commits menores
- **file watcher** - Monitora mudanças no repo e analisa automaticamente
- **notificações** - Avisa quando termina análise (Linux/macOS/Windows)

Funciona com OpenAI e Gemini.

## Instalação

```bash
git clone https://github.com/pedrocastanha/git-analyzer.git
cd git-analyzer
./install.sh
```

Se der problema de PATH:

```bash
# bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc

# zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

## Como usar

Entra no repo e roda:

```bash
gitcast
```

Na primeira vez vai pedir pra configurar provider e API key.

### Comandos

| Comando | O que faz |
|---------|-----------|
| `analyze` | Análise simples das mudanças |
| `danalyze` | Análise com dois agentes discutindo |
| `up` | Commit + push |
| `split-up` | Divide diff grande em vários commits |
| `config` | Muda configurações |
| `mermaid` | Mostra o grafo do workflow |
| `exit` | Sai |
| `suggestions` | Mostra última sugestão da IA |

Dica: digita `/` pra abrir menu com autocomplete. Setas pra navegar, Tab/Enter pra selecionar.

### Exemplo básico

```bash
# faz suas mudanças
git add .

gitcast
> analyze   # vê sugestões
> up        # commita e pusha
```

### Deep analysis

```bash
gitcast
> danalyze
```

Dois agentes vão discutir:
- Um foca em segurança e padrões
- Outro em lógica e performance

Eles vão trocando mensagens até concordarem ou bater o limite. Depois gera um plano consolidado.

### File watcher

O gitcast monitora o repositório automaticamente. Quando você salva um arquivo, ele roda uma análise em background e manda uma notificação quando termina.

Pra ver o resultado: digita `suggestions`.

## API Keys

**OpenAI**: https://platform.openai.com/api-keys

**Gemini**: https://aistudio.google.com/app/apikey

## Configuração

Fica em `~/.config/gitcast/config.json`:

```json
{
  "ai_provider": "gemini",
  "auto_stage": true,
  "auto_push": true,
  "diff_max_size": 15000,
  "language": "pt",
  "gemini_model": "gemini-2.5-flash",
  "openai_model": "gpt-4o-mini"
}
```

Ou muda pelo CLI:

```bash
gitcast
> config
```

## Estrutura

```
src/
├── core/           # workflow langgraph
│   ├── graph.py    # definição do grafo
│   ├── nodes.py    # implementação dos nodes
│   ├── router.py   # roteamento
│   └── state.py    # estado
├── providers/      # integrações com LLMs
│   ├── agents.py
│   ├── chains.py
│   ├── llms.py
│   └── prompts.py
├── config.py
└── messages.py     # prompts de sistema

main.py             # entry point
```

## Dependências

- Python 3.9+
- langgraph
- langchain
- gitpython

---

Usa LangGraph pra orquestrar os agentes.
