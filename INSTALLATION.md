# Guia de Instalação do Git AI Agent

Este tutorial irá guiá-lo na instalação e configuração do Git AI Agent em sua máquina. O agente é uma ferramenta de linha de comando que usa IA para ajudar você com análise de código e commits.

## Pré-requisitos

Antes de começar, certifique-se de que você tem instalado em seu sistema:

1.  **Git**: Para clonar o repositório do agente e para o próprio funcionamento do agente.
    *   `sudo apt install git` (Ubuntu/Debian)
    *   `brew install git` (macOS)
    *   [Download para Windows](https://git-scm.com/download/win)

2.  **Python 3.9+**: O agente é escrito em Python.
    *   `sudo apt install python3 python3-pip` (Ubuntu/Debian)
    *   `brew install python@3.9` (macOS - verifique sua versão de Python)
    *   [Download para Windows](https://www.python.org/downloads/)

3.  **pip**: O gerenciador de pacotes do Python. Geralmente vem com o Python 3. Se não tiver, o script de instalação tentará instalá-lo.

## Instalação Passo a Passo

Siga estes passos para instalar o Git AI Agent:

### 1. Clonar o Repositório

Primeiro, você precisa clonar o repositório do Git AI Agent para sua máquina. Abra seu terminal e execute:

```bash
git clone https://github.com/[seu-usuario]/[seu-repositorio].git
cd [seu-repositorio]
```

**Observação**: Substitua `https://github.com/[seu-usuario]/[seu-repositorio].git` pelo link real do seu repositório Git do agente.

### 2. Executar o Script de Instalação

Com o repositório clonado e dentro do diretório do projeto, execute o script de instalação. Este script irá verificar os pré-requisitos, instalar as dependências Python necessárias e configurar o agente para uso.

```bash
./install.sh
```

Durante a execução, o script pode pedir sua senha de `sudo` se precisar instalar o `pip` (em sistemas Debian/Ubuntu). Ele também informará sobre o progresso e o resultado da instalação.

### 3. Verificar a Instalação

Após a instalação, o comando `castanhafodao` deve estar disponível no seu terminal. Para verificar, tente executar:

```bash
castanhafodao --version
```
Ou simplesmente:
```bash
castanhafodao
```

Se você vir uma mensagem de boas-vindas ou um menu, a instalação foi bem-sucedida.

## Configurações Essenciais

O agente precisa de uma chave de API para o provedor de IA que você deseja usar (ex: OpenAI, Google Gemini, Anthropic). Sem essa chave, o agente não conseguirá se comunicar com os modelos de IA.

### Configurar Chave de API

1.  Execute o agente:
    ```bash
    castanhafodao
    ```
2.  No menu principal, digite `config` e pressione Enter.
3.  No menu de configuração, selecione `1. Escolher provider de IA` e escolha seu provedor preferido (ex: `4` para Gemini).
4.  Volte ao menu de configuração e selecione `2. Configurar API keys`. Insira sua chave de API quando solicitado.
5.  O agente salvará a configuração em um arquivo `.castanhafodao.json` na raiz do seu repositório.

**Alternativa (variável de ambiente):** Você pode definir sua chave de API como uma variável de ambiente no seu sistema. Por exemplo, para Gemini:

```bash
export GEMINI_API_KEY="SUA_CHAVE_AQUI"
```
(Substitua `GEMINI_API_KEY` e `SUA_CHAVE_AQUI` pelo seu provedor e chave reais). Adicione esta linha ao seu `~/.bashrc` ou `~/.zshrc` para que a chave seja carregada automaticamente em cada nova sessão de terminal.

## Como Usar o Agente

Com o agente instalado e configurado, você pode usá-lo dentro de qualquer repositório Git de sua preferência.

1.  **Navegue para o seu repositório Git:**
    ```bash
    cd /caminho/para/seu/repositorio-git
    ```

2.  **Execute o agente e use os comandos:**
    ```bash
    castanhafodao
    ```
    Você verá um menu com os comandos disponíveis:

    *   `analyze`: Analisa mudanças no seu código e sugere melhorias.
    *   `up`: Gera uma mensagem de commit inteligente e faz o commit e push.
    *   `config`: Abre o menu de configurações.
    *   `exit`: Sai do agente.

--- 

Para opções de personalização avançadas, consulte o arquivo `CUSTOMIZATION.md` na raiz do repositório. Aproveite seu Git AI Agent!
