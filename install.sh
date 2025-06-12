#!/bin/bash
# Script de instalação para Business Analytics Pro
# Uso: ./install.sh [opções]
#   Opções:
#     --help          Exibe esta mensagem de ajuda
#     --dev           Instala em modo de desenvolvimento
#     --docker        Instala usando Docker
#     --update        Atualiza uma instalação existente
#     --silent        Instalação silenciosa (sem perguntas)

set -e

# Configurações padrão
INSTALL_DIR="$(pwd)/business-analytics-pro"
ENV_FILE=".env"
MODE="prod"
USE_DOCKER=false
IS_UPDATE=false
SILENT=false
VERSION="2.0.0"

# Cores para terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sem Cor

# Função para exibir mensagens
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# Função para exibir ajuda
show_help() {
    echo "Business Analytics Pro - Script de Instalação"
    echo "Uso: ./install.sh [opções]"
    echo "  Opções:"
    echo "    --help          Exibe esta mensagem de ajuda"
    echo "    --dev           Instala em modo de desenvolvimento"
    echo "    --docker        Instala usando Docker"
    echo "    --update        Atualiza uma instalação existente"
    echo "    --silent        Instalação silenciosa (sem perguntas)"
    exit 0
}

# Processar argumentos
for arg in "$@"; do
    case $arg in
        --help)
            show_help
            ;;
        --dev)
            MODE="dev"
            ;;
        --docker)
            USE_DOCKER=true
            ;;
        --update)
            IS_UPDATE=true
            ;;
        --silent)
            SILENT=true
            ;;
    esac
done

# Verificar requisitos de sistema
check_requirements() {
    log "Verificando requisitos de sistema..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 não encontrado. Por favor, instale o Python 3.9+ e tente novamente."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
        log_error "Python 3.9+ é requerido. Versão encontrada: $PYTHON_VERSION"
        exit 1
    fi
    
    log_success "Python $PYTHON_VERSION encontrado."
    
    # Verificar pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 não encontrado. Por favor, instale o pip e tente novamente."
        exit 1
    fi
    
    log_success "pip3 encontrado."
    
    # Verificar Docker se necessário
    if [ "$USE_DOCKER" = true ]; then
        if ! command -v docker &> /dev/null; then
            log_error "Docker não encontrado. Por favor, instale o Docker e tente novamente."
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            log_error "docker-compose não encontrado. Por favor, instale o docker-compose e tente novamente."
            exit 1
        fi
        
        log_success "Docker e docker-compose encontrados."
    fi
    
    log_success "Todos os requisitos atendidos."
}

# Configurar ambiente
setup_environment() {
    log "Configurando ambiente..."
    
    # Criar diretório de instalação
    if [ "$IS_UPDATE" = false ]; then
        if [ -d "$INSTALL_DIR" ] && [ "$(ls -A $INSTALL_DIR)" ]; then
            if [ "$SILENT" = false ]; then
                read -p "Diretório $INSTALL_DIR já existe e não está vazio. Continuar? (s/N) " CONTINUE
                if [[ ! $CONTINUE =~ ^[Ss]$ ]]; then
                    log "Instalação cancelada pelo usuário."
                    exit 0
                fi
            fi
        else
            mkdir -p "$INSTALL_DIR"
        fi
    fi
    
    cd "$INSTALL_DIR"
    
    # Criar ambiente virtual
    if [ "$USE_DOCKER" = false ]; then
        log "Criando ambiente virtual..."
        if [ ! -d ".venv" ]; then
            python3 -m venv .venv
        fi
        
        # Ativar ambiente virtual
        source .venv/bin/activate
    fi
    
    # Criar arquivo .env se não existir
    if [ ! -f "$ENV_FILE" ]; then
        if [ "$SILENT" = false ]; then
            log "Configurando variáveis de ambiente..."
            read -p "Informe a chave da API OpenAI: " OPENAI_KEY
            
            # Para autenticação
            read -p "Defina o nome de usuário admin: " ADMIN_USER
            read -sp "Defina a senha admin: " ADMIN_PASS
            echo
            
            # Outras configurações
            read -p "Porta para o servidor (padrão: 8501): " SERVER_PORT
            SERVER_PORT=${SERVER_PORT:-8501}
            
            # Gravar no arquivo .env
            cat > "$ENV_FILE" << EOF
OPENAI_API_KEY=${OPENAI_KEY}
APP_USERNAME=${ADMIN_USER}
APP_PASSWORD=${ADMIN_PASS}
SERVER_PORT=${SERVER_PORT}
APP_ENVIRONMENT=${MODE}
EOF
        else
            # Criar .env com valores padrão (modo silencioso)
            cat > "$ENV_FILE" << EOF
OPENAI_API_KEY=seu_api_key_aqui
APP_USERNAME=admin
APP_PASSWORD=admin
SERVER_PORT=8501
APP_ENVIRONMENT=${MODE}
EOF
            log_warning "Arquivo .env criado com valores padrão. Por favor, edite-o após a instalação."
        fi
    fi
    
    # Criar estrutura de diretórios
    mkdir -p data/tenants
    mkdir -p logs
    mkdir -p cache
    mkdir -p config
    mkdir -p secrets
    
    log_success "Ambiente configurado com sucesso."
}

# Instalar dependências
install_dependencies() {
    log "Instalando dependências..."
    
    if [ "$USE_DOCKER" = false ]; then
        if [ "$MODE" = "dev" ]; then
            pip install -r requirements/dev.txt
        else
            pip install -r requirements/prod.txt
        fi
    else
        # No Docker, as dependências são instaladas no build
        log "As dependências serão instaladas durante o build do Docker."
    fi
    
    log_success "Dependências instaladas com sucesso."
}

# Configurar Docker se necessário
setup_docker() {
    if [ "$USE_DOCKER" = true ]; then
        log "Configurando Docker..."
        
        # Criar arquivo docker-compose.yml
        cat > "docker-compose.yml" << EOF
version: '3'

services:
  app:
    build: .
    ports:
      - "\${SERVER_PORT:-8501}:8501"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
      - ./.env:/app/.env
    environment:
      - APP_ENVIRONMENT=${MODE}
    restart: unless-stopped

EOF

        # Criar Dockerfile
        cat > "Dockerfile" << EOF
FROM python:3.11-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements/prod.txt

EXPOSE 8501

CMD ["streamlit", "run", "langchain_project/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF

        log_success "Docker configurado com sucesso."
    fi
}

# Realizar atualização se solicitado
perform_update() {
    if [ "$IS_UPDATE" = true ]; then
        log "Atualizando para a versão ${VERSION}..."
        
        # Fazer backup dos dados
        BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        if [ -d "data" ]; then
            cp -r data "$BACKUP_DIR/"
        fi
        
        if [ -f "$ENV_FILE" ]; then
            cp "$ENV_FILE" "$BACKUP_DIR/"
        fi
        
        if [ -d "config" ]; then
            cp -r config "$BACKUP_DIR/"
        fi
        
        log_success "Backup criado em $BACKUP_DIR"
        
        # Atualizar código
        # Em uma versão real, baixariamos a nova versão de um repositório aqui
        # Para este exemplo, assumimos que o código já está atualizado
        
        # Atualizar dependências
        install_dependencies
        
        # Executar migrações se necessário
        # ...
        
        log_success "Atualização concluída com sucesso."
    fi
}

# Iniciar a aplicação
start_application() {
    if [ "$SILENT" = false ]; then
        read -p "Deseja iniciar a aplicação agora? (S/n) " START_NOW
        if [[ ! $START_NOW =~ ^[Nn]$ ]]; then
            if [ "$USE_DOCKER" = true ]; then
                log "Iniciando aplicação com Docker..."
                docker-compose up -d
                log_success "Aplicação iniciada em http://localhost:${SERVER_PORT:-8501}"
            else
                log "Iniciando aplicação..."
                # Ativar ambiente virtual se não estiver ativado
                if [[ "$VIRTUAL_ENV" == "" ]]; then
                    source .venv/bin/activate
                fi
                
                # Iniciar em background
                nohup streamlit run langchain_project/main.py --server.port=${SERVER_PORT:-8501} > logs/app.log 2>&1 &
                log_success "Aplicação iniciada em http://localhost:${SERVER_PORT:-8501}"
            fi
        else
            show_startup_instructions
        fi
    else
        show_startup_instructions
    fi
}

# Exibir instruções de inicialização
show_startup_instructions() {
    echo 
    echo "====================== INSTRUÇÕES DE INICIALIZAÇÃO ======================"
    if [ "$USE_DOCKER" = true ]; then
        echo "Para iniciar a aplicação, execute:"
        echo "  cd $INSTALL_DIR"
        echo "  docker-compose up -d"
    else
        echo "Para iniciar a aplicação, execute:"
        echo "  cd $INSTALL_DIR"
        echo "  source .venv/bin/activate"
        echo "  streamlit run langchain_project/main.py"
    fi
    echo
    echo "Acesse a aplicação em: http://localhost:${SERVER_PORT:-8501}"
    echo "====================================================================="
}

# Função principal
main() {
    echo "==============================================="
    echo "  Business Analytics Pro - Instalador v${VERSION}  "
    echo "==============================================="
    echo
    
    check_requirements
    setup_environment
    install_dependencies
    setup_docker
    perform_update
    start_application
    
    echo
    log_success "Instalação concluída com sucesso!"
}

# Executar função principal
main
