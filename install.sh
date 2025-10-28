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
echo "🚀 Instalando Git AI Agent (Castanha Fodão)..."
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

# A verificação de repositório Git foi removida daqui.
# O instalador não precisa mais rodar de dentro de um repositório.
# A ferramenta em si, quando executada, fará as checagens necessárias.

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
pip install .

print_success "Git AI Agent instalado com sucesso no ambiente virtual!"

echo ""

print_info "Criando link simbólico para acesso global ao comando 'castanhafodao'..."

EXECUTABLE_PATH="$APP_HOME_DIR/.venv/bin/castanhafodao"
SYMLINK_PATH="/usr/local/bin/castanhafodao"

if [ -L "$SYMLINK_PATH" ] && [ "$(readlink "$SYMLINK_PATH")" = "$EXECUTABLE_PATH" ]; then
    print_success "Link simbólico global já existe e está correto."
else
    print_info "Será necessário privilégio de administrador (sudo) para criar o link em /usr/local/bin."
    if sudo ln -sf "$EXECUTABLE_PATH" "$SYMLINK_PATH"; then
        print_success "Link simbólico criado com sucesso!"
    else
        print_error "Falha ao criar o link simbólico. A instalação pode não estar acessível globalmente."
        exit 1
    fi
fi

echo ""
echo "============================================================"
print_success "Instalação concluída!"
echo "============================================================"
echo ""
echo "📝 Próximos passos:"
echo "   1. Configure sua API key:"
echo "      (Use o comando 'castanhafodao config' para configurar)"
echo ""
echo "   2. Execute o agente:"
echo "      castanhafodao"
echo ""
echo "   3. Use os comandos:"
echo "      - analyze: Analisa mudanças"
echo "      - up: Commit e push inteligente"
echo "      - config: Configurações"
echo ""
echo "🎉 Aproveite seu Git AI Agent!"
echo "============================================================"
