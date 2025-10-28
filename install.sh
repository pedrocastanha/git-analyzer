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

if [ ! -d ".git" ]; then
    print_error "Este diretório não é um repositório Git!"
    print_info "Execute 'git init' primeiro ou clone um repositório."
    exit 1
fi

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
print_info "Instalando Git AI Agent e suas dependências..."
pip install -e .

print_success "Git AI Agent instalado em modo editável no ambiente virtual!"

echo ""
if [ -f ".gitignore" ]; then
    if ! grep -q ".castanhafodao.json" .gitignore; then
        echo ".castanhafodao.json" >> .gitignore
        print_success "Adicionado .castanhafodao.json ao .gitignore"
    fi
    if ! grep -q "user_config.json" .gitignore; then
        echo "user_config.json" >> .gitignore
        print_success "Adicionado user_config.json ao .gitignore"
    fi
else
    echo ".castanhafodao.json" > .gitignore
    echo "user_config.json" >> .gitignore
    print_success "Criado .gitignore com .castanhafodao.json e user_config.json"
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
