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

echo -e "  ${GREEN}  ██████╗ ${GREEN1} █████╗ ${GREEN2}███████╗${YELLOW1}████████╗${YELLOW2} █████╗ ${YELLOW3}███╗   ██╗${BLUE1}██╗  ██╗${BLUE1}███████╗${BLUE2}██╗${BLUE2}██████╗ ${BLUE3} █████╗ ${NC}"
echo -e "  ${GREEN} ██╔════╝ ${GREEN1}██╔══██╗${GREEN2}██╔════╝${YELLOW1}╚══██╔══╝${YELLOW2}██╔══██╗${YELLOW3}████╗  ██║${BLUE1}██║  ██║${BLUE1}██╔════╝${BLUE2}██║${BLUE2}██╔══██╗${BLUE3}██╔══██╗${NC}"
echo -e "  ${GREEN} ██║      ${GREEN1}███████║${GREEN2}███████╗${YELLOW1}   ██║   ${YELLOW2}███████║${YELLOW3}██╔██╗ ██║${BLUE1}███████║${BLUE1}█████╗  ${BLUE2}██║${BLUE2}██████╔╝${BLUE3}███████║${NC}"
echo -e "  ${GREEN} ██║      ${GREEN1}██╔══██║${GREEN2}╚════██║${YELLOW1}   ██║   ${YELLOW2}██╔══██║${YELLOW3}██║╚██╗██║${BLUE1}██╔══██║${BLUE1}██╔══╝  ${BLUE2}██║${BLUE2}██╔══██╗${BLUE3}██╔══██║${NC}"
echo -e "  ${GREEN} ╚██████╗ ${GREEN1}██║  ██║${GREEN2}███████║${YELLOW1}   ██║   ${YELLOW2}██║  ██║${YELLOW3}██║ ╚████║${BLUE1}██║  ██║${BLUE1}███████╗${BLUE2}██║${BLUE2}██║  ██║${BLUE3}██║  ██║${NC}"
echo -e "  ${GREEN}  ╚═════╝ ${GREEN1}╚═╝  ╚═╝${GREEN2}╚══════╝${YELLOW1}   ╚═╝   ${YELLOW2}╚═╝  ╚═╝${YELLOW3}╚═╝  ╚═══╝${BLUE1}╚═╝  ╚═╝${BLUE1}╚══════╝${BLUE2}╚═╝${BLUE2}╚═╝  ╚═╝${BLUE3}╚═╝  ╚═╝${NC}"

#echo -e "  ${GREEN}  ██████╗${GREEN_LIGHT} █████╗${YELLOW} ███████╗${YELLOW_BRIGHT}████████╗${BLUE} █████╗${BLUE_LIGHT} ███╗   ██╗${WHITE}██╗  ██╗${WHITE} █████╗ ${NC}"
#echo -e "  ${GREEN} ██╔════╝${GREEN_LIGHT}██╔══██╗${YELLOW}██╔════╝${YELLOW_BRIGHT}╚══██╔══╝${BLUE}██╔══██╗${BLUE_LIGHT}████╗  ██║${WHITE}██║  ██║${WHITE}██╔══██╗${NC}"
#echo -e "  ${GREEN} ██║     ${GREEN_LIGHT}███████║${YELLOW}███████╗${YELLOW_BRIGHT}   ██║   ${BLUE}███████║${BLUE_LIGHT}██╔██╗ ██║${WHITE}███████║${WHITE}███████║${NC}"
#echo -e "  ${GREEN} ██║     ${GREEN_LIGHT}██╔══██║${YELLOW}╚════██║${YELLOW_BRIGHT}   ██║   ${BLUE}██╔══██║${BLUE_LIGHT}██║╚██╗██║${WHITE}██╔══██║${WHITE}██╔══██║${NC}"
#echo -e "  ${GREEN} ╚██████╗${GREEN_LIGHT}██║  ██║${YELLOW}███████║${YELLOW_BRIGHT}   ██║   ${BLUE}██║  ██║${BLUE_LIGHT}██║ ╚████║${WHITE}██║  ██║${WHITE}██║  ██║${NC}"
#echo -e "  ${GREEN}  ╚═════╝${GREEN_LIGHT}╚═╝  ╚═╝${YELLOW}╚══════╝${YELLOW_BRIGHT}   ╚═╝   ${BLUE}╚═╝  ╚═╝${BLUE_LIGHT}╚═╝  ╚═══╝${WHITE}╚═╝  ╚═╝${WHITE}╚═╝  ╚═╝${NC}"


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

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 não encontrado!"
    print_info "Instale Python 3: sudo apt install python3 python3-pip"
    exit 1
fi

print_success "Python 3 encontrado: $(python3 --version)"

if ! command -v pip3 &> /dev/null; then
    print_warning "pip3 não encontrado. Instalando..."
    sudo apt update && sudo apt install -y python3-pip
fi

print_success "pip3 encontrado"

echo ""
print_info "Instalando Git AI Agent e suas dependências..."
pip3 install --user -e .

print_success "Git AI Agent instalado em modo editável!"

echo ""
if [ -f ".gitignore" ]; then
    if ! grep -q ".castanha123.json" .gitignore; then
        echo ".castanha123.json" >> .gitignore
        print_success "Adicionado .castanha123.json ao .gitignore"
    fi
else
    echo ".castanha123.json" > .gitignore
    print_success "Criado .gitignore com .castanha123.json"
fi

echo ""
echo "============================================================"
print_success "Instalação concluída!"
echo "============================================================"
echo ""
echo "📝 Próximos passos:"
echo "   1. Configure sua API key:"
echo "      (Use o comando 'castanha123 config' para configurar)"
echo ""
echo "   2. Execute o agente:"
echo "      castanha123"
echo ""
echo "   3. Use os comandos:"
echo "      - analyze: Analisa mudanças"
echo "      - up: Commit e push inteligente"
echo "      - config: Configurações"
echo ""
echo "🎉 Aproveite seu Git AI Agent!"
echo "============================================================"
