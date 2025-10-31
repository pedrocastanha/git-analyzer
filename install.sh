set -e

GREEN='\033[38;5;22m'
GREEN1='\033[38;5;28m'
GREEN2='\033[38;5;34m'
YELLOW1='\033[38;5;190m'
YELLOW2='\033[38;5;226m'
YELLOW3='\033[38;5;220m'
BLUE1='\033[38;5;33m'
BLUE2='\033[38;5;27m'
BLUE3='\033[38;5;21m'
WHITE='\033[1;37m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo "ℹ️  $1"
}

clear
echo ""
echo ""

echo  "  ${GREEN}  ██████╗ ${GREEN1} █████╗ ${GREEN2}███████╗${YELLOW1}████████╗${YELLOW2} █████╗ ${YELLOW3}███╗   ██╗${BLUE1}██╗  ██╗${BLUE1}███████╗${BLUE2}██╗${BLUE2}██████╗ ${BLUE3} █████╗ ${NC}"
echo  "  ${GREEN} ██╔════╝ ${GREEN1}██╔══██╗${GREEN2}██╔════╝${YELLOW1}╚══██╔══╝${YELLOW2}██╔══██╗${YELLOW3}████╗  ██║${BLUE1}██║  ██║${BLUE1}██╔════╝${BLUE2}██║${BLUE2}██╔══██╗${BLUE3}██╔══██╗${NC}"
echo  "  ${GREEN} ██║      ${GREEN1}███████║${GREEN2}███████╗${YELLOW1}   ██║   ${YELLOW2}███████║${YELLOW3}██╔██╗ ██║${BLUE1}███████║${BLUE1}█████╗  ${BLUE2}██║${BLUE2}██████╔╝${BLUE3}███████║${NC}"
echo  "  ${GREEN} ██║      ${GREEN1}██╔══██║${GREEN2}╚════██║${YELLOW1}   ██║   ${YELLOW2}██╔══██║${YELLOW3}██║╚██╗██║${BLUE1}██╔══██║${BLUE1}██╔══╝  ${BLUE2}██║${BLUE2}██╔══██╗${BLUE3}██╔══██║${NC}"
echo  "  ${GREEN} ╚██████╗ ${GREEN1}██║  ██║${GREEN2}███████║${YELLOW1}   ██║   ${YELLOW2}██║  ██║${YELLOW3}██║ ╚████║${BLUE1}██║  ██║${BLUE1}███████╗${BLUE2}██║${BLUE2}██║  ██║${BLUE3}██║  ██║${NC}"
echo  "  ${GREEN}  ╚═════╝ ${GREEN1}╚═╝  ╚═╝${GREEN2}╚══════╝${YELLOW1}   ╚═╝   ${YELLOW2}╚═╝  ╚═╝${YELLOW3}╚═╝  ╚═══╝${BLUE1}╚═╝  ╚═╝${BLUE1}╚══════╝${BLUE2}╚═╝${BLUE2}╚═╝  ╚═╝${BLUE3}╚═╝  ╚═╝${NC}"


echo ""

sleep 0.3
echo "🚀 Instalando Git AI Agent ( GitCast )..."
echo "============================================================"


APP_HOME_DIR="$HOME/.local/share/git-analyzer"

print_info "Garantindo que o diretório de instalação permanente exista em '$APP_HOME_DIR'..."
mkdir -p "$APP_HOME_DIR"
print_success "Diretório de instalação pronto."

print_info "Copiando arquivos do projeto para o diretório de instalação..."
rsync -a --delete . "$APP_HOME_DIR/" --exclude ".git" --exclude ".idea" --exclude "checkpointer.sqlite"
print_success "Arquivos do projeto copiados."

print_info "Mudando para o diretório de instalação para continuar..."
cd "$APP_HOME_DIR"
echo ""

PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    if python -c 'import sys; sys.exit(0 if sys.version_info.major == 3 else 1)' &> /dev/null; then
        PYTHON_CMD="python"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    print_error "Python 3 não encontrado!"
    print_info "Instale Python 3. O nome do executável deve ser 'python3' ou 'python' e estar no seu PATH."
    exit 1
fi

print_success "Python 3 encontrado: $($PYTHON_CMD --version)"

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    print_info "Criando ambiente virtual em '$VENV_DIR'..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    print_success "Ambiente virtual criado."
fi

print_info "Ativando ambiente virtual..."
. "$VENV_DIR/bin/activate"
print_success "Ambiente virtual ativado."

print_info "Atualizando pip..."
pip install --upgrade pip
print_success "Pip atualizado."

echo ""

print_info "Instalando Git AI Agent e suas dependências no ambiente virtual..."
print_warning "Isso pode levar alguns minutos..."
pip install --upgrade --force-reinstall .

print_success "Git AI Agent instalado com sucesso no ambiente virtual!"

echo ""

print_info "Criando link simbólico para acesso global ao comando 'gitcast'..."

EXECUTABLE_PATH="$APP_HOME_DIR/.venv/bin/gitcast"
LOCAL_BIN="$HOME/.local/bin"
SYMLINK_PATH="$LOCAL_BIN/gitcast"

mkdir -p "$LOCAL_BIN"

rm -f "$SYMLINK_PATH"

ln -s "$EXECUTABLE_PATH" "$SYMLINK_PATH"
print_success "Link simbólico criado em $SYMLINK_PATH"

if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo ""
    print_warning "O diretório ~/.local/bin não está no seu PATH."
    echo ""
    echo "Adicione a seguinte linha ao seu arquivo de configuração do shell:"
    echo ""

    if [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
        echo "    echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc"
        echo "    source ~/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"
        echo "    echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
        echo "    source ~/.bashrc"
    else
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
    echo ""
    print_info "Ou feche e abra o terminal novamente."
else
    print_success "~/.local/bin já está no PATH!"
fi

echo ""
echo "============================================================"
print_success "🎉 Instalação concluída com sucesso!"
echo "============================================================"
echo ""
echo "📍 Próximos passos:"
echo ""
echo "   1️⃣  Execute o comando:"
echo "      ${GREEN}gitcast${NC}"
echo ""
echo "   2️⃣  Na primeira execução, você será guiado para:"
echo "      • Escolher seu provider de IA (OpenAI ou Gemini)"
echo "      • Configurar sua API key"
echo ""
echo "   3️⃣  Comandos disponíveis:"
echo "      • ${GREEN}analyze${NC}   - Análise simples de código"
echo "      • ${GREEN}danalyze${NC}  - Análise profunda (multi-agent)"
echo "      • ${GREEN}up${NC}        - Commit e push inteligente"
echo "      • ${GREEN}config${NC}    - Alterar configurações"
echo "      • ${GREEN}exit${NC}      - Sair"
echo ""
echo "============================================================"
echo "💡 Dica: Execute em qualquer repositório Git!"
echo "============================================================"
